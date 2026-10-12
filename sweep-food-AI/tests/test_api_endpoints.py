import pytest
from fastapi.testclient import TestClient

from web.app import (
    app,
    has_animal_ingredients,
    has_excluded_ingredients,
    has_gout_forbidden_ingredients,
    recipe_ings_map,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_autocomplete_endpoint(client):
    """Test /api/autocomplete returns valid results."""
    # Test non-empty query
    resp = client.get("/api/autocomplete?q=thịt")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) > 0
    assert any("thịt" in it["name"].lower() for it in data["results"])

    # Test empty query returns default list
    resp_empty = client.get("/api/autocomplete?q=")
    assert resp_empty.status_code == 200
    data_empty = resp_empty.json()
    assert len(data_empty["results"]) == 25


def test_presets_endpoint(client):
    """Test /api/presets returns valid response."""
    resp = client.get("/api/presets")
    assert resp.status_code == 200
    data = resp.json()
    assert "presets" in data


def test_recommend_endpoint_accuracy(client):
    """Test /api/recommend with realistic Vietnamese pantry items."""
    payload = {
        "items": [
            {"name": "thịt ba rọi", "quantity_g": 300, "hours_to_expire": 24},
            {"name": "đậu bắp", "quantity_g": 100, "hours_to_expire": 48},
            {"name": "cà chua", "quantity_g": 150, "hours_to_expire": 72}
        ],
        "household_size": 4,
        "max_cooking_time_min": 45,
        "scenario_type": "custom"
    }

    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data.get("status") == "success"
    assert data["contract_version"] == "2"
    assert data["model_version"] == "lgbm-contextual-v1"
    assert data["catalog_revision"].startswith("sha256:")
    assert data["ranker_model"] == "LightGBM LambdaMART"
    assert set(data["timings"]) == {"total_ms", "candidate_ms", "ranker_ms"}
    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) > 0

    top_rec = recs[0]
    assert "name" in top_rec
    assert isinstance(top_rec["rank_score"], float)
    assert set(top_rec["ranking_features"]) == {
        "core_coverage",
        "core_missing_count",
        "secondary_coverage",
        "shopping_gap_items",
        "rescue_weight_g",
        "nutrition_confidence",
        "kcal_per_serving",
        "protein_per_serving",
        "prep_complexity",
    }
    assert "calories_total" in top_rec
    assert float(top_rec["calories_total"]) > 0
    assert "calories_per_serving" in top_rec
    assert float(top_rec["calories_per_serving"]) > 0
    assert "protein_g" in top_rec
    assert "fat_g" in top_rec
    assert "carbs_g" in top_rec
    assert "status_text" in top_rec
    assert "matched_ingredients" in top_rec
    assert "instructions" in top_rec
    assert "instructions_steps" in top_rec
    assert isinstance(top_rec["instructions_steps"], list)
    assert len(top_rec["instructions_steps"]) > 0
    assert "source_url" in top_rec
    assert top_rec["source_url"].startswith("http")


@pytest.mark.parametrize(
    ("scenario", "items", "forbidden"),
    [
        (
            "chay",
            [
                {"name": "đậu phụ", "quantity_g": 300, "hours_to_expire": 12},
                {"name": "cà chua", "quantity_g": 200, "hours_to_expire": 20},
            ],
            has_animal_ingredients,
        ),
        (
            "gout",
            [
                {"name": "cà chua", "quantity_g": 300, "hours_to_expire": 12},
                {"name": "rau muống", "quantity_g": 300, "hours_to_expire": 20},
            ],
            has_gout_forbidden_ingredients,
        ),
    ],
)
def test_safety_scenarios_remove_forbidden_recipes(client, scenario, items, forbidden):
    response = client.post(
        "/api/recommend",
        json={"items": items, "scenario_type": scenario},
    )

    recommendations = response.json()["recommendations"]
    assert response.status_code == 200
    assert recommendations
    assert all(not forbidden(recipe_ings_map[item["id"]]) for item in recommendations)


def test_multi_urgent_recommendations_rescue_multiple_items(client):
    response = client.post(
        "/api/recommend",
        json={
            "items": [
                {"name": "thịt ba rọi", "quantity_g": 300, "hours_to_expire": 6},
                {"name": "đậu phụ", "quantity_g": 300, "hours_to_expire": 8},
                {"name": "cà chua", "quantity_g": 200, "hours_to_expire": 12},
            ],
            "scenario_type": "custom",
        },
    )

    recommendations = response.json()["recommendations"]
    rescued = {name for item in recommendations for name in item["rescued_items"]}
    assert response.status_code == 200
    assert len(rescued) >= 2


def test_allergy_filter_matches_recipe_ingredient_boundaries():
    ingredients = [{"cleaned_name": "đậu phộng rang", "raw_text": "100g đậu phộng"}]

    assert has_excluded_ingredients(ingredients, ["đậu phộng"])
    assert not has_excluded_ingredients(ingredients, ["cá"])


def test_dynamic_serving_and_calorie_scaling(client):
    """Test dynamic scaling: 4-person recipe scales down ingredients and calories for 1 person."""
    items = [
        {"name": "thịt bò", "quantity_g": 150, "hours_to_expire": 48},
        {"name": "hành tây", "quantity_g": 100, "hours_to_expire": 48}
    ]

    # Query 1: Household size 4
    resp_4 = client.post("/api/recommend", json={
        "items": items,
        "household_size": 4,
        "max_cooking_time_min": 45,
        "scenario_type": "custom"
    })
    assert resp_4.status_code == 200
    data_4 = resp_4.json()
    recs_4 = data_4.get("recommendations", [])
    assert len(recs_4) > 0

    # Query 2: Household size 1
    resp_1 = client.post("/api/recommend", json={
        "items": items,
        "household_size": 1,
        "max_cooking_time_min": 45,
        "scenario_type": "custom"
    })
    assert resp_1.status_code == 200
    data_1 = resp_1.json()
    recs_1 = data_1.get("recommendations", [])
    assert len(recs_1) > 0

    # Map by recipe id
    map_4 = {r["id"]: r for r in recs_4}
    map_1 = {r["id"]: r for r in recs_1}

    common_ids = set(map_4.keys()) & set(map_1.keys())
    assert len(common_ids) > 0

    for r_id in common_ids:
        r4 = map_4[r_id]
        r1 = map_1[r_id]

        if r4.get("default_servings") == 4:
            # Scale factor should be 0.25
            assert r1.get("scale_factor") == 0.25
            assert r1.get("is_scaled") is True
            assert r4.get("scale_factor") == 1.0

            # Calories total should scale by ~0.25
            expected_cal_1 = round(r4["calories_total"] * 0.25, 1)
            assert abs(r1["calories_total"] - expected_cal_1) <= 0.5

            # Calories per serving must remain invariant
            assert abs(r1["calories_per_serving"] - r4["calories_per_serving"]) <= 0.2

            # Compare ingredient weights
            ings_4 = {ing["name"]: ing["required_g"] for ing in r4["matched_ingredients"] + r4["missing_ingredients"]}
            ings_1 = {ing["name"]: ing["required_g"] for ing in r1["matched_ingredients"] + r1["missing_ingredients"]}

            for ing_name in set(ings_4.keys()) & set(ings_1.keys()):
                w4 = ings_4[ing_name]
                w1 = ings_1[ing_name]
                assert abs(w1 - round(w4 * 0.25, 1)) <= 0.2

