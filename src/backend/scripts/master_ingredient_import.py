"""Transform raw ingredient sources into master_ingredients.json."""

from __future__ import annotations

import argparse
import json
import unicodedata
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FOOD_INPUT = PROJECT_ROOT / "data/raw/food_nutrition_raw.json"
DEFAULT_CATEGORY_OUTPUT = PROJECT_ROOT / "data/normalized/ingredient_categories.json"
DEFAULT_RECIPE_INGREDIENT_INPUT = (
    PROJECT_ROOT / "data/raw/recipes/canonical_recipe_ingredients.json"
)
DEFAULT_QWEN_MAP_INPUT = PROJECT_ROOT / "data/raw/qwen_extracted_map.json"
DEFAULT_MASTER_OUTPUT = PROJECT_ROOT / "data/normalized/master_ingredients.json"
UNCLASSIFIED_CATEGORY = "Chưa phân loại"
INVALID_MASTER_NAMES = {
    "vừa đủ",
    "tùy thích",
    "để trang trí",
    "nguyên liệu",
}
PRIMARY_NUTRIENT_FIELDS = {
    "protein": "protein_g",
    "total lipid (fat)": "fat_g",
    "carbohydrate by difference": "carbs_g",
    "sugars, total": "sugar_g",
    "na": "sodium_mg",
}
QWEN_MATCH_METHOD = "QWEN_LLM_MATCH"
QWEN_NO_INGREDIENT = "không có nguyên liệu cụ thể"
TRUSTED_ALIAS_METHODS = {"PRESET_ALIAS_MATCH"}


def normalize_text(value: str) -> str:
    """Return NFC text with zero-width characters and excess whitespace removed."""
    normalized = unicodedata.normalize("NFC", value).replace("\u200b", "")
    return " ".join(normalized.split())


def master_ingredient_id(category_uuid: str, name: str) -> str:
    """Return the stable UUID for one master-ingredient natural key."""
    return str(
        uuid5(
            NAMESPACE_URL,
            f"sweep-food:master-ingredient:{category_uuid}:{name.casefold()}",
        )
    )


def decimal_string(value: object, *, negative_as_none: bool = False) -> str | None:
    """Convert a finite source value to a fixed-scale decimal string."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid decimal value: {value!r}") from error
    if not decimal.is_finite():
        raise ValueError(f"Decimal must be finite: {value!r}")
    if decimal < 0:
        if negative_as_none:
            return None
        raise ValueError(f"Decimal must be non-negative: {value!r}")
    return format(decimal.quantize(Decimal("0.001")), "f")


def is_valid_master_name(name: str) -> bool:
    """Accept meaningful ingredient names and reject placeholders from recipe text."""
    return (
        2 <= len(name) <= 120
        and any(character.isalpha() for character in name)
        and name.casefold() not in INVALID_MASTER_NAMES
    )


def display_name(name: str) -> str:
    """Keep source spelling while capitalizing a derived ingredient's first character."""
    return f"{name[:1].upper()}{name[1:]}"


def load_food_rows(input_path: Path) -> list[dict[str, Any]]:
    """Load the paginated nutrition payload and return its data rows."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Expected food_nutrition_raw.json to contain a data array of objects.")
    return rows


def write_json(output_path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a complete JSON array atomically."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)


def load_json_rows(input_path: Path, label: str) -> list[dict[str, Any]]:
    """Load a JSON array of object records."""
    rows = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"Expected {label} to contain an array of objects.")
    return rows


def load_qwen_extracted_map(input_path: Path) -> dict[str, str]:
    """Load explicit raw-text to ingredient-name decisions from the Qwen review."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Expected qwen_extracted_map.json to contain an object.")

    mapping: dict[str, str] = {}
    for raw_text, extracted_name in payload.items():
        if not isinstance(raw_text, str) or not isinstance(extracted_name, str):
            raise TypeError("Qwen extracted map requires string keys and values.")
        key = normalize_text(raw_text)
        value = normalize_text(extracted_name)
        existing = mapping.get(key)
        if existing is not None and existing != value:
            raise ValueError(f"Conflicting Qwen mapping for {raw_text!r}.")
        mapping[key] = value
    return mapping


