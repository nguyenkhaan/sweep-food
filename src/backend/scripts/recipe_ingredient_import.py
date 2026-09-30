"""Transform canonical recipe ingredients into database-ready JSON."""

from __future__ import annotations

import argparse
import json
import unicodedata
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = PROJECT_ROOT / "data123/raw/recipes/canonical_recipe_ingredients.json"
DEFAULT_RECIPES_INPUT = PROJECT_ROOT / "data123/normalized/recipes.json"
DEFAULT_MASTERS_INPUT = PROJECT_ROOT / "data123/normalized/master_ingredients.json"
DEFAULT_CATEGORIES_INPUT = (
    PROJECT_ROOT / "data123/normalized/ingredient_categories.json"
)
DEFAULT_FOOD_INPUT = PROJECT_ROOT / "data123/raw/food_nutrition_raw.json"
DEFAULT_QWEN_MAP_INPUT = PROJECT_ROOT / "data123/raw/qwen_extracted_map.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data123/normalized/recipe_ingredients.json"
DEFAULT_REJECTIONS_OUTPUT = PROJECT_ROOT / "data123/normalized/rejected_records.json"
UNCLASSIFIED_CATEGORY = "Chưa phân loại"
QWEN_MATCH_METHOD = "QWEN_LLM_MATCH"
QWEN_NO_INGREDIENT = "không có nguyên liệu cụ thể"
TRUSTED_ALIAS_METHODS = {"PRESET_ALIAS_MATCH"}
VALID_UNITS = {"KG", "GRAM", "LITER", "ML", "PIECE", "PACK", "OTHER"}


def normalize_text(value: str) -> str:
    """Return NFC text with zero-width characters and excess whitespace removed."""
    return " ".join(unicodedata.normalize("NFC", value).replace("\u200b", "").split())


def display_name(name: str) -> str:
    """Match the spelling policy used by the master-ingredient transformer."""
    return f"{name[:1].upper()}{name[1:]}"


def is_valid_master_name(name: str) -> bool:
    """Accept every non-blank source name supported by the database model."""
    return bool(name)


def source_ingredient_name(
    row: dict[str, Any], qwen_map: dict[str, str], *, prefer_master: bool = False
) -> str:
    """Return the same lossless fallback name used by the master transformer."""
    if row.get("match_method") == QWEN_MATCH_METHOD:
        raw_text = row.get("raw_text")
        qwen_name = (
            qwen_map.get(normalize_text(raw_text))
            if isinstance(raw_text, str)
            else None
        )
        if qwen_name and qwen_name.casefold() != QWEN_NO_INGREDIENT:
            return qwen_name
    fields = (
        ("master_ingredient_name", "cleaned_name", "raw_text")
        if prefer_master
        else ("cleaned_name", "raw_text", "master_ingredient_name")
    )
    for field in fields:
        value = row.get(field)
        if isinstance(value, str) and (name := normalize_text(value)):
            return name
    source_id = row.get("id", "không xác định")
    return f"Nguyên liệu {source_id}"


def decimal_string(value: object, *, positive: bool = False) -> str | None:
    """Return a finite decimal at the database scale, or None for blank input."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid decimal value: {value!r}") from error
    if not decimal.is_finite() or decimal < 0 or (positive and decimal <= 0):
        raise ValueError(f"Invalid positive decimal value: {value!r}")
    return format(decimal.quantize(Decimal("0.001")), "f")


def load_rows(input_path: Path, label: str) -> list[dict[str, Any]]:
    """Load a JSON array of objects."""
    rows = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise TypeError(f"Expected {label} to contain an array of objects.")
    return rows


def load_food_rows(input_path: Path) -> list[dict[str, Any]]:
    """Load food rows from the nutrition API payload."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise TypeError(
            "Expected food_nutrition_raw.json to contain a data array of objects."
        )
    return rows


