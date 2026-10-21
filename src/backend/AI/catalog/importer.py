"""Import SweepFood AI catalog bundle into PostgreSQL."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import cast
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql.schema import Table

from scripts.ingredient_category_import import (
    category_description,
    category_id,
    normalize_text,
)
from scripts.recipe_import import factual_description
from src.db import build_async_database_url
from src.model.enum_model import MeasurementUnit
from src.model.ingredient_alias_model import IngredientAliasModel
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel

logger = logging.getLogger(__name__)

DEFAULT_BUNDLE_DIR = Path(__file__).resolve().parent.parent / "data"
UNCLASSIFIED_CATEGORY = "Chưa phân loại"
VALID_MEASUREMENT_UNITS = frozenset(MeasurementUnit.__members__.keys())
PRIMARY_MASTER_NUTRIENT_COLS = frozenset({
    "code",
    "name_vi",
    "energy_kcal",
    "protein_g",
    "fat_g",
    "carbs_g",
    "sugar_g",
    "sodium_mg",
})


def parse_csv_value(value: str) -> object:
    """Parse numeric values from CSV strings while keeping strings intact."""
    if value == "":
        return ""
    try:
        val_int = int(value)
        if str(val_int) == value:
            return val_int
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def decimal_value(val_str: str | None) -> Decimal | None:
    """Safely parse a finite positive or zero decimal at 3-decimal precision."""
    if not val_str or not val_str.strip():
        return None
    try:
        dec = Decimal(val_str.strip())
        if not dec.is_finite() or dec < 0:
            return None
        return dec.quantize(Decimal("0.001"))
    except (InvalidOperation, ValueError):
        return None


def resolve_ingredient_id(raw_id: str) -> UUID:
    """Return the original UUID when standard, or a deterministic UUID5 for composite IDs."""
    clean_id = raw_id.strip()
    try:
        return UUID(clean_id)
    except ValueError:
        return uuid5(NAMESPACE_URL, f"sweep-food:recipe-ingredient:{clean_id}")


def derive_nutrition_status(incomplete_flag: object, anomaly_flag: object) -> str:
    """Derive database recipe nutrition status from catalog flags."""
    inc = int(incomplete_flag) if str(incomplete_flag).strip() in ("0", "1") else 1
    anom = int(anomaly_flag) if str(anomaly_flag).strip() in ("0", "1") else 0
    if inc:
        return "INCOMPLETE"
    return "PARTIAL" if anom else "COMPLETE"

def values_differ(val1: object, val2: object) -> bool:
    """Compare two database column values for equality across Decimals, Enums, and JSONB."""
    if val1 == val2:
        return False
    if val1 is None and val2 is None:
        return False
    if (val1 is None) != (val2 is None):
        return True
    if hasattr(val1, "value"):
        val1 = val1.value
    if hasattr(val2, "value"):
        val2 = val2.value
    if val1 == val2:
        return False
    if isinstance(val1, (int, float, Decimal)) and isinstance(val2, (int, float, Decimal)):
        try:
            return abs(float(val1) - float(val2)) > 1e-6
        except (ValueError, TypeError):
            return True
    if isinstance(val1, dict) and isinstance(val2, dict):
        return val1 != val2
    if isinstance(val1, str) and isinstance(val2, str):
        return val1.strip() != val2.strip()
    return True

@dataclass
class ImportReport:
    """Classified outcomes and audit trail for an import run."""

    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    redirected: list[str] = field(default_factory=list)
    created_placeholders: list[str] = field(default_factory=list)

    def add(self, outcome: str, record: str) -> None:
        """Add one classified record outcome."""
        if outcome == "created (placeholder)":
            self.created_placeholders.append(record)
            self.created.append(record)
        else:
            target: list[str] = getattr(self, outcome)
            target.append(record)

    def rejection_breakdown(self) -> dict[str, int]:
        """Categorize rejected records by failure reason."""
        breakdown = {
            "alias_duplicates": 0,
            "duplicate_recipe_names": 0,
            "duplicate_recipe_urls": 0,
            "duplicate_recipe_ids": 0,
            "unknown_master_codes": 0,
            "other": 0,
        }
        for item in self.rejected:
            if item.startswith("alias:"):
                breakdown["alias_duplicates"] += 1
            elif "duplicate name" in item:
                breakdown["duplicate_recipe_names"] += 1
            elif "duplicate source_url" in item:
                breakdown["duplicate_recipe_urls"] += 1
            elif "duplicate id" in item:
                breakdown["duplicate_recipe_ids"] += 1
            elif "unknown master code" in item:
                breakdown["unknown_master_codes"] += 1
            else:
                breakdown["other"] += 1
        return breakdown

    def summary(self) -> str:
        """Return a concise summary with per-reason breakdown of the import outcome."""
        breakdown = self.rejection_breakdown()
        rejection_details = ", ".join(
            f"{k}={v}" for k, v in breakdown.items() if v > 0
        ) or "none"
        placeholders_note = (
            f" [placeholders={len(self.created_placeholders)}]"
            if self.created_placeholders
            else ""
        )
        return (
            f"created={len(self.created)}{placeholders_note} updated={len(self.updated)} "
            f"unchanged={len(self.unchanged)} rejected={len(self.rejected)} "
            f"({rejection_details}) redirected={len(self.redirected)}"
        )

@dataclass(frozen=True)
class CatalogBundleRaw:
    """Raw CSV rows loaded directly from the catalog bundle."""

    recipes: list[dict[str, str]]
    recipe_ingredients: list[dict[str, str]]
    master_nutrition: list[dict[str, str]]
    redirects: list[dict[str, str]]
    recipe_media: list[dict[str, object]] = field(default_factory=list)

@dataclass(frozen=True)
class CatalogTransformedData:
    """Database-ready rows validated from the catalog bundle."""

    categories: list[dict[str, object]]
    masters: list[dict[str, object]]
    aliases: list[dict[str, object]]
    recipes: list[dict[str, object]]
    recipe_ingredients: list[dict[str, object]]
    placeholder_ids: set[UUID] = field(default_factory=set)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """Load a UTF-8/UTF-8-SIG CSV file into a list of row dicts."""
    if not path.is_file():
        raise FileNotFoundError(f"Bundle file not found: {path}")
    with path.open(mode="r", encoding="utf-8-sig") as file_handle:
        reader = csv.DictReader(file_handle)
        return list(reader)

def load_recipe_media(path: Path) -> list[dict[str, object]]:
    """Load and validate recipe_media.json next to the catalog bundle."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Recipe media file not found: {path} (run 'python -m AI.catalog.media_builder' to generate it)"
        )
    try:
        with path.open(mode="r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Recipe media file is malformed JSON: {path}: {exc}") from exc
    if not isinstance(data, list):
        raise TypeError(f"Recipe media file must contain a JSON list: {path}")
    for item in data:
        if not isinstance(item, dict) or "id" not in item:
            raise TypeError(f"Recipe media entries must be objects with 'id': {path}")
    return cast(list[dict[str, object]], data)



