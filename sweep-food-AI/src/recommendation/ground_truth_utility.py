"""Ground-Truth Latent Human Utility & Multi-Objective Preference Generator.

Simulates authentic Vietnamese human satisfaction and meal acceptance completely
independently of the feature extraction pipeline (Strict Zero-Coupling).

Human Utility Model:
U = w_feasibility * FeasibilityScore
  + w_time * TimeConvenienceScore
  + w_role * CulturalRoleHarmony
  + w_waste * ZeroWasteSatisfaction
  + w_nutrition * NutritionBalance
  + epsilon_taste (Stochastic human preference variation ~ N(0, sigma^2))

Output:
Discretized Relevance Label y in {0, 1, 2, 3}:
- 3: Optimal Zero-Waste Hero (rescuing urgent food, delicious, fully feasible)
- 2: Highly Satisfying Home Meal (ready to cook, good fit for dinner)
- 1: Marginal Match (acceptable with compromises / minor shopping)
- 0: Infeasible / Rejected (missing vital core proteins, takes way too long, or disliked)
"""

from __future__ import annotations

import random
from typing import Any

# Domain definitions for culinary satisfaction
CORE_PROTEIN_KEYWORDS = {
    "thịt heo", "thịt bò", "thịt gà", "thịt lợn", "ba chỉ", "sườn", "sườn heo", "sườn non",
    "cá", "cá lóc", "cá chép", "cá hồi", "cá basa", "cá nục", "cá thu", "cá rô",
    "tôm", "tôm sú", "mực", "cua", "ếch", "trứng", "trứng gà", "trứng vịt", "đậu phụ", "đậu hũ"
}

CORE_PRODUCE_KEYWORDS = {
    "rau muống", "bắp cải", "cải thảo", "cải ngọt", "cải thìa", "mồng tơi", "rau đay", "rau ngót",
    "cà chua", "dưa leo", "dưa chuột", "bầu", "bí xanh", "bí đỏ", "mướp", "khổ qua",
    "dọc mùng", "bạc hà", "súp lơ", "bông cải", "nấm", "nấm rơm", "nấm đùi gà", "nấm kim châm"
}

STAPLE_KEYWORDS = {
    "muối", "đường", "nước mắm", "hạt nêm", "tiêu", "dầu ăn", "tỏi", "hành tím", "hành lá", "ớt"
}


def _is_keyword_match(name: str, kw_set: set[str]) -> bool:
    clean_n = (name or "").strip().lower()
    return any(kw in clean_n for kw in kw_set)


