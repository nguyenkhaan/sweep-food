"""Serving-scale policy and cooking preview behavior for staples/unit mismatches."""

from decimal import Decimal

import pytest

from src.model.enum_model import MeasurementUnit
from src.service.recipe_quantity import scale_quantity


@pytest.mark.parametrize(
    ("quantity", "unit", "scale", "seasoning", "expected"),
    [
        ("4", MeasurementUnit.GRAM, "0.25", False, "1.0"),
        ("1", MeasurementUnit.OTHER, "0.25", False, "0.5"),
        ("1", MeasurementUnit.GRAM, "0.25", False, "0.5"),
        ("300", MeasurementUnit.GRAM, "1.5", False, "450"),
        ("500", MeasurementUnit.GRAM, "1", False, "500"),
        ("1.5", MeasurementUnit.KG, "2", False, "3.0"),
    ],
)
def test_scale_quantity_rounds_to_cookable_steps(
    quantity: str,
    unit: MeasurementUnit,
    scale: str,
    seasoning: bool,
    expected: str,
) -> None:
    """Scaled lines never produce fractions like 0.3 g and never drop to zero."""
    result = scale_quantity(Decimal(quantity), unit, Decimal(scale), seasoning=seasoning)
    assert result == Decimal(expected)


def test_seasoning_scales_slower_than_portions() -> None:
    """Doubling portions must not double the salt, halving must not halve it."""
    doubled = scale_quantity(
        Decimal(10), MeasurementUnit.GRAM, Decimal(2), seasoning=True
    )
    halved = scale_quantity(
        Decimal(10), MeasurementUnit.GRAM, Decimal("0.5"), seasoning=True
    )
    assert Decimal(10) < doubled < Decimal(20)
    assert Decimal(5) < halved < Decimal(10)


def _preview(ingredient_unit, category_name, batch_unit, batch_qty):
    """Build a preview for one 500-unit ingredient against one pantry batch."""
    from typing import cast

    from sqlalchemy.ext.asyncio import AsyncSession

    from src.module.cooking.cooking_helper import CookingHelper
    from src.model.ingredient_category_model import IngredientCategoryModel
    from src.service.fefo_service import FEFOService
    from src.test.test_cooking_service import (
        build_batch,
        build_recipe,
        build_recipe_ingredient,
    )

    recipe = build_recipe()
    recipe_ingredient, ingredient = build_recipe_ingredient()
    recipe_ingredient.unit = ingredient_unit
    ingredient.category = IngredientCategoryModel(name=category_name)
    batch = build_batch()
    batch.unit = batch_unit
    batch.current_quantity = batch_qty
    helper = CookingHelper(cast(AsyncSession, None), FEFOService())
    return helper.build_preview(recipe, [(recipe_ingredient, ingredient)], [batch], 2.0)


def test_preview_never_reports_seasoning_as_missing() -> None:
    """An empty pantry must not block cooking because of salt or fish sauce."""
    preview = _preview(MeasurementUnit.GRAM, "Gia vị, nước chấm", MeasurementUnit.GRAM, 1.0)
    assert not preview.missing_ingredients


def test_preview_treats_unconvertible_unit_stock_as_available() -> None:
    """Pantry pieces vs recipe grams cannot be compared and must not read as missing."""
    preview = _preview(MeasurementUnit.GRAM, "Thịt", MeasurementUnit.PIECE, 3.0)
    assert not preview.missing_ingredients


def test_preview_still_reports_real_shortfall_for_main_ingredient() -> None:
    """Compatible but insufficient stock of a main ingredient stays missing."""
    preview = _preview(MeasurementUnit.GRAM, "Thịt", MeasurementUnit.GRAM, 100.0)
    assert [m.missing_quantity for m in preview.missing_ingredients] == [400.0]


def _line_and_batch(recipe_name, cleaned_name, batch_master_name, custom_name=None):
    from uuid import uuid4

    from sqlalchemy.orm import attributes

    from src.model.inventory_batch_model import InventoryBatchModel
    from src.model.master_ingredient_model import MasterIngredientModel
    from src.model.recipe_ingredient_model import RecipeIngredientModel

    ingredient = MasterIngredientModel(id=uuid4(), name=recipe_name)
    line = RecipeIngredientModel(
        master_ingredient_id=ingredient.id,
        ai_attributes={"cleaned_name": cleaned_name},
    )
    batch = InventoryBatchModel(
        master_ingredient_id=uuid4() if batch_master_name else None,
        custom_name=custom_name,
    )
    if batch_master_name:
        batch.master_ingredient = MasterIngredientModel(
            id=batch.master_ingredient_id, name=batch_master_name
        )
    else:
        attributes.set_committed_value(batch, "master_ingredient", None)
    return line, ingredient, batch


def test_batch_with_a_different_master_but_same_name_satisfies_the_line() -> None:
    """Pantry 'Thịt bò' must satisfy recipe 'Thịt bò nạc' like the recommendation does."""
    from src.service.ingredient_match import batch_matches_line

    line, ingredient, batch = _line_and_batch("Thịt bò nạc", "thịt bò", "Thịt bò")
    assert batch_matches_line(batch, line, ingredient)


def test_custom_named_batch_matches_by_name_and_unrelated_does_not() -> None:
    """Free-text pantry items match by name; different foods never match."""
    from src.service.ingredient_match import batch_matches_line

    line, ingredient, batch = _line_and_batch("Thịt bò nạc", "thịt bò", None, "thịt bò")
    assert batch_matches_line(batch, line, ingredient)
    line, ingredient, batch = _line_and_batch("Thịt bò nạc", "thịt bò", "Cá basa")
    assert not batch_matches_line(batch, line, ingredient)
