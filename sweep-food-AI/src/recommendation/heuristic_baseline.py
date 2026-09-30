"""Expert Handcrafted Domain Heuristic Baseline for Recipe Ranking.

Represents an expert rule-based ranking engine utilizing domain heuristics:
- Continuous Quantity Elasticity (elastic_match_score)
- Core Ingredient Deficits (missing_core_count)
- Zero-Waste Food Expiry Urgency (urgency_weighted_score)

Serves as the benchmark baseline against which machine learning models are compared.
"""

from __future__ import annotations

from typing import Any
from src.recommendation.ingredient_roles import IngredientRole, classify_ingredient_role
from src.recommendation.quantity_elasticity import compute_quantity_elasticity


def compute_domain_heuristic_score(
    pantry: dict[str, Any],
    recipe: dict[str, Any],
    recipe_ingredients: list[dict[str, Any]]
) -> float:
    """Computes expert domain heuristic ranking score (Spec 6.1 formula)."""
    pantry_items = pantry["items"]

    household_size = float(pantry.get("household_size") or 4.0)
    try:
        raw_servings = float(recipe.get("default_servings") or 4.0)
        default_servings = raw_servings if raw_servings > 0 else 4.0
    except (ValueError, TypeError):
        default_servings = 4.0
    scale_factor = household_size / default_servings

    pantry_by_code = {it.get("code"): it for it in pantry_items if it.get("code")}
    pantry_by_name = {(it.get("name") or "").strip().lower(): it for it in pantry_items if it.get("name")}

    elastic_scores = []
    missing_core_count = 0
    urgency_score = 0.0

    for ing in recipe_ingredients:
        c = ing.get("master_ingredient_code")
        n = (ing.get("cleaned_name") or "").strip().lower()
        base_g = float(ing.get("estimated_weight_g") or 100.0)
        req_g = base_g * scale_factor

        role = classify_ingredient_role(n, c)

        p_item = pantry_by_code.get(c) or pantry_by_name.get(n)
        avail_g = float(p_item["quantity_g"]) if p_item else 0.0

        el = compute_quantity_elasticity(avail_g, req_g, n, role)

        if role != IngredientRole.STAPLE_SPICE:
            elastic_scores.append(el["elastic_score"])
            if not el["usable"] and role in (IngredientRole.CORE_PROTEIN, IngredientRole.CORE_PRODUCE):
                missing_core_count += 1

        if p_item and not p_item.get("is_staple", False):
            hours = float(p_item.get("hours_to_expire") or 999.0)
            if hours <= 48.0:
                urgency_score += max(0.0, (72.0 - hours) / 72.0)

    avg_elastic = sum(elastic_scores) / len(elastic_scores) if elastic_scores else 1.0
    total_ings = max(1.0, float(len(recipe_ingredients)))

    # Spec 6.1 Expert Heuristic Formula
    heuristic_score = (
        0.45 * min(2.0, urgency_score)
        + 0.35 * avg_elastic
        - 0.20 * (missing_core_count / total_ings)
    )

    return float(heuristic_score)