def uniquely_named_food_rows(
    food_rows: Iterable[dict[str, Any]],
) -> list[tuple[dict[str, Any], str]]:
    """Mirror the lossless food-name disambiguation used by the master transform."""
    result: list[tuple[dict[str, Any], str]] = []
    used_keys: set[tuple[str, str]] = set()
    codes: set[str] = set()
    for food in sorted(food_rows, key=lambda row: str(row.get("code", ""))):
        code, raw_name, raw_category = (
            food.get("code"),
            food.get("name_vi"),
            food.get("category"),
        )
        if (
            not isinstance(code, str)
            or not isinstance(raw_name, str)
            or not isinstance(raw_category, str)
        ):
            raise TypeError(
                "Nutrition food rows require string code, name_vi, and category."
            )
        if code in codes:
            raise ValueError(f"Duplicate nutrition food code: {code!r}")
        codes.add(code)
        name = normalize_text(raw_name)
        category_key = normalize_text(raw_category).casefold()
        key = (category_key, name.casefold())
        if key in used_keys:
            name = f"{name} ({code})"
            key = (category_key, name.casefold())
        if key in used_keys:
            raise ValueError(f"Cannot disambiguate nutrition food {code!r}.")
        used_keys.add(key)
        result.append((food, name))
    return result


def load_qwen_map(input_path: Path) -> dict[str, str]:
    """Load reviewed Qwen decisions keyed by normalized raw ingredient text."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Expected qwen_extracted_map.json to contain an object.")
    result: dict[str, str] = {}
    for raw_text, extracted_name in payload.items():
        if not isinstance(raw_text, str) or not isinstance(extracted_name, str):
            raise TypeError("Qwen extracted map requires string keys and values.")
        result[normalize_text(raw_text)] = normalize_text(extracted_name)
    return result


def category_ids_by_name(rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Index normalized category names and require the fallback category."""
    result: dict[str, str] = {}
    for row in rows:
        name, category_id = row.get("name"), row.get("id")
        if not isinstance(name, str) or not isinstance(category_id, str):
            raise TypeError("Normalized category rows require string id and name.")
        key = normalize_text(name).casefold()
        if key in result:
            raise ValueError(f"Duplicate category name: {name!r}")
        result[key] = category_id
    if UNCLASSIFIED_CATEGORY.casefold() not in result:
        raise ValueError("Normalized categories must include 'Chưa phân loại'.")
    return result


def master_indexes(
    rows: Iterable[dict[str, Any]],
) -> tuple[set[str], dict[tuple[str, str], str], dict[str, set[str]]]:
    """Build ID, natural-key, and name indexes for approved master output."""
    ids: set[str] = set()
    natural: dict[tuple[str, str], str] = {}
    names: dict[str, set[str]] = {}
    for row in rows:
        master_id, name, category_id = (
            row.get("id"),
            row.get("name"),
            row.get("category_id"),
        )
        if (
            not isinstance(master_id, str)
            or not isinstance(name, str)
            or not isinstance(category_id, str)
        ):
            raise TypeError(
                "Normalized master rows require string id, name, and category_id."
            )
        UUID(master_id)
        key = (category_id, normalize_text(name).casefold())
        if master_id in ids or key in natural:
            raise ValueError("Normalized master IDs or natural keys are not unique.")
        ids.add(master_id)
        natural[key] = master_id
        names.setdefault(key[1], set()).add(master_id)
    return ids, natural, names


def food_master_ids(
    food_rows: Iterable[dict[str, Any]],
    category_ids: dict[str, str],
    masters_by_natural: dict[tuple[str, str], str],
) -> dict[str, str]:
    """Resolve nutrition codes to the exact master natural key generated in phase 2."""
    result: dict[str, str] = {}
    for food, name in uniquely_named_food_rows(food_rows):
        code = str(food["code"])
        category = str(food["category"])
        category_id = category_ids.get(normalize_text(category).casefold())
        master_id = (
            masters_by_natural.get((category_id, name.casefold()))
            if category_id is not None
            else None
        )
        if master_id is None:
            raise ValueError(f"Nutrition food {code} has no normalized master.")
        result[code] = master_id
    return result


def source_code_master_ids(
    rows: Iterable[dict[str, Any]],
    nutrition_ids: dict[str, str],
    unclassified_id: str,
    masters_by_natural: dict[tuple[str, str], str],
) -> dict[str, str]:
    """Mirror the coded-master identity selection from master_ingredient_import."""
    result: dict[str, str] = {}
    for row in sorted(
        rows,
        key=lambda value: (
            str(value.get("master_ingredient_code", "")),
            str(value.get("master_ingredient_name", "")),
        ),
    ):
        if row.get("match_method") == QWEN_MATCH_METHOD:
            continue
        code = row.get("master_ingredient_code")
        if not isinstance(code, str) or not code or code in result:
            continue
        if code in nutrition_ids:
            result[code] = nutrition_ids[code]
            continue
        normalized_name = source_ingredient_name(row, {}, prefer_master=True)
        master_id = masters_by_natural.get(
            (unclassified_id, normalized_name.casefold())
        )
        if master_id is not None:
            result[code] = master_id
    return result


