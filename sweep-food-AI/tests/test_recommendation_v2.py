from src.recommendation.candidate_generator import CandidateGenerator
from src.recommendation.contextual_features import (
    FEATURE_COLS,
    extract_contextual_features,
)
from src.recommendation.life_scenarios import generate_life_pantry
from src.recommendation.pantry_resolver import (
    build_master_alias_index,
    get_effective_codes,
    resolve_pantry_items,
)


def test_resolver_adds_exact_alias_codes_without_replacing_explicit_code() -> None:
    index = build_master_alias_index(
        [
            {
                "code": "7001",
                "name_vi": "Thịt bò",
                "aliases": "bò; thịt bò tươi",
            },
            {
                "code": "7002",
                "name_vi": "Thịt bò",
                "aliases": "",
            },
        ]
    )

    resolved = resolve_pantry_items(
        [{"name": "  THỊT BÒ  ", "code": "custom-code"}],
        index,
    )

    assert resolved[0]["code"] == "custom-code"
    assert resolved[0]["resolved_codes"] == ["7001", "7002"]
    assert get_effective_codes(resolved[0]) == {"custom-code", "7001", "7002"}


def test_candidate_generator_retrieves_by_resolved_master_code() -> None:
    recipes = [{"id": "recipe-beef", "name": "Bò xào"}]
    ingredients = [
        {
            "recipe_id": "recipe-beef",
            "master_ingredient_code": "7001",
            "cleaned_name": "thịt bò",
            "ingredient_role": "core",
        }
    ]

    candidates = CandidateGenerator(recipes, ingredients).retrieve_candidates(
        [
            {
                "name": "bò tươi",
                "resolved_codes": ["7001"],
                "quantity_g": 300,
                "hours_to_expire": 12,
                "is_staple": False,
            }
        ]
    )

    assert [candidate["id"] for candidate in candidates] == ["recipe-beef"]


def test_contextual_features_follow_authoritative_order() -> None:
    pantry = {
        "household_size": 2,
        "items": [
            {
                "name": "thịt bò",
                "code": "7001",
                "quantity_g": 200,
                "hours_to_expire": 12,
                "is_staple": False,
            }
        ],
    }
    recipe = {
        "default_servings": 2,
        "calories_per_serving": 450,
        "protein_per_serving": 30,
        "nutrition_confidence": 0.9,
    }
    ingredients = [
        {
            "master_ingredient_code": "7001",
            "cleaned_name": "thịt bò",
            "ingredient_role": "core",
            "estimated_weight_g": 200,
        }
    ]

    features = extract_contextual_features(pantry, recipe, ingredients, steps=[])

    assert list(features) == FEATURE_COLS
    assert features["core_coverage"] == 1.0
    assert features["core_missing_count"] == 0.0
    assert features["rescue_weight_g"] == 200.0


def test_life_scenario_generation_is_deterministic() -> None:
    assert generate_life_pantry(7) == generate_life_pantry(7)
