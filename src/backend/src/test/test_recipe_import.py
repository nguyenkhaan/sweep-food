"""Unit tests for recipe normalization."""

from scripts.recipe_import import transform_recipes


def test_transform_recipes_uses_fallback_description_and_empty_steps() -> None:
    """Hashtag descriptions and missing steps remain database-valid."""
    rows = transform_recipes(
        [
            {
                "id": "000f5f77-b69f-47f9-90a3-a0ca3b57d86f",
                "name": "  Canh chua  ",
                "source_platform": "Cookpad",
                "source_url": "HTTPS://EXAMPLE.TEST/recipe/#section",
                "default_servings": "2.0",
                "estimated_cooking_minutes": "30",
                "cooking_method": "Nấu",
                "dish_type": "Món canh",
                "diet_tags": "Gia đình; Gia đình;  Ăn chay ",
                "total_calories": "100.5",
                "total_protein_g": "4",
                "total_fat_g": "2",
                "total_carbs_g": "16",
            },
        ],
        [
            {
                "id": "000f5f77-b69f-47f9-90a3-a0ca3b57d86f",
                "incomplete_flag": 0,
                "nutrition_anomaly_flag": 1,
                "total_sugar_g": 3.6,
                "total_sodium_mg": 57.4,
                "total_fiber_g": 7.1,
            },
        ],
        [
            {
                "source_url": "https://example.test/recipe",
                "description": "#monngon #canhchua",
                "instructions": [],
                "media_url": "",
            },
        ],
    )

    assert len(rows) == 1
    recipe = rows[0]
    assert recipe["source_url"] == "https://example.test/recipe"
    assert (
        recipe["description"]
        == "Món canh Canh chua chế biến theo phương pháp Nấu, phù hợp cho 2 khẩu phần."
    )
    assert recipe["instructions"] == {"steps": []}
    assert recipe["media_url"] is None
    assert recipe["default_servings"] == "2.000"
    assert recipe["nutrition_status"] == "PARTIAL"
    assert recipe["total_sugar_g"] == "3.600"
    assert recipe["other_nutrients"] == {"sodium_mg": 57.4, "fiber_g": 7.1}
    assert recipe["tags"]["diet"] == ["Gia đình", "Ăn chay"]


def test_transform_recipes_marks_missing_aggregate_as_incomplete() -> None:
    """A canonical recipe without aggregate nutrition remains importable."""
    rows = transform_recipes(
        [
            {
                "id": "000f5f77-b69f-47f9-90a3-a0ca3b57d86f",
                "name": "Canh chua",
                "source_platform": "Cookpad",
                "source_url": "https://example.test/recipe",
                "default_servings": 2,
                "estimated_cooking_minutes": 30,
            }
        ],
        [],
        [
            {
                "source_url": "https://example.test/recipe",
                "description": "Canh chua",
                "instructions": [],
            }
        ],
    )

    assert rows[0]["nutrition_status"] == "INCOMPLETE"
    assert rows[0]["total_sugar_g"] is None
    assert rows[0]["other_nutrients"] == {}
