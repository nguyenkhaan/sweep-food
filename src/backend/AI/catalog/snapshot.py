"""In-memory catalog snapshot, bundle loader, and process-wide cache.

Provides immutable snapshots of the recipe catalog, recipe ingredients,
and master ingredients for recommendation candidate retrieval and ranking.
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from AI.catalog.errors import CatalogNotLoadedError
from AI.catalog.master_index import build_master_alias_index

logger = logging.getLogger(__name__)
DEFAULT_BUNDLE_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class CatalogSnapshot:
    """Immutable snapshot of the catalog for in-process inference."""

    recipes: list[dict[str, Any]]
    recipes_by_id: dict[str, dict[str, Any]]
    ingredients: list[dict[str, Any]]
    ingredients_by_recipe: dict[str, list[dict[str, Any]]]
    master_rows: list[dict[str, Any]]
    master_by_code: dict[str, dict[str, Any]]
    master_alias_index: dict[str, tuple[str, ...]]
    revision: str


def _clean_str(val: object) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


def _load_json_or_csv(json_path: Path, csv_path: Path) -> list[dict[str, Any]]:
    """Load records prioritizing JSON if present, falling back to CSV."""
    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, list):
                return data
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            return [dict(row) for row in reader]
    raise FileNotFoundError(f"Neither {json_path} nor {csv_path} was found.")


def load_snapshot_from_bundle(
    bundle_dir: str | Path | None = None,
) -> CatalogSnapshot:
    """Load an immutable CatalogSnapshot from bundled files in AI/data."""
    root = Path(bundle_dir) if bundle_dir is not None else DEFAULT_BUNDLE_DIR

    recipes_json = root / "catalog" / "recipes.json"
    recipes_csv = root / "catalog" / "recipes.csv"
    recipes = _load_json_or_csv(recipes_json, recipes_csv)

    ings_json = root / "catalog" / "recipe_ingredients.json"
    ings_csv = root / "catalog" / "recipe_ingredients.csv"
    ingredients = _load_json_or_csv(ings_json, ings_csv)

    master_json = root / "master_ingredients" / "master_ingredients_nutrition.json"
    master_csv = root / "master_ingredients" / "master_ingredients_nutrition.csv"
    master_rows = _load_json_or_csv(master_json, master_csv)

    recipes_by_id: dict[str, dict[str, Any]] = {}
    for r in recipes:
        r_id = _clean_str(r.get("id"))
        if r_id:
            recipes_by_id[r_id] = r

    ingredients_by_recipe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ing in ingredients:
        r_id = _clean_str(ing.get("recipe_id"))
        if r_id:
            ingredients_by_recipe[r_id].append(ing)

    master_by_code: dict[str, dict[str, Any]] = {}
    for m in master_rows:
        code = _clean_str(m.get("code"))
        if code:
            master_by_code[code] = m

    master_alias_index = build_master_alias_index(master_rows)

    manifest_path = root / "catalog" / "catalog_manifest.json"
    if manifest_path.exists():
        try:
            with manifest_path.open("r", encoding="utf-8") as fh:
                manifest = json.load(fh)
            rev = manifest.get("revision", 1259)
            notes_rev = manifest.get("notes_revision", 31)
            fingerprint = manifest.get("corpus_fingerprint", "")[:12]
            revision = f"catalog-r{rev}-n{notes_rev}-{fingerprint}"
        except (json.JSONDecodeError, OSError, TypeError, KeyError):
            revision = f"catalog-bundle-{len(recipes)}-{len(ingredients)}"
    else:
        hash_data = f"{len(recipes)}:{len(ingredients)}:{len(master_rows)}"
        rev_hash = hashlib.sha256(hash_data.encode("utf-8")).hexdigest()[:12]
        revision = f"catalog-bundle-{rev_hash}"

    return CatalogSnapshot(
        recipes=recipes,
        recipes_by_id=recipes_by_id,
        ingredients=ingredients,
        ingredients_by_recipe=dict(ingredients_by_recipe),
        master_rows=master_rows,
        master_by_code=master_by_code,
        master_alias_index=master_alias_index,
        revision=revision,
    )


async def load_snapshot(session: AsyncSession) -> CatalogSnapshot:
    """Load an immutable CatalogSnapshot from the database per shared contract."""
    from sqlalchemy import text

    from AI.catalog.errors import CatalogNotLoadedError
    from src.model.ingredient_alias_model import IngredientAliasModel
    from src.model.master_ingredient_model import MasterIngredientModel
    from src.model.recipe_ingredient_model import RecipeIngredientModel
    from src.model.recipe_model import RecipeModel

    recipes_result = await session.execute(
        select(RecipeModel)
        .where(RecipeModel.ai_features != text("'{}'::jsonb"))
        .order_by(RecipeModel.id)
    )
    recipe_models = list(recipes_result.scalars().all())

    if not recipe_models:
        raise CatalogNotLoadedError(
            "No AI recipes found in the database. Run 'python -m AI.catalog.importer' to populate the catalog."
        )

    ai_recipe_ids = [r.id for r in recipe_models]

    ings_result = await session.execute(
        select(RecipeIngredientModel)
        .where(
            RecipeIngredientModel.recipe_id.in_(ai_recipe_ids),
            RecipeIngredientModel.ai_attributes != text("'{}'::jsonb"),
        )
        .order_by(RecipeIngredientModel.id)
    )
    ing_models = list(ings_result.scalars().all())

    used_master_ids = {ing.master_ingredient_id for ing in ing_models}
    if used_master_ids:
        master_filter = (MasterIngredientModel.source_code.is_not(None)) | (
            MasterIngredientModel.id.in_(used_master_ids)
        )
    else:
        master_filter = MasterIngredientModel.source_code.is_not(None)

    master_result = await session.execute(
        select(MasterIngredientModel).where(master_filter).order_by(MasterIngredientModel.id)
    )
    master_models = list(master_result.scalars().all())
    master_ids = [m.id for m in master_models]

    if master_ids:
        aliases_result = await session.execute(
            select(IngredientAliasModel)
            .where(IngredientAliasModel.master_ingredient_id.in_(master_ids))
            .order_by(IngredientAliasModel.id)
        )
    else:
        aliases_result = await session.execute(
            select(IngredientAliasModel).order_by(IngredientAliasModel.id)
        )
    alias_models = list(aliases_result.scalars().all())

    aliases_by_master_id: dict[str, list[str]] = defaultdict(list)
    for al in alias_models:
        aliases_by_master_id[str(al.master_ingredient_id)].append(al.alias)

    recipes: list[dict[str, Any]] = []
    recipes_by_id: dict[str, dict[str, Any]] = {}
    for r in recipe_models:
        r_id = str(r.id)
        ai_features = getattr(r, "ai_features", None) or {}
        r_dict: dict[str, Any] = {
            "id": r_id,
            "name": r.name,
            "source_platform": getattr(r, "source_platform", "internal"),
            "source_url": getattr(r, "source_url", ""),
            "default_servings": float(r.default_servings) if r.default_servings is not None else 4.0,
            "estimated_cooking_minutes": int(r.estimated_cooking_minutes) if r.estimated_cooking_minutes is not None else 30,
            "total_calories": float(r.total_calories) if getattr(r, "total_calories", None) is not None else 0.0,
            "total_protein_g": float(r.total_protein_g) if getattr(r, "total_protein_g", None) is not None else 0.0,
            "total_fat_g": float(r.total_fat_g) if getattr(r, "total_fat_g", None) is not None else 0.0,
            "total_carbs_g": float(r.total_carbs_g) if getattr(r, "total_carbs_g", None) is not None else 0.0,
            "total_sugar_g": float(r.total_sugar_g) if getattr(r, "total_sugar_g", None) is not None else 0.0,
            **ai_features,
        }
        recipes.append(r_dict)
        recipes_by_id[r_id] = r_dict

    ingredients: list[dict[str, Any]] = []
    ingredients_by_recipe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ing in ing_models:
        r_id = str(ing.recipe_id)
        ai_attrs = getattr(ing, "ai_attributes", None) or {}
        unit_val = getattr(ing, "unit", "")
        if hasattr(unit_val, "value"):
            unit_str = str(unit_val.value)
        else:
            unit_str = str(unit_val)
        ing_dict: dict[str, Any] = {
            "id": str(ing.id),
            "recipe_id": r_id,
            "required_quantity": float(ing.required_quantity) if getattr(ing, "required_quantity", None) is not None else 0.0,
            "unit": unit_str,
            **ai_attrs,
        }
        ingredients.append(ing_dict)
        ingredients_by_recipe[r_id].append(ing_dict)

    master_rows: list[dict[str, Any]] = []
    master_by_code: dict[str, dict[str, Any]] = {}
    for m in master_models:
        m_id = str(m.id)
        source_code = getattr(m, "source_code", None)
        other_nutrients = getattr(m, "other_nutrients", None) or {}
        code = str(source_code or other_nutrients.get("code") or "")
        db_aliases = aliases_by_master_id.get(m_id, [])
        csv_aliases = other_nutrients.get("aliases") or ""
        all_aliases_set = set(filter(None, [a.strip() for a in str(csv_aliases).split(";")]))
        for da in db_aliases:
            if da.strip():
                all_aliases_set.add(da.strip())
        combined_aliases = ";".join(sorted(all_aliases_set))

        m_dict: dict[str, Any] = {
            "id": m_id,
            "code": code,
            "name_vi": m.name,
            "name_en": other_nutrients.get("name_en", ""),
            "category_vi": other_nutrients.get("category_vi", ""),
            "aliases": combined_aliases,
            **other_nutrients,
        }
        master_rows.append(m_dict)
        if code:
            master_by_code[code] = m_dict

    master_alias_index = build_master_alias_index(master_rows)

    content_canonical = json.dumps(
        {
            "recipes": [
                {
                    "id": str(r.id),
                    "ai_features": getattr(r, "ai_features", None) or {},
                }
                for r in sorted(recipe_models, key=lambda r: str(r.id))
            ],
            "ingredients": [
                {
                    "id": str(ing.id),
                    "recipe_id": str(ing.recipe_id),
                    "ai_attributes": getattr(ing, "ai_attributes", None) or {},
                }
                for ing in sorted(ing_models, key=lambda i: str(i.id))
            ],
            "masters": [
                {
                    "id": str(m.id),
                    "source_code": getattr(m, "source_code", None) or "",
                }
                for m in sorted(master_models, key=lambda m: str(m.id))
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    rev_hash = hashlib.sha256(content_canonical).hexdigest()[:12]
    revision = f"catalog-db-{len(recipes)}-{rev_hash}"

    return CatalogSnapshot(
        recipes=recipes,
        recipes_by_id=recipes_by_id,
        ingredients=ingredients,
        ingredients_by_recipe=dict(ingredients_by_recipe),
        master_rows=master_rows,
        master_by_code=master_by_code,
        master_alias_index=master_alias_index,
        revision=revision,
    )


# Process-wide cached singleton
_SNAPSHOT_CACHE: CatalogSnapshot | None = None
_SNAPSHOT_LOCK = asyncio.Lock()


async def get_catalog_snapshot(
    session: AsyncSession | None = None,
) -> CatalogSnapshot:
    """Return process-wide cached snapshot. Lazily loads from DB if not initialized."""
    global _SNAPSHOT_CACHE
    if _SNAPSHOT_CACHE is not None:
        return _SNAPSHOT_CACHE

    async with _SNAPSHOT_LOCK:
        if _SNAPSHOT_CACHE is not None:
            return _SNAPSHOT_CACHE

        if session is None:
            raise CatalogNotLoadedError(
                "Catalog is not loaded in memory and no database session was provided."
            )

        snapshot = await load_snapshot(session)
        if not snapshot.recipes:
            raise CatalogNotLoadedError()

        _SNAPSHOT_CACHE = snapshot
        return _SNAPSHOT_CACHE


def invalidate_catalog_snapshot() -> None:
    """Clear process-wide cached snapshot so next request reloads."""
    global _SNAPSHOT_CACHE
    _SNAPSHOT_CACHE = None


async def warm_up(session: AsyncSession) -> None:
    """Lifespan warm-up: loads snapshot from DB if available, else stays lazy."""
    try:
        snapshot = await load_snapshot(session)
        if snapshot.recipes:
            global _SNAPSHOT_CACHE
            _SNAPSHOT_CACHE = snapshot
            logger.info(
                "Catalog snapshot warmed up from database (%d recipes, revision %s).",
                len(snapshot.recipes),
                snapshot.revision,
            )
        else:
            logger.info("Catalog database empty on startup; staying lazy.")
    except SQLAlchemyError as exc:
        logger.warning(
            "Catalog warm-up skipped (database query failed): %s", exc
        )
