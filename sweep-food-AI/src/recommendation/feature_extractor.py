"""3-Tier Observable Feature Extraction Architecture for Ablation Experiments.

Organizes observable, pre-decision signals into 3 strict tiers:
- Tier 1: X_raw (16 features) - Pure raw context and inventory signals without interactions/ratios.
- Tier 2: X_engineered (25 features) - X_raw + Jaccard similarity, overlap ratios, macro ratios.
- Tier 3: X_full (30 features) - X_engineered + domain context alignment (time diff, perishables, deficit).

All features are 100% available BEFORE recommendation decision and contain ZERO target proxy leakage.
"""

from __future__ import annotations

import re
from typing import Any
from src.recommendation.candidate_generator import extract_pantry_name_aliases

METHOD_MAP = {
    "Chiên/Rán": 0, "Xào": 1, "Kho": 2, "Canh/Súp": 3, "Nướng": 4,
    "Hấp": 5, "Luộc": 6, "Trộn/Gỏi": 7, "Pha chế": 8, "Ngâm/Muối chua": 9, "Khác": 10
}
DISH_TYPE_MAP = {
    "Món chính": 0, "Canh": 1, "Món khai vị / Gỏi": 2,
    "Món ăn vặt": 3, "Món tráng miệng": 4, "Đồ uống": 5
}

RAW_FEATURE_COLS = [
    "pantry_item_count",
    "pantry_min_expiry_hours",
    "household_size",
    "user_max_cooking_time",
    "cooking_time_min",
    "ingredients_count",
    "default_servings",
    "cooking_method_code",
    "dish_type_code",
    "total_calories",
    "total_protein_g",
    "total_fat_g",
    "total_carbs_g",
    "raw_matched_tokens_count",
    "raw_matched_weight_g",
    "raw_recipe_total_weight_g",
]

ENGINEERED_FEATURE_COLS = RAW_FEATURE_COLS + [
    "raw_jaccard_similarity",
    "raw_token_overlap_ratio",
    "raw_weight_ratio",
    "protein_energy_ratio",
    "calories_per_serving",
    "protein_g_per_serving",
    "fat_g_per_serving",
    "carbs_g_per_serving",
    "serving_size_diff",
]

FULL_FEATURE_COLS = ENGINEERED_FEATURE_COLS + [
    "time_feasibility_diff",
    "pantry_has_urgent_item",
    "pantry_perishable_count",
    "pantry_perishable_ratio",
    "raw_weight_deficit_g",
]


def _tokenize(text: str) -> set[str]:
    cleaned = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return {t for t in cleaned.split() if len(t) > 1}


