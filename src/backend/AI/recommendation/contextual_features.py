"""Nine contextual pantry/recipe features for the LightGBM LambdaMART ranker.

Authoritative feature ordering matching metadata.json:
1. core_coverage: share of core weight the pantry satisfies [0, 1]
2. core_missing_count: core ingredients effectively absent (count)
3. secondary_coverage: share of secondary weight satisfied [0, 1]
4. shopping_gap_items: distinct non-staple items to buy (count)
5. rescue_weight_g: grams of <=24h food the dish consumes
6. nutrition_confidence: share of recipe weight measured, not guessed [0, 1]
7. kcal_per_serving: clipped energy density
8. protein_per_serving: clipped protein density
9. prep_complexity: core count + log(1 + steps)
"""

from __future__ import annotations

import math
from typing import Any

from AI.catalog.master_index import get_effective_codes
from AI.recommendation.candidate_generator import extract_pantry_name_aliases

FEATURE_COLS: list[str] = [
    "core_coverage",
    "core_missing_count",
    "secondary_coverage",
    "shopping_gap_items",
    "rescue_weight_g",
    "nutrition_confidence",
    "kcal_per_serving",
    "protein_per_serving",
    "prep_complexity",
]

MONOTONE_CONSTRAINTS: list[int] = [1, -1, 1, -1, 1, 1, 0, 0, -1]

CORE_ROLES: tuple[str, ...] = ("core",)
SUBSTANTIVE_ROLES: tuple[str, ...] = ("core", "secondary", "liquid_base")
URGENT_HOURS: float = 24.0
PRESENCE_RATIO: float = 0.35

KCAL_CLIP: tuple[float, float] = (50.0, 1500.0)
PROTEIN_CLIP: tuple[float, float] = (0.0, 120.0)


def _num(value: object, default: float | None = None) -> float | None:
    try:
        f = float(value)  # type: ignore[arg-type]
        return f if not math.isnan(f) else default
    except (TypeError, ValueError):
        return default


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def pantry_index(
    items: list[dict[str, Any]],
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """Index pantry items by name/alias -> grams, code -> grams, and urgent subset.

    Grams add up across items, so stock split over several batches counts in full.
    """
    by_name: dict[str, float] = {}
    by_code: dict[str, float] = {}
    urgent: dict[str, float] = {}
    for item in items:
        name = (item.get("name") or "").strip().lower()
        raw_grams = item.get("quantity_g")
        grams = math.inf if raw_grams is None else (_num(raw_grams, 0.0) or 0.0)
        for code in get_effective_codes(item):
            by_code[code] = by_code.get(code, 0.0) + grams
        for alias in extract_pantry_name_aliases(name) | {name}:
            if alias:
                by_name[alias] = by_name.get(alias, 0.0) + grams
                if (
                    not item.get("is_staple")
                    and (_num(item.get("hours_to_expire"), 999.0) or 999.0)
                    <= URGENT_HOURS
                ):
                    urgent[alias] = urgent.get(alias, 0.0) + grams
    return by_name, by_code, urgent


_pantry_index = pantry_index


def _available(
    ing: dict[str, Any],
    by_name: dict[str, float],
    by_code: dict[str, float],
) -> float:
    code = str(ing.get("master_ingredient_code") or "").strip()
    if code and code in by_code:
        return by_code[code]
    name = (ing.get("cleaned_name") or "").strip().lower()
    if name in by_name:
        return by_name[name]
    best = 0.0
    for alias in extract_pantry_name_aliases(name):
        if alias in by_name:
            best = max(best, by_name[alias])
    return best


def extract_contextual_features(
    pantry: dict[str, Any],
    recipe: dict[str, Any],
    recipe_ingredients: list[dict[str, Any]],
    steps: list[dict[str, Any]] | None = None,
) -> dict[str, float]:
    """Compute the 9 authoritative ranker features for a candidate recipe."""
    household = _num(pantry.get("household_size"), 4.0) or 4.0
    servings = _num(recipe.get("default_servings"), 4.0) or 4.0
    if servings <= 0:
        servings = 4.0
    scale = household / servings

    by_name, by_code, urgent = pantry_index(pantry.get("items", []))

    core_req = core_have = 0.0
    sec_req = sec_have = 0.0
    core_missing = 0
    shopping_gap = 0
    rescue_g = 0.0
    core_count = 0

    for ing in recipe_ingredients:
        role = (ing.get("ingredient_role") or "").strip().lower()
        if role not in SUBSTANTIVE_ROLES:
            continue
        required = (_num(ing.get("estimated_weight_g"), 0.0) or 0.0) * scale
        if required <= 0:
            continue
        available = _available(ing, by_name, by_code)
        satisfied = min(required, available)
        ratio = available / required

        if role in CORE_ROLES:
            core_count += 1
            core_req += required
            core_have += satisfied
            if ratio < PRESENCE_RATIO:
                core_missing += 1
        else:
            sec_req += required
            sec_have += satisfied

        if ratio < PRESENCE_RATIO:
            shopping_gap += 1

        name = (ing.get("cleaned_name") or "").strip().lower()
        if urgent:
            aliases = extract_pantry_name_aliases(name) | {name}
            if aliases & urgent.keys():
                rescue_g += satisfied

    kcal = _num(recipe.get("calories_per_serving"), 0.0) or 0.0
    protein = _num(recipe.get("protein_per_serving"), 0.0) or 0.0
    n_steps = len(steps or [])

    return {
        "core_coverage": round(core_have / core_req, 4) if core_req > 0 else 1.0,
        "core_missing_count": float(core_missing),
        "secondary_coverage": round(sec_have / sec_req, 4) if sec_req > 0 else 1.0,
        "shopping_gap_items": float(shopping_gap),
        "rescue_weight_g": round(rescue_g, 1),
        "nutrition_confidence": _num(recipe.get("nutrition_confidence"), 0.0) or 0.0,
        "kcal_per_serving": round(_clip(kcal, *KCAL_CLIP), 1),
        "protein_per_serving": round(_clip(protein, *PROTEIN_CLIP), 1),
        "prep_complexity": round(core_count + math.log1p(n_steps), 3),
    }


def feature_vector(*args: Any, **kwargs: Any) -> list[float]:
    """Return feature values in the strict order required by LightGBM."""
    feats = extract_contextual_features(*args, **kwargs)
    return [feats[c] for c in FEATURE_COLS]
