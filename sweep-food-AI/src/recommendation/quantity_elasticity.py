"""Continuous Quantity Elasticity Model with Profile-based Kitchen Heuristics.

Encodes the real-life culinary insight: 'Thiếu một chút vẫn nấu được'.
Eliminates boundary cliffs via a continuous C^0 piecewise formulation:
For HIGH elasticity (e.g. leafy greens, vegetables):
    elastic_score(r) =
        1.0                      if r >= 0.80
        0.85 + 0.15 * (r-0.4)/0.4 if 0.40 <= r < 0.80
        0.85 * (r / 0.40)        if r < 0.40

Profiles:
- VERY_HIGH: Basic seasonings & aromatics (fish sauce, salt, oil, pepper, garlic)
- HIGH: Vegetables, leafy greens, fresh herbs, mushrooms
- MEDIUM: Animal & plant proteins (pork, beef, chicken, fish, tofu)
- LOW_MEDIUM: Eggs (discrete counts, culinary structure)
- LOW: Flour, starches, noodles, rice
- VERY_LOW: Baking agents, yeast, gelatin
"""

from __future__ import annotations

from typing import TypedDict
from src.recommendation.ingredient_roles import IngredientRole


class ElasticityResult(TypedDict):
    ratio: float
    elastic_score: float
    profile: str
    usable: bool


class ElasticityProfile:
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW_MEDIUM = "LOW_MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


def determine_elasticity_profile(cleaned_name: str, role: str) -> str:
    """Assigns an elasticity profile based on ingredient type and physical behavior."""
    n = cleaned_name.strip().lower()

    # 1. Baking agents / structure critical
    if any(k in n for k in ["bột nở", "men nở", "baking powder", "gelatin", "men bánh"]):
        return ElasticityProfile.VERY_LOW

    # 2. Flour / Starches
    if any(k in n for k in ["bột mì", "bột gạo", "bột năng", "bột bắp", "bột chiên"]):
        return ElasticityProfile.LOW

    # 3. Eggs
    if any(k in n for k in ["trứng", "hột gà", "hột vịt", "trứng cút"]):
        return ElasticityProfile.LOW_MEDIUM

    # 4. Spices & Seasonings (VERY_HIGH)
    if role == IngredientRole.STAPLE_SPICE:
        return ElasticityProfile.VERY_HIGH

    # 5. Vegetables, Produce, Herbs, Mushrooms (HIGH)
    if role in (IngredientRole.CORE_PRODUCE, IngredientRole.OPTIONAL_GARNISH):
        return ElasticityProfile.HIGH

    # 6. Meat, Poultry, Seafood, Tofu (MEDIUM)
    if role == IngredientRole.CORE_PROTEIN:
        return ElasticityProfile.MEDIUM

    return ElasticityProfile.HIGH


def compute_quantity_elasticity(
    quantity_pantry: float,
    quantity_required: float,
    cleaned_name: str = "",
    role: str = IngredientRole.CORE_PRODUCE
) -> ElasticityResult:
    """Calculates continuous quantity elasticity and returns a structured output."""
    if quantity_required <= 0:
        return {
            "ratio": 1.0,
            "elastic_score": 1.0,
            "profile": ElasticityProfile.VERY_HIGH,
            "usable": True
        }

    ratio = max(0.0, quantity_pantry / quantity_required)
    profile = determine_elasticity_profile(cleaned_name, role)

    # 1. VERY_HIGH (Seasonings, Spices, Aromatics)
    if profile == ElasticityProfile.VERY_HIGH:
        if ratio >= 0.50:
            score = 1.0
        elif ratio >= 0.20:
            score = 0.90 + 0.10 * ((ratio - 0.20) / 0.30)
        else:
            score = 0.85 * (ratio / 0.20)
        usable = True  # In VN cooking, missing basic spice never stops cooking

    # 2. HIGH (Vegetables, Herbs, Mushrooms)
    # Continuous at r=0.80 and r=0.40, zero at r=0
    elif profile == ElasticityProfile.HIGH:
        if ratio >= 0.80:
            score = 1.0
        elif ratio >= 0.40:
            # Having 150g vs 300g required (r=0.5) -> score = 0.8875!
            score = 0.85 + 0.15 * ((ratio - 0.40) / 0.40)
        else:
            score = 0.85 * (ratio / 0.40)
        usable = ratio >= 0.35

    # 3. MEDIUM (Meat, Poultry, Seafood, Tofu)
    elif profile == ElasticityProfile.MEDIUM:
        if ratio >= 0.85:
            score = 1.0
        elif ratio >= 0.55:
            # 55% - 85% of meat allows slightly smaller portion
            score = 0.75 + 0.25 * ((ratio - 0.55) / 0.30)
        else:
            score = 0.75 * (ratio / 0.55)
        usable = ratio >= 0.50

    # 4. LOW_MEDIUM (Eggs)
    elif profile == ElasticityProfile.LOW_MEDIUM:
        if ratio >= 0.90:
            score = 1.0
        elif ratio >= 0.65:
            score = 0.70 + 0.30 * ((ratio - 0.65) / 0.25)
        else:
            score = 0.70 * (ratio / 0.65)
        usable = ratio >= 0.60

    # 5. LOW (Flour, Starches, Noodles)
    elif profile == ElasticityProfile.LOW:
        if ratio >= 0.95:
            score = 1.0
        elif ratio >= 0.75:
            score = 0.60 + 0.40 * ((ratio - 0.75) / 0.20)
        else:
            score = 0.60 * (ratio / 0.75)
        usable = ratio >= 0.70

    # 6. VERY_LOW (Baking agents, Yeast)
    else:
        if ratio >= 0.98:
            score = 1.0
        elif ratio >= 0.85:
            score = 0.40 + 0.60 * ((ratio - 0.85) / 0.13)
        else:
            score = 0.40 * (ratio / 0.85)
        usable = ratio >= 0.85

    return {
        "ratio": round(ratio, 4),
        "elastic_score": round(max(0.0, min(1.0, score)), 4),
        "profile": profile,
        "usable": usable
    }
