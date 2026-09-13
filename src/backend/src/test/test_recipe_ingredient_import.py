"""Unit tests for recipe-ingredient normalization."""

from scripts.recipe_ingredient_import import transform_recipe_ingredients


def test_transform_recipe_ingredients_resolves_trusted_and_reviewed_masters() -> None:
    """Weights, aliases, and Qwen review produce only valid foreign keys."""
    recipes = [{"id": "000f5f77-b69f-47f9-90a3-a0ca3b57d86f"}]
    categories = [
        {"id": "produce-id", "name": "Rau"},
        {"id": "unclassified-id", "name": "Chưa phân loại"},
    ]
    masters = [
        {"id": "e9f86a4c-cb2b-4a43-8f11-d6a6b3f7c01b", "name": "Cà chua", "category_id": "produce-id"},
        {"id": "03ad1d68-93a5-4293-8e39-2b7c2af04d6c", "name": "Nước tương", "category_id": "unclassified-id"},
        {"id": "bf5ad3e2-a390-444d-80c2-17f01f2f8e1e", "name": "Mì căn", "category_id": "unclassified-id"},
    ]
    source = [
        {
            "id": "7af23757-8525-4c03-b0d5-ebb52b4161a8",
            "recipe_id": recipes[0]["id"],
            "master_ingredient_code": "100",
            "master_ingredient_name": "Cà chua",
            "estimated_weight_g": "10",
            "required_quantity": "2",
            "unit": "MUONG_CA_PHE",
            "unit_vi": "muỗng cà phê",
            "preparation_note": " băm ",
        },
        {
            "id": "9537dca4-1ee7-4321-a301-2c446e2f0588",
            "recipe_id": recipes[0]["id"],
            "master_ingredient_code": "external-1",
            "master_ingredient_name": "Nước tương",
            "cleaned_name": "xì dầu",
            "match_method": "PRESET_ALIAS_MATCH",
            "estimated_weight_g": "1",
            "required_quantity": "1",
            "unit": "OTHER",
        },
        {
            "id": "a1e61db6-204f-40de-bee9-871fa149f799",
            "recipe_id": recipes[0]["id"],
            "cleaned_name": "xì dầu",
            "estimated_weight_g": "",
            "required_quantity": "0.5",
            "unit": "LAT_MIENG",
        },
        {
            "id": "ea6b4bd8-db85-46c0-b957-08384c8b6175",
            "recipe_id": recipes[0]["id"],
            "master_ingredient_code": "3025",
            "master_ingredient_name": "Đậu phụ",
            "raw_text": "Mì căn 100 g",
            "cleaned_name": "mì căn",
            "match_method": "QWEN_LLM_MATCH",
            "estimated_weight_g": "100",
            "required_quantity": "100",
            "unit": "GRAM",
        },
        {
            "id": "0c65bab7-f4ed-4205-9673-f289b062a9cf",
            "recipe_id": recipes[0]["id"],
            "raw_text": "Dầu hành lá",
            "match_method": "QWEN_LLM_MATCH",
            "estimated_weight_g": "2",
            "required_quantity": "2",
            "unit": "GRAM",
        },
        {
            "id": "0dec68e5-60d1-47e9-912a-4084ba092b27",
            "recipe_id": recipes[0]["id"],
            "cleaned_name": "muối",
            "estimated_weight_g": "",
            "required_quantity": "",
            "unit": "OTHER",
        },
    ]

    rows, rejections = transform_recipe_ingredients(
        source,
        recipes,
        masters,
        categories,
        [{"code": "100", "name_vi": "Cà chua", "category": "Rau"}],
        {"Mì căn 100 g": "mì căn", "Dầu hành lá": "không có nguyên liệu cụ thể"},
    )

    by_id = {row["id"]: row for row in rows}
    assert len(rows) == 4
    assert by_id["7af23757-8525-4c03-b0d5-ebb52b4161a8"]["required_quantity"] == "10.000"
    assert by_id["7af23757-8525-4c03-b0d5-ebb52b4161a8"]["unit"] == "GRAM"
    assert by_id["7af23757-8525-4c03-b0d5-ebb52b4161a8"]["preparation_note"] == "băm"
    assert by_id["a1e61db6-204f-40de-bee9-871fa149f799"]["unit"] == "OTHER"
    assert by_id["a1e61db6-204f-40de-bee9-871fa149f799"]["master_ingredient_id"] == masters[1]["id"]
    assert by_id["ea6b4bd8-db85-46c0-b957-08384c8b6175"]["master_ingredient_id"] == masters[2]["id"]
    assert {row["reason"] for row in rejections} == {
        "MISSING_USABLE_QUANTITY",
        "QWEN_NO_INGREDIENT",
    }
