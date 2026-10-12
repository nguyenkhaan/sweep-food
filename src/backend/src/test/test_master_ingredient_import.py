"""Unit tests for master-ingredient normalization."""

from scripts.ingredient_category_import import transform_categories
from scripts.master_ingredient_import import (
    category_ids_by_name,
    transform_master_ingredients,
)


def test_transform_master_ingredients_uses_reviewed_qwen_extractions() -> None:
    """Reviewed Qwen names supersede their crawler-provided master code."""
    categories = transform_categories(
        [
            {"code": "100", "category_vi": "Rau"},
        ]
    )
    rows = transform_master_ingredients(
        [
            {
                "code": "100",
                "name_vi": "Cà chua",
                "category_vi": "Rau",
                "energy_kcal": "18",
                "protein_g": "0.9",
                "fat_g": "0.2",
                "carbs_g": "-0.03",
                "sugar_g": "2.6",
                "sodium_mg": "5",
                "fiber_g": "1.2",
                "calcium_mg": "10",
            },
            {
                "code": "101",
                "name_vi": "Cà chua",
                "category_vi": "Rau",
                "energy_kcal": "20",
                "protein_g": "1",
                "fat_g": "0.3",
                "carbs_g": "4",
                "sugar_g": "2.5",
                "sodium_mg": "4",
                "fiber_g": "1.1",
                "calcium_mg": "9",
            },
        ],
        [
            {
                "master_ingredient_code": "100",
                "master_ingredient_name": "Cà chua",
                "cleaned_name": "cà chua",
            },
            {
                "master_ingredient_code": "external-1",
                "master_ingredient_name": "Nước tương",
                "cleaned_name": "xì dầu",
                "match_method": "PRESET_ALIAS_MATCH",
            },
            {
                "master_ingredient_code": "",
                "master_ingredient_name": "",
                "cleaned_name": "xì dầu",
            },
            {
                "master_ingredient_code": "",
                "master_ingredient_name": "",
                "cleaned_name": "hành lá",
            },
            {
                "master_ingredient_code": "3025",
                "master_ingredient_name": "Đậu phụ",
                "cleaned_name": "mì căn",
                "raw_text": "Mì căn 100 g",
                "match_method": "QWEN_LLM_MATCH",
            },
            {
                "master_ingredient_code": "4019",
                "master_ingredient_name": "Hành hoa, tươi",
                "cleaned_name": "dầu hành lá",
                "raw_text": "Dầu hành lá",
                "match_method": "QWEN_LLM_MATCH",
            },
            {
                "master_ingredient_code": "",
                "master_ingredient_name": "",
                "cleaned_name": "vừa đủ",
            },
        ],
        category_ids_by_name(categories),
        {
            "Mì căn 100 g": "mì căn",
            "Dầu hành lá": "không có nguyên liệu cụ thể",
        },
    )

    by_name = {row["name"]: row for row in rows}
    assert set(by_name) == {
        "Cà chua",
        "Cà chua (101)",
        "Dầu hành lá",
        "Hành lá",
        "Mì căn",
        "Nước tương",
        "Vừa đủ",
    }
    assert "Đậu phụ" not in by_name
    assert by_name["Cà chua"]["calories"] == "18.000"
    assert by_name["Cà chua"]["protein_g"] == "0.900"
    assert by_name["Cà chua"]["fat_g"] == "0.200"
    assert by_name["Cà chua"]["sodium_mg"] == "5.000"
    assert by_name["Cà chua"]["sugar_g"] == "2.600"
    assert by_name["Cà chua"]["carbs_g"] is None
    assert by_name["Cà chua"]["other_nutrients"] == {
        "fiber_g": {"value": "1.200", "unit": "g"},
        "calcium_mg": {"value": "10.000", "unit": "mg"},
    }
    assert by_name["Cà chua (101)"]["calories"] == "20.000"
    assert all(row["is_verified"] is True for row in rows)
