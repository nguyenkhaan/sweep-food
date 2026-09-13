"""Import normalized catalog JSON into PostgreSQL."""
# uv run python scripts/import_data.py
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, cast
from uuid import UUID

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql.schema import Table

from src.db import build_async_database_url
from src.model.enum_model import MeasurementUnit, StorageMode
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data/normalized"
NUTRITION_STATUS = {"COMPLETE", "PARTIAL", "INCOMPLETE"}

CATEGORY_FIELDS = {"id", "name", "description"}
MASTER_FIELDS = {
    "id",
    "name",
    "description",
    "category_id",
    "default_media_url",
    "canonical_unit",
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
    "sugar_g",
    "sodium_mg",
    "other_nutrients",
    "default_storage_mode",
    "is_verified",
}
RECIPE_FIELDS = {
    "id",
    "name",
    "description",
    "instructions",
    "media_url",
    "source_platform",
    "source_url",
    "default_servings",
    "estimated_cooking_minutes",
    "estimated_cost",
    "total_calories",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "total_sugar_g",
    "other_nutrients",
    "nutrition_status",
    "tags",
}
RECIPE_INGREDIENT_FIELDS = {
    "id",
    "recipe_id",
    "master_ingredient_id",
    "required_quantity",
    "unit",
    "display_quantity",
    "display_unit",
    "is_optional",
    "preparation_note",
}


class DataValidationError(ValueError):
    """Raised when a normalized release cannot safely be imported."""


@dataclass(frozen=True)
class CatalogData:
    """Validated records ready for the four catalog tables."""

    categories: list[dict[str, object]]
    masters: list[dict[str, object]]
    recipes: list[dict[str, object]]
    recipe_ingredients: list[dict[str, object]]


def load_rows(input_path: Path, label: str) -> list[dict[str, Any]]:
    """Load one normalized JSON array without accepting non-object records."""
    try:
        rows = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise DataValidationError(f"Missing {label}: {input_path}") from error
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise DataValidationError(f"{label} must contain a JSON array of objects.")
    return rows


def require_contract(row: dict[str, Any], fields: set[str], label: str) -> None:
    """Reject unexpected or missing fields before values reach the database."""
    if set(row) != fields:
        missing = sorted(fields - set(row))
        unknown = sorted(set(row) - fields)
        raise DataValidationError(f"{label} has missing={missing} unknown={unknown} fields.")


def text_value(value: object, field: str, *, nullable: bool = False) -> str | None:
    """Validate a required or nullable non-blank text value."""
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DataValidationError(f"{field} must be a non-blank string.")
    return value


def uuid_value(value: object, field: str) -> UUID:
    """Convert one normalized UUID string to the database UUID type."""
    if not isinstance(value, str):
        raise DataValidationError(f"{field} must be a UUID string.")
    try:
        return UUID(value)
    except ValueError as error:
        raise DataValidationError(f"{field} is not a valid UUID.") from error


def decimal_value(
    value: object,
    field: str,
    *,
    nullable: bool = False,
    positive: bool = False,
) -> Decimal | None:
    """Convert a normalized finite decimal while preserving its exact value."""
    if value is None and nullable:
        return None
    if not isinstance(value, (str, int, float, Decimal)) or isinstance(value, bool):
        raise DataValidationError(f"{field} must be a decimal value.")
    try:
        decimal = Decimal(str(value))
    except InvalidOperation as error:
        raise DataValidationError(f"{field} is not a decimal value.") from error
    if not decimal.is_finite() or decimal < 0 or (positive and decimal <= 0):
        raise DataValidationError(f"{field} must be {'positive' if positive else 'non-negative'}.")
    return decimal


def object_value(value: object, field: str) -> dict[str, object]:
    """Require a JSON object for JSONB columns."""
    if not isinstance(value, dict):
        raise DataValidationError(f"{field} must be a JSON object.")
    return value


def enum_value(
    value: object, enum_type: type[MeasurementUnit | StorageMode], field: str
) -> MeasurementUnit | StorageMode:
    """Convert a serialized enum value to the enum used by SQLAlchemy."""
    if not isinstance(value, str):
        raise DataValidationError(f"{field} must be a string enum value.")
    try:
        return enum_type(value)
    except ValueError as error:
        raise DataValidationError(f"{field} has an unsupported value: {value!r}.") from error


def require_unique(values: list[object], label: str) -> None:
    """Reject duplicate release identities before any database write."""
    if len(set(values)) != len(values):
        raise DataValidationError(f"{label} contains duplicates.")