def alias_master_ids(
    rows: Iterable[dict[str, Any]], code_ids: dict[str, str]
) -> dict[str, set[str]]:
    """Keep only unambiguous aliases supplied by the trusted preset matcher."""
    aliases: dict[str, set[str]] = {}
    for row in rows:
        if row.get("match_method") not in TRUSTED_ALIAS_METHODS:
            continue
        code, raw_alias = row.get("master_ingredient_code"), row.get("cleaned_name")
        master_id = code_ids.get(code) if isinstance(code, str) else None
        if master_id is None or not isinstance(raw_alias, str):
            continue
        alias = normalize_text(raw_alias)
        if is_valid_master_name(alias):
            aliases.setdefault(alias.casefold(), set()).add(master_id)
    return aliases


def resolve_master_id(
    row: dict[str, Any],
    code_ids: dict[str, str],
    aliases: dict[str, set[str]],
    masters_by_name: dict[str, set[str]],
    masters_by_natural: dict[tuple[str, str], str],
    unclassified_id: str,
    qwen_map: dict[str, str],
) -> tuple[str | None, str | None]:
    """Resolve one source row to an existing master, never creating an FK on the fly."""
    if row.get("match_method") == QWEN_MATCH_METHOD:
        raw_text = row.get("raw_text")
        name = (
            qwen_map.get(normalize_text(raw_text))
            if isinstance(raw_text, str)
            else None
        )
        if name is None:
            return None, "MISSING_MASTER_NAME"
        if name.casefold() == QWEN_NO_INGREDIENT:
            name = source_ingredient_name(row, qwen_map)
    else:
        code = row.get("master_ingredient_code")
        if isinstance(code, str) and code:
            master_id = code_ids.get(code)
            return (master_id, None) if master_id else (None, "MISSING_MASTER")
        raw_name = row.get("cleaned_name")
        name = normalize_text(raw_name) if isinstance(raw_name, str) else ""
        if not is_valid_master_name(name):
            name = source_ingredient_name(row, qwen_map)
        alias_ids = aliases.get(name.casefold(), set())
        if len(alias_ids) == 1:
            return next(iter(alias_ids)), None

    if not is_valid_master_name(name):
        return None, "MISSING_MASTER_NAME"
    master_ids = masters_by_name.get(name.casefold(), set())
    if len(master_ids) == 1:
        return next(iter(master_ids)), None
    preferred_id = masters_by_natural.get(
        (unclassified_id, display_name(name).casefold())
    )
    if preferred_id is not None:
        return preferred_id, None
    return None, "AMBIGUOUS_MASTER" if master_ids else "MISSING_MASTER"


def normalized_quantity(
    row: dict[str, Any],
) -> tuple[str | None, str | None, str | None]:
    """Prefer positive grams, then source quantity, then a schema-valid placeholder."""
    try:
        weight = decimal_string(row.get("estimated_weight_g"), positive=True)
    except ValueError:
        weight = None
    if weight is not None:
        return weight, "GRAM", None
    try:
        source_quantity = decimal_string(row.get("required_quantity"), positive=True)
    except ValueError:
        source_quantity = None
    if source_quantity is None:
        return "1.000", "OTHER", None
    source_unit = row.get("unit")
    if not isinstance(source_unit, str):
        return source_quantity, "OTHER", None
    unit = normalize_text(source_unit)
    return source_quantity, unit if unit in VALID_UNITS else "OTHER", None