def compute_ground_truth_utility(
    pantry: dict[str, Any],
    recipe: dict[str, Any],
    recipe_ingredients: list[dict[str, Any]],
    add_stochastic_noise: bool = True
) -> tuple[float, int]:
    """Computes latent human utility U and returns (utility_score, relevance_grade_y).

    Completely isolated from feature extraction.
    """
    pantry_items = pantry["items"]
    user_time_min = float(pantry.get("max_cooking_time_min", 45.0))
    household_size = float(pantry.get("household_size") or 4.0)
    try:
        raw_servings = float(recipe.get("default_servings") or 4.0)
        default_servings = raw_servings if raw_servings > 0 else 4.0
    except (ValueError, TypeError):
        default_servings = 4.0
    scale_factor = household_size / default_servings

    # Fast inventory lookup
    pantry_by_code = {it.get("code"): it for it in pantry_items if it.get("code")}
    pantry_by_name = {(it.get("name") or "").strip().lower(): it for it in pantry_items if it.get("name")}

    # 1. Culinary Feasibility Assessment
    missing_core_protein = 0
    missing_core_produce = 0
    rescued_urgent_items = 0
    ingredient_satisfaction_scores = []

    for ing in recipe_ingredients:
        c = ing.get("master_ingredient_code")
        n = (ing.get("cleaned_name") or "").strip().lower()
        base_g = float(ing.get("estimated_weight_g") or 100.0)
        req_g = base_g * scale_factor

        # Check if staple, protein, or produce
        is_staple = _is_keyword_match(n, STAPLE_KEYWORDS)
        is_protein = _is_keyword_match(n, CORE_PROTEIN_KEYWORDS)
        is_produce = _is_keyword_match(n, CORE_PRODUCE_KEYWORDS)

        p_item = pantry_by_code.get(c) or pantry_by_name.get(n)
        avail_g = float(p_item["quantity_g"]) if p_item else 0.0

        ratio = avail_g / max(1.0, req_g)

        # Human perceived sufficiency curve
        if is_staple:
            suff_score = 1.0 if (avail_g > 0 or p_item is None) else 0.9  # Staples are forgiving
        elif is_produce:
            # Vegetables: 50% morning glory is very usable (score ~ 0.88)
            if ratio >= 0.80:
                suff_score = 1.0
            elif ratio >= 0.40:
                suff_score = 0.85 + 0.15 * ((ratio - 0.40) / 0.40)
            else:
                suff_score = 0.85 * (ratio / 0.40)
            if ratio < 0.25:
                missing_core_produce += 1
        elif is_protein:
            # Proteins: less elastic (meat needs at least 50-60%)
            if ratio >= 0.85:
                suff_score = 1.0
            elif ratio >= 0.50:
                suff_score = 0.75 + 0.25 * ((ratio - 0.50) / 0.35)
            else:
                suff_score = 0.75 * (ratio / 0.50)
            if ratio < 0.35:
                missing_core_protein += 1
        else:
            suff_score = min(1.0, ratio)

        ingredient_satisfaction_scores.append(suff_score)

        if p_item and float(p_item.get("hours_to_expire", 999.0)) <= 24.0 and not p_item.get("is_staple", False):
            rescued_urgent_items += 1

    avg_ingredient_suff = (
        sum(ingredient_satisfaction_scores) / len(ingredient_satisfaction_scores)
        if ingredient_satisfaction_scores else 0.0
    )

    feasibility_score = max(
        0.0,
        avg_ingredient_suff - 0.50 * missing_core_protein - 0.25 * missing_core_produce
    )

    # 2. Time Convenience Penalty
    cook_time = float(recipe.get("estimated_cooking_minutes") or 30.0)
    time_penalty = 0.0
    if cook_time > user_time_min:
        time_over = cook_time - user_time_min
        time_penalty = min(1.0, time_over / 30.0)

    # 3. Cultural & Meal Role Harmony
    dish_type = recipe.get("dish_type", "Món chính")
    if dish_type in ("Món chính", "Canh"):
        role_harmony = 1.0
    elif dish_type == "Món khai vị / Gỏi":
        role_harmony = 0.7
    else:  # Đồ uống, tráng miệng, ăn vặt
        role_harmony = 0.3

    # 4. Nutritional Balance
    tot_cal = float(recipe.get("total_calories") or 500.0)
    tot_p = float(recipe.get("total_protein_g") or 30.0)
    pe_ratio = (4.0 * tot_p) / max(1.0, tot_cal)
    nutrition_score = min(1.0, pe_ratio / 0.25)

    # 5. Composite Latent Utility U
    latent_utility = (
        0.40 * feasibility_score
        + 0.20 * (1.0 - time_penalty)
        + 0.15 * role_harmony
        + 0.15 * (1.0 if rescued_urgent_items >= 1 else 0.0)
        + 0.10 * nutrition_score
    )

    # Add realistic human stochastic variation
    if add_stochastic_noise:
        latent_utility += random.gauss(0.0, 0.06)

    latent_utility = max(0.0, min(1.0, latent_utility))

    # Discretize into 4 relevance grades (0 to 3)
    if missing_core_protein > 0 or latent_utility < 0.38:
        grade = 0  # Infeasible / Rejected
    elif latent_utility >= 0.78 and rescued_urgent_items >= 1:
        grade = 3  # Zero-Waste Hero
    elif latent_utility >= 0.62:
        grade = 2  # Highly Satisfying Home Meal
    else:
        grade = 1  # Marginal / Acceptable with compromises

    return latent_utility, grade