def build_catalog_data(input_dir: Path) -> CatalogData:
    """Load, validate, convert, and cross-check one normalized catalog release."""
    category_rows = load_rows(input_dir / "ingredient_categories.json", "ingredient_categories.json")
    master_rows = load_rows(input_dir / "master_ingredients.json", "master_ingredients.json")
    recipe_rows = load_rows(input_dir / "recipes.json", "recipes.json")
    recipe_ingredient_rows = load_rows(
        input_dir / "recipe_ingredients.json", "recipe_ingredients.json"
    )

    categories: list[dict[str, object]] = []
    for row in category_rows:
        require_contract(row, CATEGORY_FIELDS, "ingredient category")
        categories.append(
            {
                "id": uuid_value(row["id"], "category.id"),
                "name": text_value(row["name"], "category.name"),
                "description": text_value(
                    row["description"], "category.description", nullable=True
                ),
            }
        )
    category_ids = {row["id"] for row in categories}
    require_unique([row["id"] for row in categories], "ingredient category IDs")
    require_unique(
        [str(row["name"]).casefold() for row in categories], "ingredient category names"
    )

    masters: list[dict[str, object]] = []
    for row in master_rows:
        require_contract(row, MASTER_FIELDS, "master ingredient")
        category_id = uuid_value(row["category_id"], "master.category_id")
        if category_id not in category_ids:
            raise DataValidationError("master ingredient references an unknown category.")
        storage_mode = row["default_storage_mode"]
        masters.append(
            {
                "id": uuid_value(row["id"], "master.id"),
                "name": text_value(row["name"], "master.name"),
                "description": text_value(row["description"], "master.description", nullable=True),
                "category_id": category_id,
                "default_media_url": text_value(
                    row["default_media_url"], "master.default_media_url", nullable=True
                ),
                "canonical_unit": enum_value(
                    row["canonical_unit"], MeasurementUnit, "master.canonical_unit"
                ),
                "calories": decimal_value(row["calories"], "master.calories", nullable=True),
                "protein_g": decimal_value(row["protein_g"], "master.protein_g", nullable=True),
                "fat_g": decimal_value(row["fat_g"], "master.fat_g", nullable=True),
                "carbs_g": decimal_value(row["carbs_g"], "master.carbs_g", nullable=True),
                "sugar_g": decimal_value(row["sugar_g"], "master.sugar_g", nullable=True),
                "sodium_mg": decimal_value(row["sodium_mg"], "master.sodium_mg", nullable=True),
                "other_nutrients": object_value(row["other_nutrients"], "master.other_nutrients"),
                "default_storage_mode": None
                if storage_mode is None
                else enum_value(storage_mode, StorageMode, "master.default_storage_mode"),
                "is_verified": row["is_verified"],
            }
        )
        if not isinstance(row["is_verified"], bool):
            raise DataValidationError("master.is_verified must be boolean.")
    master_ids = {row["id"] for row in masters}
    require_unique([row["id"] for row in masters], "master ingredient IDs")
    require_unique(
        [(row["category_id"], str(row["name"]).casefold()) for row in masters],
        "master ingredient category/name keys",
    )

    recipes: list[dict[str, object]] = []
    for row in recipe_rows:
        require_contract(row, RECIPE_FIELDS, "recipe")
        status = text_value(row["nutrition_status"], "recipe.nutrition_status")
        if status not in NUTRITION_STATUS:
            raise DataValidationError("recipe.nutrition_status is invalid.")
        cooking_minutes = row["estimated_cooking_minutes"]
        if not isinstance(cooking_minutes, int) or isinstance(cooking_minutes, bool) or cooking_minutes < 0:
            raise DataValidationError("recipe.estimated_cooking_minutes must be non-negative.")
        estimated_cost = row["estimated_cost"]
        cost = (
            None
            if estimated_cost is None
            else decimal_value(estimated_cost, "recipe.estimated_cost")
        )
        if estimated_cost is not None and cost is None:
            raise DataValidationError("recipe.estimated_cost is missing.")
        recipes.append(
            {
                "id": uuid_value(row["id"], "recipe.id"),
                "name": text_value(row["name"], "recipe.name"),
                "description": text_value(row["description"], "recipe.description"),
                "instructions": object_value(row["instructions"], "recipe.instructions"),
                "media_url": text_value(row["media_url"], "recipe.media_url", nullable=True),
                "source_platform": text_value(row["source_platform"], "recipe.source_platform"),
                "source_url": text_value(row["source_url"], "recipe.source_url"),
                "default_servings": decimal_value(
                    row["default_servings"], "recipe.default_servings", positive=True
                ),
                "estimated_cooking_minutes": cooking_minutes,
                "estimated_cost": None if cost is None else float(cost),
                "total_calories": decimal_value(
                    row["total_calories"], "recipe.total_calories", nullable=True
                ),
                "total_protein_g": decimal_value(
                    row["total_protein_g"], "recipe.total_protein_g", nullable=True
                ),
                "total_fat_g": decimal_value(
                    row["total_fat_g"], "recipe.total_fat_g", nullable=True
                ),
                "total_carbs_g": decimal_value(
                    row["total_carbs_g"], "recipe.total_carbs_g", nullable=True
                ),
                "total_sugar_g": decimal_value(
                    row["total_sugar_g"], "recipe.total_sugar_g", nullable=True
                ),
                "other_nutrients": object_value(row["other_nutrients"], "recipe.other_nutrients"),
                "nutrition_status": status,
                "tags": object_value(row["tags"], "recipe.tags"),
            }
        )
    recipe_ids = {row["id"] for row in recipes}
    require_unique([row["id"] for row in recipes], "recipe IDs")
    require_unique([str(row["name"]).casefold() for row in recipes], "recipe names")
    require_unique([row["source_url"] for row in recipes], "recipe source URLs")

    recipe_ingredients: list[dict[str, object]] = []
    for row in recipe_ingredient_rows:
        require_contract(row, RECIPE_INGREDIENT_FIELDS, "recipe ingredient")
        recipe_id = uuid_value(row["recipe_id"], "recipe ingredient.recipe_id")
        master_id = uuid_value(
            row["master_ingredient_id"], "recipe ingredient.master_ingredient_id"
        )
        if recipe_id not in recipe_ids or master_id not in master_ids:
            raise DataValidationError("recipe ingredient has an unknown foreign key.")
        optional = row["is_optional"]
        if not isinstance(optional, bool):
            raise DataValidationError("recipe ingredient.is_optional must be boolean.")
        recipe_ingredients.append(
            {
                "id": uuid_value(row["id"], "recipe ingredient.id"),
                "recipe_id": recipe_id,
                "master_ingredient_id": master_id,
                "required_quantity": decimal_value(
                    row["required_quantity"], "recipe ingredient.required_quantity", positive=True
                ),
                "unit": enum_value(row["unit"], MeasurementUnit, "recipe ingredient.unit"),
                "display_quantity": decimal_value(
                    row["display_quantity"],
                    "recipe ingredient.display_quantity",
                    nullable=True,
                    positive=True,
                ),
                "display_unit": text_value(
                    row["display_unit"], "recipe ingredient.display_unit", nullable=True
                ),
                "is_optional": optional,
                "preparation_note": text_value(
                    row["preparation_note"], "recipe ingredient.preparation_note", nullable=True
                ),
            }
        )
    require_unique([row["id"] for row in recipe_ingredients], "recipe ingredient IDs")
    return CatalogData(categories, masters, recipes, recipe_ingredients)


