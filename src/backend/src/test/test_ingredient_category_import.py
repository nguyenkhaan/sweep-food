"""Unit tests for ingredient-category normalization."""

from scripts.ingredient_category_import import transform_categories


def test_transform_categories_normalizes_and_deduplicates_names() -> None:
    """Category names share a stable record after text normalization."""
    rows = transform_categories(
        [
            {"code": "100", "category_vi": "  Rau\u200b,   củ  "},
            {"code": "101", "category_vi": "Rau, củ"},
            {"code": "102", "category_vi": "Thịt"},
        ]
    )

    assert [row["name"] for row in rows] == ["Chưa phân loại", "Rau, củ", "Thịt"]
    assert len({row["id"] for row in rows}) == 3
    assert all(isinstance(row["description"], str) for row in rows)
    assert all(len(row["description"].split()) < 30 for row in rows)