def extract_all_features(
    pantry: dict[str, Any],
    recipe: dict[str, Any],
    recipe_ingredients: list[dict[str, Any]]
) -> dict[str, float]:
    """Extracts the full dictionary containing features for all 3 tiers."""
    pantry_items = pantry["items"]
    user_time_min = float(pantry.get("max_cooking_time_min", 45.0))
    household_size = float(pantry.get("household_size", 4.0))

    # Pantry signals
    pantry_count = len(pantry_items)
    perishable_count = sum(1 for it in pantry_items if not it.get("is_staple", False))
    known_expiry_hours = [
        float(it["hours_to_expire"])
        for it in pantry_items
        if it.get("hours_to_expire") is not None
    ]
    min_exp_h = min(known_expiry_hours, default=999.0)
    has_urgent = 1.0 if min_exp_h <= 24.0 else 0.0

    pantry_tokens = set()
    pantry_name_weights = {}
    pantry_code_weights = {}

    for it in pantry_items:
        n = (it.get("name") or "").strip().lower()
        c = it.get("code")
        w = float(it.get("quantity_g", 0.0))
        pantry_tokens.update(_tokenize(n))
        if n:
            aliases = extract_pantry_name_aliases(n)
            for a in aliases:
                pantry_tokens.update(_tokenize(a))
                pantry_name_weights[a] = max(pantry_name_weights.get(a, 0.0), w)
        if c:
            pantry_code_weights[str(c).strip()] = max(pantry_code_weights.get(str(c).strip(), 0.0), w)

    cook_time = float(recipe.get("estimated_cooking_minutes") or 30.0)
    try:
        raw_servings = float(recipe.get("default_servings") or 4.0)
        servings = raw_servings if raw_servings > 0 else 4.0
    except (ValueError, TypeError):
        servings = 4.0

    # Dynamic scaling factor: scales required ingredient weights to match target household size
    scale_factor = household_size / servings

    # Recipe signals
    recipe_tokens = set()
    total_recipe_w = 0.0
    matched_w = 0.0
    matched_token_cnt = 0

    for ing in recipe_ingredients:
        n = (ing.get("cleaned_name") or "").strip().lower()
        c = str(ing.get("master_ingredient_code")).strip() if ing.get("master_ingredient_code") else ""
        base_w = float(ing.get("estimated_weight_g") or 100.0)
        req_w = base_w * scale_factor
        total_recipe_w += req_w

        ing_toks = _tokenize(n)
        recipe_tokens.update(ing_toks)

        overlap = ing_toks & pantry_tokens
        if overlap:
            matched_token_cnt += len(overlap)

        avail_w = 0.0
        if c and c in pantry_code_weights:
            avail_w = pantry_code_weights[c]
        elif n and n in pantry_name_weights:
            avail_w = pantry_name_weights[n]
        else:
            ing_aliases = extract_pantry_name_aliases(n)
            for a in ing_aliases:
                if a in pantry_name_weights:
                    avail_w = max(avail_w, pantry_name_weights[a])
        matched_w += min(req_w, avail_w)

    tot_cal = float(recipe.get("total_calories") or 500.0)
    tot_p = float(recipe.get("total_protein_g") or 30.0)
    tot_f = float(recipe.get("total_fat_g") or 15.0)
    tot_c = float(recipe.get("total_carbs_g") or 50.0)
    method_code = float(METHOD_MAP.get(recipe.get("cooking_method", "Khác"), 10))
    dish_code = float(DISH_TYPE_MAP.get(recipe.get("dish_type", "Món chính"), 0))

    # Tier 1: Raw features
    raw_feats = {
        "pantry_item_count": float(pantry_count),
        "pantry_min_expiry_hours": float(min_exp_h),
        "household_size": household_size,
        "user_max_cooking_time": user_time_min,
        "cooking_time_min": cook_time,
        "ingredients_count": float(recipe.get("ingredients_count") or len(recipe_ingredients)),
        "default_servings": servings,
        "cooking_method_code": method_code,
        "dish_type_code": dish_code,
        "total_calories": tot_cal,
        "total_protein_g": tot_p,
        "total_fat_g": tot_f,
        "total_carbs_g": tot_c,
        "raw_matched_tokens_count": float(matched_token_cnt),
        "raw_matched_weight_g": round(matched_w, 1),
        "raw_recipe_total_weight_g": round(total_recipe_w, 1),
    }

    # Tier 2: Engineered ratios & similarity
    union_toks = recipe_tokens | pantry_tokens
    jaccard = len(recipe_tokens & pantry_tokens) / max(1, len(union_toks))
    overlap_ratio = matched_token_cnt / max(1, len(recipe_tokens))
    w_ratio = matched_w / max(1.0, total_recipe_w)
    pe_ratio = (4.0 * tot_p) / max(1.0, tot_cal)

    engineered_feats = {
        **raw_feats,
        "raw_jaccard_similarity": round(jaccard, 4),
        "raw_token_overlap_ratio": round(overlap_ratio, 4),
        "raw_weight_ratio": round(w_ratio, 4),
        "protein_energy_ratio": round(pe_ratio, 4),
        "calories_per_serving": round(tot_cal / max(1.0, servings), 1),
        "protein_g_per_serving": round(tot_p / max(1.0, servings), 1),
        "fat_g_per_serving": round(tot_f / max(1.0, servings), 1),
        "carbs_g_per_serving": round(tot_c / max(1.0, servings), 1),
        "serving_size_diff": round(servings - household_size, 1),
    }

    # Tier 3: Full domain features
    full_feats = {
        **engineered_feats,
        "time_feasibility_diff": round(user_time_min - cook_time, 1),
        "pantry_has_urgent_item": float(has_urgent),
        "pantry_perishable_count": float(perishable_count),
        "pantry_perishable_ratio": round(perishable_count / max(1, pantry_count), 4),
        "raw_weight_deficit_g": round(max(0.0, total_recipe_w - matched_w), 1),
    }

    return full_feats
