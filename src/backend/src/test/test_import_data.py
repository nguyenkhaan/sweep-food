"""Unit tests for normalized catalog import validation."""

import json
from pathlib import Path

import pytest

from scripts.import_data import DataValidationError, build_catalog_data


def _write_json(path: Path, name: str, rows: list[dict[str, object]]) -> None:
    (path / name).write_text(json.dumps(rows), encoding="utf-8")


def _write_release(path: Path, master_id: str = "22222222-2222-4222-8222-222222222222") -> None:
    category_id = "11111111-1111-4111-8111-111111111111"
    recipe_id = "33333333-3333-4333-8333-333333333333"
    _write_json(
        path,
        "ingredient_categories.json",
        [{"id": category_id, "name": "Rau", "description": "Rau dùng trong bữa ăn."}],
    )
    _write_json(
        path,
        "master_ingredients.json",
        [
            {
                "id": master_id,
                "name": "Cà chua",
                "description": None,
                "category_id": category_id,
                "default_media_url": None,
                "canonical_unit": "GRAM",
                "calories": "18.000",
                "protein_g": None,
                "fat_g": None,
                "carbs_g": None,
                "sugar_g": None,
                "sodium_mg": None,
                "other_nutrients": {},
                "default_storage_mode": None,
                "is_verified": True,
            }
        ],
    )
    _write_json(
        path,
        "recipes.json",
        [
            {
                "id": recipe_id,
                "name": "Canh chua",
                "description": "Canh chua cà chua.",
                "instructions": {"steps": []},
                "media_url": None,
                "source_platform": "example",
                "source_url": "https://example.test/canh-chua",
                "default_servings": "2.000",
                "estimated_cooking_minutes": 20,
                "estimated_cost": None,
                "total_calories": None,
                "total_protein_g": None,
                "total_fat_g": None,
                "total_carbs_g": None,
                "total_sugar_g": None,
                "other_nutrients": {},
                "nutrition_status": "INCOMPLETE",
                "tags": {},
            }
        ],
    )
    _write_json(
        path,
        "recipe_ingredients.json",
        [
            {
                "id": "44444444-4444-4444-8444-444444444444",
                "recipe_id": recipe_id,
                "master_ingredient_id": master_id,
                "required_quantity": "100.000",
                "unit": "GRAM",
                "display_quantity": "1.000",
                "display_unit": "quả",
                "is_optional": False,
                "preparation_note": None,
            }
        ],
    )


def test_build_catalog_data_converts_database_values(tmp_path: Path) -> None:
    """A valid release has UUID and Decimal values ready for PostgreSQL."""
    _write_release(tmp_path)

    data = build_catalog_data(tmp_path)

    assert len(data.categories) == len(data.masters) == len(data.recipes) == 1
    assert len(data.recipe_ingredients) == 1
    assert str(data.recipe_ingredients[0]["required_quantity"]) == "100.000"


def test_build_catalog_data_rejects_orphan_master(tmp_path: Path) -> None:
    """No import begins when a normalized foreign key is missing."""
    _write_release(tmp_path, master_id="55555555-5555-4555-8555-555555555555")
    recipe_ingredients_path = tmp_path / "recipe_ingredients.json"
    rows = json.loads(recipe_ingredients_path.read_text(encoding="utf-8"))
    rows[0]["master_ingredient_id"] = "22222222-2222-4222-8222-222222222222"
    recipe_ingredients_path.write_text(json.dumps(rows), encoding="utf-8")

    with pytest.raises(DataValidationError, match="unknown foreign key"):
        build_catalog_data(tmp_path)
