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
            {"code": "100", "category": "Rau"},
        ]
    )
    rows = transform_master_ingredients(
        [
            {
                "code": "100",
                "name_vi": "Cà chua",
                "category": "Rau",
                "energy": 18,
                "nutrition": [
                    {"name_en": "Protein", "value": 0.9, "unit": "g"},
                    {"name_en": "Na", "value": 5, "unit": "mg"},
                    {
                        "name_en": "Carbohydrate by difference",
                        "value": -0.03,
                        "unit": "g",
                    },
                ],
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
    assert set(by_name) == {"Cà chua", "Hành lá", "Mì căn", "Nước tương"}
    assert "Đậu phụ" not in by_name
    assert by_name["Cà chua"]["calories"] == "18.000"
    assert by_name["Cà chua"]["protein_g"] == "0.900"
    assert by_name["Cà chua"]["sodium_mg"] == "5.000"
    assert by_name["Cà chua"]["carbs_g"] is None
    assert all(row["is_verified"] is True for row in rows)
