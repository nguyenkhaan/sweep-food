"""Transform canonical recipe sources into recipes.json."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CANONICAL_INPUT = PROJECT_ROOT / "data/raw/recipes/canonical_recipes.json"
DEFAULT_NUTRITION_INPUT = PROJECT_ROOT / "data/raw/recipes/recipes.json"
DEFAULT_SCRAPED_INPUT = PROJECT_ROOT / "data/raw/recipes_raw_scraped.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/normalized/recipes.json"
NUTRITION_STATUSES = {"COMPLETE", "PARTIAL", "INCOMPLETE"}
HASHTAG_ONLY = re.compile(r"^\s*(#[^\s]+\s*)+$")


def normalize_text(value: str) -> str:
    """Return NFC text with zero-width characters and excess whitespace removed."""
    normalized = unicodedata.normalize("NFC", value).replace("\u200b", "")
    return " ".join(normalized.split())


def normalize_url(value: str) -> str:
    """Normalize a source URL without changing its path or query semantics."""
    parsed = urlsplit(normalize_text(value))
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid source URL: {value!r}")
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, ""))


def decimal_string(value: object, *, positive: bool = False) -> str | None:
    """Convert a finite source number to a fixed-scale decimal string."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid decimal value: {value!r}") from error
    if not decimal.is_finite() or decimal < 0 or (positive and decimal <= 0):
        raise ValueError(f"Invalid non-negative decimal value: {value!r}")
    return format(decimal.quantize(Decimal("0.001")), "f")


def cooking_minutes(value: object) -> int:
    """Convert a non-negative whole-minute source value to an integer."""
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid cooking minutes: {value!r}") from error
    if not decimal.is_finite() or decimal < 0 or decimal != decimal.to_integral_value():
        raise ValueError(f"Cooking minutes must be a non-negative integer: {value!r}")
    return int(decimal)


def normalized_tags(value: object) -> list[str]:
    """Split semicolon-separated diet tags and retain stable unique values."""
    if not isinstance(value, str):
        return []
    tags: list[str] = []
    seen: set[str] = set()
    for tag in value.split(";"):
        normalized = normalize_text(tag)
        if normalized and normalized.casefold() not in seen:
            tags.append(normalized)
            seen.add(normalized.casefold())
    return tags


def normalized_steps(value: object) -> dict[str, list[dict[str, object]]]:
    """Convert scraped instructions to the JSONB contract expected by recipes."""
    if not isinstance(value, list):
        raise TypeError("Scraped recipe instructions must be an array.")
    steps: list[dict[str, object]] = []
    for raw_step in value:
        if not isinstance(raw_step, dict):
            raise TypeError("Scraped recipe step must be an object.")
        content = raw_step.get("content")
        if not isinstance(content, str):
            raise TypeError("Scraped recipe step must contain string content.")
        normalized_content = normalize_text(content)
        if not normalized_content:
            continue
        title = raw_step.get("title")
        normalized_title = normalize_text(title) if isinstance(title, str) else ""
        step_number = len(steps) + 1
        steps.append(
            {
                "step_number": step_number,
                "title": normalized_title or f"Bước {step_number}",
                "content": normalized_content,
            }
        )
    return {"steps": steps}


def factual_description(
    name: str, dish_type: str | None, cooking_method: str | None, servings: str
) -> str:
    """Create a short non-promotional fallback when scraped description is unusable."""
    dish = dish_type or "Món ăn"
    method = f" theo phương pháp {cooking_method}" if cooking_method else ""
    servings_display = servings.rstrip("0").rstrip(".")
    return f"{dish} {name} chế biến{method}, phù hợp cho {servings_display} khẩu phần."


def load_rows(input_path: Path, label: str) -> list[dict[str, Any]]:
    """Load a JSON array of object records."""
    rows = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise TypeError(f"Expected {label} to contain an array of objects.")
    return rows