def transform_recipe_ingredients(
    source_rows: Iterable[dict[str, Any]],
    recipe_rows: Iterable[dict[str, Any]],
    master_rows: Iterable[dict[str, Any]],
    category_rows: Iterable[dict[str, Any]],
    food_rows: Iterable[dict[str, Any]],
    qwen_map: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, object]]]:
    """Produce one FK-safe database row for every source recipe ingredient."""
    source = list(source_rows)
    recipe_ids = {
        row.get("id") for row in recipe_rows if isinstance(row.get("id"), str)
    }
    master_ids, masters_by_natural, masters_by_name = master_indexes(master_rows)
    category_ids = category_ids_by_name(category_rows)
    unclassified_id = category_ids[UNCLASSIFIED_CATEGORY.casefold()]
    nutrition_ids = food_master_ids(food_rows, category_ids, masters_by_natural)
    code_ids = source_code_master_ids(
        source, nutrition_ids, unclassified_id, masters_by_natural
    )
    aliases = alias_master_ids(source, code_ids)
    output: list[dict[str, Any]] = []
    rejections: list[dict[str, object]] = []

    for row in source:
        source_id, recipe_id = row.get("id"), row.get("recipe_id")
        if not isinstance(source_id, str) or not isinstance(recipe_id, str):
            raise TypeError("Recipe ingredient is missing id or recipe_id.")
        try:
            UUID(source_id)
            UUID(recipe_id)
        except ValueError as error:
            raise ValueError(
                f"Recipe ingredient {source_id!r} has an invalid UUID."
            ) from error
        if recipe_id not in recipe_ids:
            raise ValueError(
                f"Recipe ingredient {source_id} references an unknown recipe."
            )

        quantity, unit, quantity_error = normalized_quantity(row)
        if quantity_error:
            raise ValueError(f"Recipe ingredient {source_id} has {quantity_error}.")
        master_id, master_error = resolve_master_id(
            row,
            code_ids,
            aliases,
            masters_by_name,
            masters_by_natural,
            unclassified_id,
            qwen_map,
        )
        if master_error or master_id not in master_ids:
            reason = master_error or "MISSING_MASTER"
            raise ValueError(f"Recipe ingredient {source_id} has {reason}.")

        try:
            display_quantity = decimal_string(
                row.get("required_quantity"), positive=True
            )
        except ValueError:
            display_quantity = None
        display_unit = row.get("unit_vi")
        note = row.get("preparation_note")
        output.append(
            {
                "id": source_id,
                "recipe_id": recipe_id,
                "master_ingredient_id": master_id,
                "required_quantity": quantity,
                "unit": unit,
                "display_quantity": display_quantity,
                "display_unit": normalize_text(display_unit)
                if isinstance(display_unit, str) and normalize_text(display_unit)
                else None,
                "is_optional": False,
                "preparation_note": normalize_text(note)
                if isinstance(note, str) and normalize_text(note)
                else None,
            }
        )

    if len({row["id"] for row in output}) != len(output):
        raise ValueError("Normalized recipe ingredient IDs are not unique.")
    if any(row["recipe_id"] not in recipe_ids for row in output):
        raise ValueError("Normalized recipe ingredient has an unknown recipe.")
    if any(row["master_ingredient_id"] not in master_ids for row in output):
        raise ValueError("Normalized recipe ingredient has an unknown master.")
    output.sort(key=lambda row: str(row["id"]))
    return output, rejections


def write_json(
    output_path: Path, rows: list[dict[str, Any]] | list[dict[str, object]]
) -> None:
    """Write a complete JSON array atomically."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary_path.replace(output_path)


def parse_args() -> argparse.Namespace:
    """Parse recipe-ingredient transform options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--recipes-input", type=Path, default=DEFAULT_RECIPES_INPUT)
    parser.add_argument("--masters-input", type=Path, default=DEFAULT_MASTERS_INPUT)
    parser.add_argument(
        "--categories-input", type=Path, default=DEFAULT_CATEGORIES_INPUT
    )
    parser.add_argument("--food-input", type=Path, default=DEFAULT_FOOD_INPUT)
    parser.add_argument("--qwen-map-input", type=Path, default=DEFAULT_QWEN_MAP_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--rejections-output", type=Path, default=DEFAULT_REJECTIONS_OUTPUT
    )
    return parser.parse_args()


def main() -> None:
    """Run the recipe-ingredient transformation."""
    args = parse_args()
    rows, rejections = transform_recipe_ingredients(
        load_rows(args.input, "canonical_recipe_ingredients.json"),
        load_rows(args.recipes_input, "recipes.json"),
        load_rows(args.masters_input, "master_ingredients.json"),
        load_rows(args.categories_input, "ingredient_categories.json"),
        load_food_rows(args.food_input),
        load_qwen_map(args.qwen_map_input),
    )
    write_json(args.output, rows)
    write_json(args.rejections_output, rejections)
    print(f"Wrote {len(rows)} recipe ingredients and {len(rejections)} rejections")


if __name__ == "__main__":
    main()