def load_catalog_bundle(bundle_dir: Path) -> CatalogBundleRaw:
    """Read every required CSV file from the given bundle directory."""
    catalog_dir = bundle_dir / "catalog"
    master_dir = bundle_dir / "master_ingredients"

    recipes_path = catalog_dir / "recipes.csv"
    recipe_ings_path = catalog_dir / "recipe_ingredients.csv"
    master_path = master_dir / "master_ingredients_nutrition.csv"
    redirects_path = master_dir / "master_code_redirects.csv"
    media_path = catalog_dir / "recipe_media.json"

    recipes = load_csv_rows(recipes_path)
    recipe_ingredients = load_csv_rows(recipe_ings_path)
    master_nutrition = load_csv_rows(master_path)
    redirects = load_csv_rows(redirects_path) if redirects_path.exists() else []
    recipe_media = load_recipe_media(media_path)

    return CatalogBundleRaw(
        recipes=recipes,
        recipe_ingredients=recipe_ingredients,
        master_nutrition=master_nutrition,
        redirects=redirects,
        recipe_media=recipe_media,
    )


def transform_categories(
    master_nutrition: list[dict[str, str]],
) -> list[dict[str, object]]:
    """Normalize unique master ingredient categories into ingredient_categories rows."""
    categories_by_name: dict[str, dict[str, object]] = {}
    unclass_uuid = UUID(category_id(UNCLASSIFIED_CATEGORY))
    categories_by_name[UNCLASSIFIED_CATEGORY] = {
        "id": unclass_uuid,
        "name": UNCLASSIFIED_CATEGORY,
        "description": category_description(UNCLASSIFIED_CATEGORY),
    }

    for row in master_nutrition:
        raw_cat = row.get("category_vi", "")
        norm_cat = normalize_text(raw_cat)
        if norm_cat and norm_cat not in categories_by_name:
            cat_uuid = UUID(category_id(norm_cat))
            desc = category_description(norm_cat)
            categories_by_name[norm_cat] = {
                "id": cat_uuid,
                "name": norm_cat,
                "description": desc,
            }
    return list(categories_by_name.values())