def scraped_by_url(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index scraped details by normalized source URL."""
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_url = row.get("source_url")
        if not isinstance(source_url, str):
            raise TypeError("Scraped recipe has no source_url.")
        key = normalize_url(source_url)
        if key in indexed:
            raise ValueError(f"Duplicate scraped source URL: {source_url!r}")
        indexed[key] = row
    return indexed


def nutrition_status_by_id(rows: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Index valid nutrition status by source recipe UUID."""
    statuses: dict[str, str] = {}
    for row in rows:
        recipe_id = row.get("id")
        status = row.get("nutrition_status")
        if not isinstance(recipe_id, str) or not isinstance(status, str):
            raise TypeError("Nutrition recipe requires string id and nutrition_status.")
        if status not in NUTRITION_STATUSES:
            raise ValueError(f"Invalid nutrition status for {recipe_id}: {status!r}")
        if recipe_id in statuses:
            raise ValueError(f"Duplicate nutrition recipe id: {recipe_id}")
        statuses[recipe_id] = status
    return statuses


def transform_recipes(
    canonical_rows: Iterable[dict[str, Any]],
    nutrition_rows: Iterable[dict[str, Any]],
    scraped_rows: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create database-ready recipes from canonical and scraped sources."""
    scraped_lookup = scraped_by_url(scraped_rows)
    nutrition_statuses = nutrition_status_by_id(nutrition_rows)
    output: list[dict[str, Any]] = []

    for canonical in canonical_rows:
        recipe_id = canonical.get("id")
        name = canonical.get("name")
        source_platform = canonical.get("source_platform")
        source_url = canonical.get("source_url")
        if (
            not isinstance(recipe_id, str)
            or not isinstance(name, str)
            or not isinstance(source_platform, str)
            or not isinstance(source_url, str)
        ):
            raise TypeError("Canonical recipe requires string id, name, source_platform, and source_url.")
        UUID(recipe_id)
        normalized_name = normalize_text(name)
        normalized_platform = normalize_text(source_platform)
        normalized_url = normalize_url(source_url)
        if not normalized_name or not normalized_platform:
            raise ValueError(f"Recipe {recipe_id} has a blank required text field.")
        scraped = scraped_lookup.get(normalized_url)
        if scraped is None:
            raise ValueError(f"Recipe {recipe_id} has no scraped detail.")
        nutrition_status = nutrition_statuses.get(recipe_id)
        if nutrition_status is None:
            raise ValueError(f"Recipe {recipe_id} has no nutrition status.")

        servings = decimal_string(canonical.get("default_servings"), positive=True)
        if servings is None:
            raise ValueError(f"Recipe {recipe_id} has no default_servings.")
        dish_type = canonical.get("dish_type")
        cooking_method = canonical.get("cooking_method")
        normalized_dish_type = normalize_text(dish_type) if isinstance(dish_type, str) else None
        normalized_cooking_method = (
            normalize_text(cooking_method) if isinstance(cooking_method, str) else None
        )
        raw_description = scraped.get("description")
        description = normalize_text(raw_description) if isinstance(raw_description, str) else ""
        if not description or HASHTAG_ONLY.fullmatch(description):
            description = factual_description(
                normalized_name,
                normalized_dish_type,
                normalized_cooking_method,
                servings,
            )
        media_url = scraped.get("media_url")
        if media_url is not None and not isinstance(media_url, str):
            raise TypeError(f"Recipe {recipe_id} has invalid media_url.")
        normalized_media_url = normalize_text(media_url) if media_url else None

        output.append(
            {
                "id": recipe_id,
                "name": normalized_name,
                "description": description,
                "instructions": normalized_steps(scraped.get("instructions")),
                "media_url": normalized_media_url,
                "source_platform": normalized_platform,
                "source_url": normalized_url,
                "default_servings": servings,
                "estimated_cooking_minutes": cooking_minutes(
                    canonical.get("estimated_cooking_minutes")
                ),
                "estimated_cost": None,
                "total_calories": decimal_string(canonical.get("total_calories")),
                "total_protein_g": decimal_string(canonical.get("total_protein_g")),
                "total_fat_g": decimal_string(canonical.get("total_fat_g")),
                "total_carbs_g": decimal_string(canonical.get("total_carbs_g")),
                "total_sugar_g": None,
                "other_nutrients": {},
                "nutrition_status": nutrition_status,
                "tags": {
                    "cooking_method": normalized_cooking_method,
                    "dish_type": normalized_dish_type,
                    "diet": normalized_tags(canonical.get("diet_tags")),
                },
            }
        )

    if len({row["id"] for row in output}) != len(output):
        raise ValueError("Normalized recipe IDs are not unique.")
    if len({str(row["name"]).casefold() for row in output}) != len(output):
        raise ValueError("Normalized recipe names are not unique.")
    if len({row["source_url"] for row in output}) != len(output):
        raise ValueError("Normalized recipe source URLs are not unique.")
    output.sort(key=lambda row: str(row["id"]))
    return output


def write_json(output_path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a complete JSON array atomically."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)


def parse_args() -> argparse.Namespace:
    """Parse recipe-transform options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-input", type=Path, default=DEFAULT_CANONICAL_INPUT)
    parser.add_argument("--nutrition-input", type=Path, default=DEFAULT_NUTRITION_INPUT)
    parser.add_argument("--scraped-input", type=Path, default=DEFAULT_SCRAPED_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    """Run the recipe transformation."""
    args = parse_args()
    rows = transform_recipes(
        load_rows(args.canonical_input, "canonical_recipes.json"),
        load_rows(args.nutrition_input, "recipes.json"),
        load_rows(args.scraped_input, "recipes_raw_scraped.json"),
    )
    write_json(args.output, rows)
    print(f"Wrote {len(rows)} recipes to {args.output}")


if __name__ == "__main__":
    main()
