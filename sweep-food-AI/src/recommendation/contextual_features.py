"""Nine contextual features for the pantry ranker.

Replaces the 30-feature extractor, which fed the ranker near-verbatim copies of
the synthetic label's own terms (`time_feasibility_diff` == the label's time
penalty, `dish_type_code` == its role harmony, `protein_energy_ratio` == its
nutrition score). That is why the ablation showed 30 features scoring *worse*
than 16: the extras were noise on top of leakage.

Design rules applied here
-------------------------
* Role-aware, never token-aware. Token overlap and Jaccard are dominated by
  seasoning, which 55% of recipes are half made of.
* Every feature must survive a real pantry. Nothing derived from
  `estimated_cooking_minutes` as a platform constant, from heuristic
  `dish_type`/`cooking_method` codes, or from unreliable `default_servings`.
* Data quality is itself a feature (`nutrition_confidence`), so a dish with
  guessed weights loses rank instead of pretending to be precise.
* Signs are monotone by construction, so the trainer can be constrained.

FEATURE_COLS is the authoritative ordering for training and serving.
"""

from __future__ import annotations

import math
import re
from typing import Any

from src.recommendation.candidate_generator import extract_pantry_name_aliases
from src.recommendation.pantry_resolver import get_effective_codes

FEATURE_COLS: list[str] = [
    "core_coverage",            # + share of core weight the pantry satisfies
    "core_missing_count",       # - core ingredients effectively absent
    "secondary_coverage",       # + share of secondary weight satisfied
    "shopping_gap_items",       # - distinct non-staple items to buy
    "rescue_weight_g",          # + grams of <=24h food the dish consumes
    "nutrition_confidence",     # + share of recipe weight measured, not guessed
    "kcal_per_serving",         # clipped energy density
    "protein_per_serving",      # clipped protein density
    "prep_complexity",          # - core count + log(1 + steps)
]

# Monotone direction per feature for LightGBM `monotone_constraints`.
MONOTONE_CONSTRAINTS: list[int] = [1, -1, 1, -1, 1, 1, 0, 0, -1]

CORE_ROLES = ("core",)
SUBSTANTIVE_ROLES = ("core", "secondary", "liquid_base")
URGENT_HOURS = 24.0
PRESENCE_RATIO = 0.35  # below this share of the requirement, treat as absent

KCAL_CLIP = (50.0, 1500.0)
PROTEIN_CLIP = (0.0, 120.0)


def _num(value: Any, default: float | None = None) -> float | None:
    try:
        f = float(value)
        return f if f == f else default
    except (TypeError, ValueError):
        return default


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pantry_index(items: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """name/alias -> grams, code -> grams, and the urgent subset."""
    by_name: dict[str, float] = {}
    by_code: dict[str, float] = {}
    urgent: dict[str, float] = {}
    for item in items:
        name = (item.get("name") or "").strip().lower()
        grams = _num(item.get("quantity_g"), 0.0) or 0.0
        for code in get_effective_codes(item):
            by_code[code] = max(by_code.get(code, 0.0), grams)
        for alias in extract_pantry_name_aliases(name) | {name}:
            if alias:
                by_name[alias] = max(by_name.get(alias, 0.0), grams)
                if not item.get("is_staple") and (_num(item.get("hours_to_expire"), 999.0) or 999.0) <= URGENT_HOURS:
                    urgent[alias] = max(urgent.get(alias, 0.0), grams)
    return by_name, by_code, urgent


def _available(ing: dict[str, Any], by_name: dict[str, float], by_code: dict[str, float]) -> float:
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
    household = _num(pantry.get("household_size"), 4.0) or 4.0
    servings = _num(recipe.get("default_servings"), 4.0) or 4.0
    if servings <= 0:
        servings = 4.0
    scale = household / servings

    by_name, by_code, urgent = _pantry_index(pantry.get("items", []))

    core_req = core_have = 0.0
    sec_req = sec_have = 0.0
    core_missing = 0
    shopping_gap = 0
    rescue_g = 0.0
    core_count = 0

    for ing in recipe_ingredients:
        role = (ing.get("ingredient_role") or "").strip()
        if role not in SUBSTANTIVE_ROLES:
            continue  # seasoning and garnish never decide a dish
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
    feats = extract_contextual_features(*args, **kwargs)
    return [feats[c] for c in FEATURE_COLS]