def transform_masters(
    master_nutrition: list[dict[str, str]],
    categories_lookup: dict[str, UUID],
) -> list[dict[str, object]]:
    """Transform master nutrition CSV rows into master_ingredients rows."""
    masters: list[dict[str, object]] = []
    for row in master_nutrition:
        code = row["code"].strip()
        master_uuid = uuid5(NAMESPACE_URL, f"sweep-food:master-ingredient:{code}")
        norm_cat = normalize_text(row.get("category_vi", ""))
        category_uuid = categories_lookup.get(norm_cat)
        if category_uuid is None:
            raise ValueError(f"Master ingredient {code} has unknown category {norm_cat!r}")

        other_nutrients: dict[str, object] = {}
        for key, val in row.items():
            if key not in PRIMARY_MASTER_NUTRIENT_COLS:
                other_nutrients[key] = parse_csv_value(val)

        name_vi = normalize_text(row.get("name_vi", ""))
        masters.append({
            "id": master_uuid,
            "name": name_vi,
            "description": None,
            "category_id": category_uuid,
            "default_media_url": None,
            "canonical_unit": MeasurementUnit.GRAM,
            "calories": decimal_value(row.get("energy_kcal")),
            "protein_g": decimal_value(row.get("protein_g")),
            "fat_g": decimal_value(row.get("fat_g")),
            "carbs_g": decimal_value(row.get("carbs_g")),
            "sugar_g": decimal_value(row.get("sugar_g")),
            "sodium_mg": decimal_value(row.get("sodium_mg")),
            "other_nutrients": other_nutrients,
            "default_storage_mode": None,
            "is_verified": True,
            "source_code": code,
        })
    return masters


def transform_aliases(
    master_nutrition: list[dict[str, str]],
    master_code_to_id: dict[str, UUID],
    report: ImportReport,
) -> list[dict[str, object]]:
    """Extract and deduplicate aliases for ingredient_aliases table."""
    aliases: list[dict[str, object]] = []
    seen_aliases: dict[str, str] = {}

    for row in master_nutrition:
        code = row["code"].strip()
        master_uuid = master_code_to_id.get(code)
        if master_uuid is None:
            continue
        raw_aliases = row.get("aliases", "")
        if not raw_aliases:
            continue
        for part in raw_aliases.split(";"):
            raw_alias = part.strip()
            norm_alias = normalize_text(raw_alias).casefold()
            if not norm_alias:
                continue
            if norm_alias in seen_aliases:
                report.add(
                    "rejected",
                    f"alias:{norm_alias} duplicate between code {seen_aliases[norm_alias]} and {code}",
                )
                continue
            seen_aliases[norm_alias] = code
            alias_uuid = uuid5(NAMESPACE_URL, f"sweep-food:ingredient-alias:{norm_alias}")
            aliases.append({
                "id": alias_uuid,
                "master_ingredient_id": master_uuid,
                "alias": raw_alias,
                "normalized_alias": norm_alias,
            })
    return aliases