async def upsert_rows(
    session: AsyncSession, table: Table, rows: list[dict[str, object]], batch_size: int
) -> None:
    """Upsert rows by stable UUID primary key in bounded PostgreSQL batches."""
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        statement = insert(table).values(batch)
        updates = {field: statement.excluded[field] for field in batch[0] if field != "id"}
        await session.execute(
            statement.on_conflict_do_update(index_elements=[table.c.id], set_=updates)
        )


async def import_catalog(
    database_url: str, data: CatalogData, *, dry_run: bool, batch_size: int
) -> None:
    """Write a validated release in dependency order within one transaction."""
    engine = create_async_engine(build_async_database_url(database_url), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            transaction = await session.begin()
            try:
                await upsert_rows(
                    session,
                    cast(Table, IngredientCategoryModel.__table__),
                    data.categories,
                    batch_size,
                )
                await upsert_rows(
                    session,
                    cast(Table, MasterIngredientModel.__table__),
                    data.masters,
                    batch_size,
                )
                await upsert_rows(
                    session, cast(Table, RecipeModel.__table__), data.recipes, batch_size
                )
                await upsert_rows(
                    session,
                    cast(Table, RecipeIngredientModel.__table__),
                    data.recipe_ingredients,
                    batch_size,
                )
                if dry_run:
                    await transaction.rollback()
                else:
                    await transaction.commit()
            except Exception:
                if transaction.is_active:
                    await transaction.rollback()
                raise
    finally:
        await engine.dispose()


def parse_args() -> argparse.Namespace:
    """Parse data-import options without exposing database credentials."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be greater than zero")
    return args


def application_database_url() -> str:
    """Read the project's configured database URL only when an import is run."""
    from src.core.setting import DATABASE_URL

    return DATABASE_URL


def main() -> None:
    """Validate JSON first, then import or dry-run the release."""
    args = parse_args()
    data = build_catalog_data(args.input_dir)
    asyncio.run(
        import_catalog(
            application_database_url(),
            data,
            dry_run=args.dry_run,
            batch_size=args.batch_size,
        )
    )
    mode = "Dry-run validated and rolled back" if args.dry_run else "Imported"
    print(
        f"{mode}: categories={len(data.categories)} masters={len(data.masters)} "
        f"recipes={len(data.recipes)} recipe_ingredients={len(data.recipe_ingredients)}"
    )


if __name__ == "__main__":
    main()