def qwen_extracted_name(
    recipe_ingredient: dict[str, Any], qwen_map: dict[str, str]
) -> str | None:
    """Return the reviewed Qwen extraction or the explicit no-ingredient sentinel."""
    raw_text = recipe_ingredient.get("raw_text")
    if not isinstance(raw_text, str):
        raise TypeError("Qwen recipe ingredient has no raw_text.")
    name = qwen_map.get(normalize_text(raw_text))
    if name is None:
        raise ValueError(f"Qwen map has no entry for {raw_text!r}.")
    if name.casefold() == QWEN_NO_INGREDIENT:
        return None
    return name


def category_ids_by_name(category_rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Build the normalized category-name to UUID lookup used by masters."""
    lookup: dict[str, str] = {}
    for row in category_rows:
        name = row.get("name")
        category_uuid = row.get("id")
        if not isinstance(name, str) or not isinstance(category_uuid, str):
            raise TypeError("Normalized category rows require string id and name.")
        key = normalize_text(name).casefold()
        if key in lookup:
            raise ValueError(f"Duplicate normalized category name: {name!r}")
        lookup[key] = category_uuid
    if UNCLASSIFIED_CATEGORY.casefold() not in lookup:
        raise ValueError("Normalized categories must include 'Chưa phân loại'.")
    return lookup


def nutrition_values(food: dict[str, Any]) -> tuple[dict[str, str | None], dict[str, object]]:
    """Map source nutrition values to master columns and preserve remaining values."""
    primary: dict[str, str | None] = {
        "calories": decimal_string(food.get("energy"), negative_as_none=True),
        "protein_g": None,
        "fat_g": None,
        "carbs_g": None,
        "sugar_g": None,
        "sodium_mg": None,
    }
    other: dict[str, object] = {}
    nutrients = food.get("nutrition", [])
    if not isinstance(nutrients, list):
        raise TypeError(f"Food {food.get('code', '<unknown>')} has invalid nutrition.")

    for nutrient in nutrients:
        if not isinstance(nutrient, dict):
            raise TypeError(f"Food {food.get('code', '<unknown>')} has invalid nutrient.")
        source_name = nutrient.get("name_en") or nutrient.get("name")
        if not isinstance(source_name, str):
            raise TypeError(f"Food {food.get('code', '<unknown>')} has unnamed nutrient.")
        normalized_name = normalize_text(source_name)
        value = decimal_string(nutrient.get("value"), negative_as_none=True)
        if value is None:
            continue

        primary_field = PRIMARY_NUTRIENT_FIELDS.get(normalized_name.casefold())
        if primary_field is not None:
            primary[primary_field] = value
            continue

        unit = nutrient.get("unit")
        if unit is not None and not isinstance(unit, str):
            raise TypeError(f"Food {food.get('code', '<unknown>')} has invalid nutrient unit.")
        if normalized_name in other:
            raise ValueError(
                f"Food {food.get('code', '<unknown>')} repeats nutrient {normalized_name!r}."
            )
        other[normalized_name] = {
            "value": value,
            "unit": normalize_text(unit) if unit else None,
        }
    return primary, other


def master_row(
    name: str,
    category_uuid: str,
    nutrition: dict[str, str | None] | None = None,
    other_nutrients: dict[str, object] | None = None,
) -> dict[str, Any]:
    """Build the exact database contract for one master ingredient."""
    values = nutrition or {
        "calories": None,
        "protein_g": None,
        "fat_g": None,
        "carbs_g": None,
        "sugar_g": None,
        "sodium_mg": None,
    }
    return {
        "id": master_ingredient_id(category_uuid, name),
        "name": name,
        "description": None,
        "category_id": category_uuid,
        "default_media_url": None,
        "canonical_unit": "GRAM",
        "calories": values["calories"],
        "protein_g": values["protein_g"],
        "fat_g": values["fat_g"],
        "carbs_g": values["carbs_g"],
        "sugar_g": values["sugar_g"],
        "sodium_mg": values["sodium_mg"],
        "other_nutrients": other_nutrients or {},
        "default_storage_mode": None,
        "is_verified": True,
    }


def add_master_candidate(
    candidates: dict[tuple[str, str], tuple[int, dict[str, Any]]],
    row: dict[str, Any],
    priority: int,
) -> None:
    """Keep the most trustworthy row for one database natural key."""
    key = (str(row["category_id"]), str(row["name"]).casefold())
    existing = candidates.get(key)
    if existing is None or priority < existing[0]:
        candidates[key] = (priority, row)


def transform_master_ingredients(
    food_rows: Iterable[dict[str, Any]],
    recipe_ingredient_rows: Iterable[dict[str, Any]],
    category_ids: dict[str, str],
    qwen_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Create verified masters from nutrition, reviewed Qwen, coded, and clean names."""
    candidates: dict[tuple[str, str], tuple[int, dict[str, Any]]] = {}
    nutrition_ids_by_code: dict[str, str] = {}
    recipe_rows = list(recipe_ingredient_rows)
    unclassified_id = category_ids[UNCLASSIFIED_CATEGORY.casefold()]

    for food in sorted(food_rows, key=lambda row: str(row.get("code", ""))):
        code = food.get("code")
        raw_name = food.get("name_vi")
        raw_category = food.get("category")
        if (
            not isinstance(code, str)
            or not isinstance(raw_name, str)
            or not isinstance(raw_category, str)
        ):
            raise TypeError("Nutrition food rows require string code, name_vi, and category.")
        name = normalize_text(raw_name)
        category_name = normalize_text(raw_category)
        if not (2 <= len(name) <= 120 and any(character.isalpha() for character in name)):
            raise ValueError(f"Nutrition food {code} has an invalid name: {name!r}")
        category_uuid = category_ids.get(category_name.casefold())
        if category_uuid is None:
            raise ValueError(f"Nutrition food {code} has an unknown category: {category_name!r}")
        nutrition, other_nutrients = nutrition_values(food)
        row = master_row(name, category_uuid, nutrition, other_nutrients)
        add_master_candidate(candidates, row, priority=0)
        nutrition_ids_by_code[code] = row["id"]

    code_ids: dict[str, str] = {}
    coded_rows = sorted(
        recipe_rows,
        key=lambda row: (
            str(row.get("master_ingredient_code", "")),
            str(row.get("master_ingredient_name", "")),
        ),
    )
    for recipe_ingredient in coded_rows:
        code = recipe_ingredient.get("master_ingredient_code")
        if not isinstance(code, str) or not code:
            continue
        if recipe_ingredient.get("match_method") == QWEN_MATCH_METHOD:
            continue
        if code in code_ids:
            continue
        if code in nutrition_ids_by_code:
            code_ids[code] = nutrition_ids_by_code[code]
            continue
        raw_name = recipe_ingredient.get("master_ingredient_name")
        if not isinstance(raw_name, str):
            raise TypeError(f"Coded ingredient {code} has no master name.")
        name = normalize_text(raw_name)
        if not is_valid_master_name(name):
            continue
        row = master_row(name, unclassified_id)
        add_master_candidate(candidates, row, priority=1)
        code_ids[code] = str(row["id"])

    known_ids_by_name: dict[str, set[str]] = {}
    for _, row in candidates.values():
        known_ids_by_name.setdefault(str(row["name"]).casefold(), set()).add(str(row["id"]))

    for recipe_ingredient in recipe_rows:
        if recipe_ingredient.get("match_method") != QWEN_MATCH_METHOD:
            continue
        qwen_name = qwen_extracted_name(recipe_ingredient, qwen_map)
        if qwen_name is None or not is_valid_master_name(qwen_name):
            continue
        name = qwen_name
        known_ids = known_ids_by_name.get(name.casefold(), set())
        if len(known_ids) == 1:
            continue
        derived_name = display_name(name)
        row = master_row(derived_name, unclassified_id)
        add_master_candidate(candidates, row, priority=2)
        known_ids_by_name.setdefault(name.casefold(), set()).add(str(row["id"]))

    for recipe_ingredient in recipe_rows:
        if recipe_ingredient.get("match_method") not in TRUSTED_ALIAS_METHODS:
            continue
        code = recipe_ingredient.get("master_ingredient_code")
        master_uuid = code_ids.get(code) if isinstance(code, str) else None
        raw_alias = recipe_ingredient.get("cleaned_name")
        if master_uuid is None or not isinstance(raw_alias, str):
            continue
        alias = normalize_text(raw_alias)
        if is_valid_master_name(alias):
            known_ids_by_name.setdefault(alias.casefold(), set()).add(master_uuid)

    for recipe_ingredient in recipe_rows:
        code = recipe_ingredient.get("master_ingredient_code")
        if isinstance(code, str) and code:
            continue
        if recipe_ingredient.get("match_method") == QWEN_MATCH_METHOD:
            qwen_name = qwen_extracted_name(recipe_ingredient, qwen_map)
            if qwen_name is None:
                continue
            name = qwen_name
        else:
            raw_name = recipe_ingredient.get("cleaned_name")
            if not isinstance(raw_name, str):
                raise TypeError("Uncoded recipe ingredient has no cleaned_name.")
            name = normalize_text(raw_name)
        if not is_valid_master_name(name):
            continue
        known_ids = known_ids_by_name.get(name.casefold(), set())
        if len(known_ids) == 1:
            continue
        derived_name = display_name(name)
        row = master_row(derived_name, unclassified_id)
        add_master_candidate(candidates, row, priority=2)
        known_ids_by_name.setdefault(name.casefold(), set()).add(row["id"])

    rows = [row for _, row in candidates.values()]
    rows.sort(key=lambda row: str(row["id"]))
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Normalized master ingredient IDs are not unique.")
    return rows


def run_transform_master_ingredients(
    food_input: Path,
    recipe_ingredients_input: Path,
    categories_input: Path,
    qwen_map_input: Path,
    output_path: Path,
) -> None:
    """Transform and write master ingredients."""
    category_ids = category_ids_by_name(
        load_json_rows(categories_input, "ingredient_categories.json")
    )
    rows = transform_master_ingredients(
        load_food_rows(food_input),
        load_json_rows(recipe_ingredients_input, "canonical_recipe_ingredients.json"),
        category_ids,
        load_qwen_extracted_map(qwen_map_input),
    )
    write_json(output_path, rows)
    print(f"Wrote {len(rows)} master ingredients to {output_path}")


def parse_args() -> argparse.Namespace:
    """Parse master-ingredient transform options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--food-input", type=Path, default=DEFAULT_FOOD_INPUT)
    parser.add_argument(
        "--recipe-ingredients-input",
        type=Path,
        default=DEFAULT_RECIPE_INGREDIENT_INPUT,
    )
    parser.add_argument("--categories-input", type=Path, default=DEFAULT_CATEGORY_OUTPUT)
    parser.add_argument("--qwen-map-input", type=Path, default=DEFAULT_QWEN_MAP_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_MASTER_OUTPUT)
    return parser.parse_args()


def main() -> None:
    """Run the master-ingredient transformation."""
    args = parse_args()
    run_transform_master_ingredients(
        args.food_input,
        args.recipe_ingredients_input,
        args.categories_input,
        args.qwen_map_input,
        args.output,
    )


if __name__ == "__main__":
    main()