def transform_recipes(
    recipe_rows: list[dict[str, str]],
    report: ImportReport,
    media_by_id: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Transform and validate recipes.csv rows into recipes table rows."""
    recipes: list[dict[str, object]] = []
    seen_ids: set[UUID] = set()
    seen_names: set[str] = set()
    seen_urls: set[str] = set()

    for row in recipe_rows:
        raw_id = row.get("id", "").strip()
        try:
            recipe_uuid = UUID(raw_id)
        except ValueError:
            report.add("rejected", f"recipe has invalid UUID: {raw_id!r}")
            continue

        raw_name = row.get("name", "")
        name = normalize_text(raw_name)
        if not name:
            report.add("rejected", f"recipe:{recipe_uuid} has blank name")
            continue

        source_url = row.get("source_url", "").strip()
        if not source_url:
            report.add("rejected", f"recipe:{recipe_uuid} has blank source_url")
            continue

        if recipe_uuid in seen_ids:
            report.add("rejected", f"recipe:{recipe_uuid} duplicate id")
            continue
        if name.casefold() in seen_names:
            report.add("rejected", f"recipe:{recipe_uuid} duplicate name {name!r}")
            continue
        if source_url in seen_urls:
            report.add("rejected", f"recipe:{recipe_uuid} duplicate source_url {source_url!r}")
            continue

        seen_ids.add(recipe_uuid)
        seen_names.add(name.casefold())
        seen_urls.add(source_url)

        try:
            default_servings = Decimal(str(row.get("default_servings", "4.0"))).quantize(Decimal("0.01"))
            if default_servings <= 0:
                default_servings = Decimal("4.00")
        except (InvalidOperation, ValueError):
            default_servings = Decimal("4.00")

        try:
            cooking_minutes = int(float(row.get("estimated_cooking_minutes", "30")))
        except (ValueError, TypeError):
            cooking_minutes = 30

        dish_type = normalize_text(row.get("dish_type", ""))
        cooking_method = normalize_text(row.get("cooking_method", ""))
        status = derive_nutrition_status(
            row.get("incomplete_flag", 0),
            row.get("nutrition_anomaly_flag", 0),
        )

        diet_tags = [
            normalize_text(t)
            for t in row.get("diet_tags", "").split(",")
            if normalize_text(t)
        ]
        tags: dict[str, object] = {
            "cooking_method": cooking_method,
            "dish_type": dish_type,
            "diet": diet_tags,
        }

        other_nutrients: dict[str, object] = {}
        if row.get("total_sodium_mg"):
            try:
                other_nutrients["sodium_mg"] = float(row["total_sodium_mg"])
            except ValueError:
                pass
        if row.get("total_fiber_g"):
            try:
                other_nutrients["fiber_g"] = float(row["total_fiber_g"])
            except ValueError:
                pass

        ai_features: dict[str, object] = {
            key: parse_csv_value(val) for key, val in row.items() if key != "id"
        }

        media_entry = media_by_id.get(str(recipe_uuid)) if media_by_id else None
        media_url: str | None = None
        instructions: dict[str, object] = {"steps": []}

        if media_entry:
            raw_media = media_entry.get("media_url")
            if isinstance(raw_media, str) and raw_media.strip():
                media_url = raw_media.strip()

            raw_steps = media_entry.get("steps")
            if isinstance(raw_steps, list) and raw_steps:
                formatted_steps: list[dict[str, object]] = []
                for s in raw_steps:
                    if isinstance(s, str) and s.strip():
                        order = len(formatted_steps) + 1
                        formatted_steps.append({"order": order, "text": s.strip()})
                    elif isinstance(s, dict):
                        step_val = s.get("step")
                        if step_val is None:
                            step_val = s.get("order")
                        order = (
                            int(step_val)
                            if isinstance(step_val, int)
                            else len(formatted_steps) + 1
                        )
                        raw_title = s.get("title")
                        title = str(raw_title).strip() if raw_title is not None else ""
                        raw_content = s.get("content")
                        content = str(raw_content).strip() if raw_content is not None else ""
                        if not content and isinstance(s.get("text"), str):
                            content = cast(str, s["text"]).strip()

                        if title and title != f"Bước {order}" and not content.startswith(title):
                            text = f"{title}: {content}" if content else title
                        else:
                            text = content or title

                        if not text:
                            continue

                        step_dict: dict[str, object] = {
                            "order": order,
                            "text": text,
                        }
                        if "duration_min" in s and s["duration_min"] is not None:
                            step_dict["duration_min"] = s["duration_min"]
                        formatted_steps.append(step_dict)

                instructions = {"steps": formatted_steps}

        recipes.append({
            "id": recipe_uuid,
            "name": name,
            "description": factual_description(name, dish_type, cooking_method, str(default_servings)),
            "instructions": instructions,
            "media_url": media_url,
            "source_platform": normalize_text(row.get("source_platform", "internal")),
            "source_url": source_url,
            "default_servings": default_servings,
            "estimated_cooking_minutes": cooking_minutes,
            "estimated_cost": None,
            "total_calories": decimal_value(row.get("total_calories")),
            "total_protein_g": decimal_value(row.get("total_protein_g")),
            "total_fat_g": decimal_value(row.get("total_fat_g")),
            "total_carbs_g": decimal_value(row.get("total_carbs_g")),
            "total_sugar_g": decimal_value(row.get("total_sugar_g")),
            "other_nutrients": other_nutrients,
            "nutrition_status": status,
            "tags": tags,
            "ai_features": ai_features,
        })
    return recipes


def transform_recipe_ingredients(
    ingredient_rows: list[dict[str, str]],
    valid_recipe_ids: set[UUID],
    master_code_to_id: dict[str, UUID],
    redirect_map: dict[str, str],
    unclassified_category_id: UUID,
    placeholder_masters: dict[UUID, dict[str, object]],
    report: ImportReport,
) -> list[dict[str, object]]:
    """Transform and validate recipe_ingredients.csv rows into recipe_ingredients table rows."""
    recipe_ingredients: list[dict[str, object]] = []
    seen_ids: set[UUID] = set()

    for row in ingredient_rows:
        raw_id = row.get("id", "").strip()
        ingredient_uuid = resolve_ingredient_id(raw_id)

        raw_recipe_id = row.get("recipe_id", "").strip()
        try:
            recipe_uuid = UUID(raw_recipe_id)
        except ValueError:
            report.add("rejected", f"recipe_ingredient:{ingredient_uuid} invalid recipe UUID {raw_recipe_id!r}")
            continue

        if recipe_uuid not in valid_recipe_ids:
            report.add("rejected", f"recipe_ingredient:{ingredient_uuid} references unknown recipe:{recipe_uuid}")
            continue

        raw_code = row.get("master_ingredient_code", "").strip()
        code = raw_code
        if code in redirect_map:
            canonical_code = redirect_map[code]
            report.add("redirected", f"recipe_ingredient:{ingredient_uuid} code {code} -> {canonical_code}")
            code = canonical_code

        if not code:
            cleaned_name = normalize_text(
                row.get("cleaned_name") or row.get("raw_text") or "Nguyên liệu chưa định danh"
            )
            placeholder_id = uuid5(
                NAMESPACE_URL,
                f"sweep-food:master-ingredient:unclassified:{cleaned_name.casefold()}",
            )
            if placeholder_id not in placeholder_masters:
                placeholder_masters[placeholder_id] = {
                    "id": placeholder_id,
                    "name": cleaned_name,
                    "description": f"Placeholder master for unmatched ingredient: {cleaned_name}",
                    "category_id": unclassified_category_id,
                    "default_media_url": None,
                    "canonical_unit": MeasurementUnit.GRAM,
                    "calories": None,
                    "protein_g": None,
                    "fat_g": None,
                    "carbs_g": None,
                    "sugar_g": None,
                    "sodium_mg": None,
                    "other_nutrients": {"source_type": "placeholder", "cleaned_name": cleaned_name},
                    "default_storage_mode": None,
                    "is_verified": False,
                    "source_code": None,
                }
            master_uuid = placeholder_id
        elif code not in master_code_to_id:
            report.add("rejected", f"recipe_ingredient:{ingredient_uuid} unknown master code: {raw_code!r}")
            continue
        else:
            master_uuid = master_code_to_id[code]

        if ingredient_uuid in seen_ids:
            report.add("rejected", f"recipe_ingredient:{ingredient_uuid} duplicate ingredient ID")
            continue
        seen_ids.add(ingredient_uuid)

        raw_qty = row.get("required_quantity", "").strip()
        raw_weight = row.get("estimated_weight_g", "").strip()
        raw_unit = row.get("unit", "").strip()

        req_qty_parsed = decimal_value(raw_qty)
        if req_qty_parsed is not None and req_qty_parsed > 0:
            req_qty = req_qty_parsed
            unit = MeasurementUnit(raw_unit) if raw_unit in VALID_MEASUREMENT_UNITS else MeasurementUnit.OTHER
            display_qty = req_qty
            display_unit = row.get("unit_vi") or raw_unit or None
        else:
            weight_parsed = decimal_value(raw_weight)
            if weight_parsed is not None and weight_parsed > 0:
                req_qty = weight_parsed
                unit = MeasurementUnit.GRAM
            else:
                req_qty = Decimal("1.000")
                unit = MeasurementUnit(raw_unit) if raw_unit in VALID_MEASUREMENT_UNITS else MeasurementUnit.OTHER
            display_qty = None
            display_unit = row.get("unit_vi") or None

        preparation_note = row.get("preparation_note", "").strip() or None
        ai_attributes: dict[str, object] = {
            key: val for key, val in row.items() if key not in ("id", "recipe_id")
        }

        recipe_ingredients.append({
            "id": ingredient_uuid,
            "recipe_id": recipe_uuid,
            "master_ingredient_id": master_uuid,
            "required_quantity": req_qty,
            "unit": unit,
            "display_quantity": display_qty,
            "display_unit": display_unit,
            "is_optional": False,
            "preparation_note": preparation_note,
            "ai_attributes": ai_attributes,
        })
    return recipe_ingredients


def transform_catalog_bundle(
    bundle: CatalogBundleRaw,
    report: ImportReport | None = None,
) -> tuple[CatalogTransformedData, ImportReport]:
    """Execute pure transformation pipeline and return validated data and outcome report."""
    if report is None:
        report = ImportReport()

    redirect_map = {
        row["old_code"].strip(): row["canonical_code"].strip()
        for row in bundle.redirects
        if row.get("old_code") and row.get("canonical_code")
    }

    categories = transform_categories(bundle.master_nutrition)
    categories_lookup = {cast(str, cat["name"]): cast(UUID, cat["id"]) for cat in categories}
    unclassified_cat_uuid = categories_lookup[UNCLASSIFIED_CATEGORY]

    masters = transform_masters(bundle.master_nutrition, categories_lookup)
    master_code_to_id = {cast(str, m["source_code"]): cast(UUID, m["id"]) for m in masters}

    aliases = transform_aliases(bundle.master_nutrition, master_code_to_id, report)

    media_by_id = {
        str(item["id"]).strip(): item
        for item in bundle.recipe_media
        if isinstance(item, dict) and "id" in item
    }
    recipes = transform_recipes(bundle.recipes, report, media_by_id)
    valid_recipe_ids = {cast(UUID, r["id"]) for r in recipes}

    placeholder_masters: dict[UUID, dict[str, object]] = {}
    recipe_ingredients = transform_recipe_ingredients(
        bundle.recipe_ingredients,
        valid_recipe_ids,
        master_code_to_id,
        redirect_map,
        unclassified_cat_uuid,
        placeholder_masters,
        report,
    )

    all_masters = masters + list(placeholder_masters.values())
    placeholder_ids = set(placeholder_masters.keys())

    data = CatalogTransformedData(
        categories=categories,
        masters=all_masters,
        aliases=aliases,
        recipes=recipes,
        recipe_ingredients=recipe_ingredients,
        placeholder_ids=placeholder_ids,
    )
    return data, report


async def _upsert_table_batch(
    session: AsyncSession,
    table: Table,
    rows: list[dict[str, object]],
    batch_size: int,
) -> None:
    """Upsert rows by primary key id in bounded batches."""
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        stmt = insert(table).values(batch)
        updates = {
            col: stmt.excluded[col] for col in batch[0] if col != "id"
        }
        await session.execute(
            stmt.on_conflict_do_update(index_elements=[table.c.id], set_=updates)
        )


async def _classify_and_upsert_table(
    session: AsyncSession,
    table: Table,
    rows: list[dict[str, object]],
    table_label: str,
    report: ImportReport,
    *,
    dry_run: bool,
    batch_size: int,
    placeholder_ids: set[UUID] | None = None,
) -> None:
    """Classify rows as created/updated/unchanged and upsert them if not dry-run."""
    if not rows:
        return

    existing_result = await session.execute(select(table))
    existing_by_id = {row_mapping["id"]: row_mapping for row_mapping in existing_result.mappings()}

    rows_to_upsert: list[dict[str, object]] = []

    for row in rows:
        row_id = cast(UUID, row["id"])
        existing = existing_by_id.get(row_id)
        if existing is None:
            if placeholder_ids and row_id in placeholder_ids:
                report.add("created (placeholder)", f"{table_label}:{row_id}")
            else:
                report.add("created", f"{table_label}:{row_id}")
            rows_to_upsert.append(row)
        else:
            changed = False
            for col_name, val in row.items():
                if col_name in existing:
                    existing_val = existing[col_name]
                    if values_differ(val, existing_val):
                        changed = True
                        break
            if changed:
                report.add("updated", f"{table_label}:{row_id}")
                rows_to_upsert.append(row)
            else:
                report.add("unchanged", f"{table_label}:{row_id}")

    if not dry_run and rows_to_upsert:
        await _upsert_table_batch(session, table, rows_to_upsert, batch_size)


async def import_catalog(
    database_url: str | None,
    data: CatalogTransformedData,
    report: ImportReport,
    *,
    dry_run: bool = False,
    batch_size: int = 500,
) -> ImportReport:
    """Upsert validated catalog data into PostgreSQL inside one transaction."""
    if dry_run and not database_url:
        logger.info("Dry-run without database URL; classifying all validated records as created.")
        for cat in data.categories:
            report.add("created", f"category:{cat['id']}")
        for m in data.masters:
            if m["id"] in data.placeholder_ids:
                report.add("created (placeholder)", f"master_ingredient:{m['id']}")
            else:
                report.add("created", f"master_ingredient:{m['id']}")
        for a in data.aliases:
            report.add("created", f"ingredient_alias:{a['id']}")
        for r in data.recipes:
            report.add("created", f"recipe:{r['id']}")
        for ing in data.recipe_ingredients:
            report.add("created", f"recipe_ingredient:{ing['id']}")
        return report

    try:
        engine = create_async_engine(
            build_async_database_url(cast(str, database_url)),
            connect_args={"statement_cache_size": 0},
            pool_pre_ping=True,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with session_factory() as session, session.begin():
                await _classify_and_upsert_table(
                    session,
                    cast(Table, IngredientCategoryModel.__table__),
                    data.categories,
                    "category",
                    report,
                    dry_run=dry_run,
                    batch_size=batch_size,
                )
                await _classify_and_upsert_table(
                    session,
                    cast(Table, MasterIngredientModel.__table__),
                    data.masters,
                    "master_ingredient",
                    report,
                    dry_run=dry_run,
                    batch_size=batch_size,
                    placeholder_ids=data.placeholder_ids,
                )
                await _classify_and_upsert_table(
                    session,
                    cast(Table, IngredientAliasModel.__table__),
                    data.aliases,
                    "ingredient_alias",
                    report,
                    dry_run=dry_run,
                    batch_size=batch_size,
                )
                await _classify_and_upsert_table(
                    session,
                    cast(Table, RecipeModel.__table__),
                    data.recipes,
                    "recipe",
                    report,
                    dry_run=dry_run,
                    batch_size=batch_size,
                )
                await _classify_and_upsert_table(
                    session,
                    cast(Table, RecipeIngredientModel.__table__),
                    data.recipe_ingredients,
                    "recipe_ingredient",
                    report,
                    dry_run=dry_run,
                    batch_size=batch_size,
                )
        finally:
            await engine.dispose()
    except Exception as exc:
        if dry_run:
            logger.warning(
                "Database unavailable during dry-run; recording transformed records as created: %s",
                exc,
            )
            for cat in data.categories:
                report.add("created", f"category:{cat['id']}")
            for m in data.masters:
                if m["id"] in data.placeholder_ids:
                    report.add("created (placeholder)", f"master_ingredient:{m['id']}")
                else:
                    report.add("created", f"master_ingredient:{m['id']}")
            for a in data.aliases:
                report.add("created", f"ingredient_alias:{a['id']}")
            for r in data.recipes:
                report.add("created", f"recipe:{r['id']}")
            for ing in data.recipe_ingredients:
                report.add("created", f"recipe_ingredient:{ing['id']}")
        else:
            raise

    return report


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI options for the catalog importer."""
    parser = argparse.ArgumentParser(
        description="Import SweepFood AI catalog bundle into PostgreSQL.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate bundle without writing to the database.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help=f"Path to AI data bundle directory (default: {DEFAULT_BUNDLE_DIR}).",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="Database URL (default: DATABASE_URL environment setting).",
    )
    parser.add_argument(
        "--replace-catalog",
        action="store_true",
        default=False,
        help="Replace live catalog with bundle, protecting or cascading user activity.",
    )
    parser.add_argument(
        "--delete-user-data",
        action="store_true",
        default=False,
        help="When --replace-catalog is set, cascade-delete user activity referencing removed catalog rows.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory to write pre-mutation JSONL backups.",
    )
    return parser.parse_args(args)

def resolve_database_url(url: str | None = None) -> str | None:
    """Return database URL from argument, setting, or environment lazily."""
    if url:
        return url
    import os

    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    try:
        from src.core.setting import DATABASE_URL

        return DATABASE_URL
    except (KeyError, ImportError):
        return None


async def run_importer(
    bundle_dir: Path,
    database_url: str | None = None,
    *,
    dry_run: bool = False,
) -> ImportReport:
    """Load bundle, transform, and apply to database."""
    resolved_db_url = database_url or resolve_database_url()
    bundle = load_catalog_bundle(bundle_dir)
    report = ImportReport()
    data, report = transform_catalog_bundle(bundle, report)

    logger.info(
        "Catalog bundle transformed: %d categories, %d masters, %d aliases, %d recipes, %d ingredients",
        len(data.categories),
        len(data.masters),
        len(data.aliases),
        len(data.recipes),
        len(data.recipe_ingredients),
    )

    await import_catalog(resolved_db_url, data, report, dry_run=dry_run)
    return report

def main(args: Sequence[str] | None = None) -> None:
    """CLI entrypoint for python -m AI.catalog.importer."""
    parsed = parse_args(args)
    if parsed.replace_catalog:
        from AI.catalog.replace import ReplaceOptions, run_replace_catalog

        options = ReplaceOptions(
            bundle_dir=parsed.bundle_dir,
            backup_dir=parsed.backup_dir,
            delete_user_data=parsed.delete_user_data,
            dry_run=parsed.dry_run,
            database_url=parsed.database_url,
        )
        asyncio.run(run_replace_catalog(options))
    else:
        report = asyncio.run(
            run_importer(
                bundle_dir=parsed.bundle_dir,
                database_url=parsed.database_url,
                dry_run=parsed.dry_run,
            )
        )
        print(f"Catalog import completed: {report.summary()}")

if __name__ == "__main__":
    main()
