"""Serving-scale policy shared by recipe detail and cooking.

Recipes are stored for ``default_servings``. Scaling every line linearly gives
absurd results (0.3 g of an item, +1 g of fish sauce), so lines are rounded to a
cookable step and seasonings scale sub-linearly because taste does not grow in
proportion to portions.
"""

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import inspect

from src.model.enum_model import MeasurementUnit
from src.model.master_ingredient_model import MasterIngredientModel

SEASONING_CATEGORY_NAME = "Gia vị, nước chấm"
_SEASONING_EXPONENT = 0.7
_COUNT_UNITS = {MeasurementUnit.PIECE, MeasurementUnit.PACK, MeasurementUnit.OTHER}
_BIG_UNITS = {MeasurementUnit.KG, MeasurementUnit.LITER}


def is_seasoning(ingredient: MasterIngredientModel) -> bool:
    """Return whether the ingredient belongs to the pantry-staple seasoning category.

    The category relationship is read only when it was eagerly loaded, so this
    never triggers a lazy load on an async session.
    """
    if "category" in inspect(ingredient).unloaded:
        return False
    return ingredient.category.name == SEASONING_CATEGORY_NAME


def scale_quantity(
    quantity: Decimal,
    unit: MeasurementUnit,
    scale: Decimal,
    *,
    seasoning: bool,
) -> Decimal:
    """Scale one recipe line for a serving multiplier and round it to a usable step."""
    quantity = Decimal(str(quantity))
    if scale == 1:
        return quantity
    effective = scale
    if seasoning:
        effective = Decimal(str(float(scale) ** _SEASONING_EXPONENT))
    scaled = quantity * effective
    return _round_to_step(scaled, _step_for(scaled, unit))


def _step_for(value: Decimal, unit: MeasurementUnit) -> Decimal:
    if unit in _COUNT_UNITS:
        return Decimal("0.5")
    if unit in _BIG_UNITS:
        return Decimal("0.05")
    if value < 10:
        return Decimal("0.5")
    if value < 50:
        return Decimal(1)
    if value < 200:
        return Decimal(5)
    return Decimal(10)


def _round_to_step(value: Decimal, step: Decimal) -> Decimal:
    rounded = (value / step).quantize(Decimal(1), rounding=ROUND_HALF_UP) * step
    return max(rounded, step)
