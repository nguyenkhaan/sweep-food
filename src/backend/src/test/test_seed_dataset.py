"""Unit coverage for the curated default catalog seed dataset."""

from dataclasses import replace
from decimal import Decimal

import pytest

from scripts.seed import (
    DEFAULT_DATASET,
    AdminSeedConfig,
    NutritionSeed,
    SeedValidationError,
    reconcile_recipe_nutrition,
    validate_seed_input,
)
from src.model.enum_model import StorageMode


def _seed_config() -> AdminSeedConfig:
    """Provide a valid, non-production admin configuration for validation only."""
    return AdminSeedConfig(
        name="Seed Dataset Test Administrator",
        phone_e164="+84123456701",
        email="seed-dataset@example.test",
        password="test-seed-password",
    )


def test_curated_dataset_has_no_rejected_records() -> None:
    """The production dataset validates before any database write is attempted."""
    report = validate_seed_input(DEFAULT_DATASET, _seed_config())

    assert not report.rejected


def test_curated_dataset_covers_recommendation_and_storage_scenarios() -> None:
    """Three recipes and all storage modes support the first recommendation flows."""
    storage_modes = {rule.storage_mode for rule in DEFAULT_DATASET.shelf_life_rules}

    assert 3 <= len(DEFAULT_DATASET.recipes) <= 5
    assert storage_modes == set(StorageMode)


def test_curated_recipe_nutrition_reconciles_from_mass_ingredients() -> None:
    """Denormalized recipe totals exactly match their nutrition-bearing ingredients."""
    calculated = reconcile_recipe_nutrition(DEFAULT_DATASET)

    assert set(calculated) == {recipe.key for recipe in DEFAULT_DATASET.recipes}
    assert calculated["spinach-soup"].calories == Decimal("198.000")
    assert calculated["chicken-rice-bowl"].protein_g == Decimal("73.550")
    assert calculated["tomato-spinach-tofu-stir-fry"].carbs_g == Decimal("14.250")
    for recipe in DEFAULT_DATASET.recipes:
        actual = calculated[recipe.key]
        expected = recipe.details.nutrition
        assert actual.calories == expected.calories
        assert actual.protein_g == expected.protein_g
        assert actual.fat_g == expected.fat_g
        assert actual.carbs_g == expected.carbs_g
        assert actual.sugar_g == expected.sugar_g


def test_seed_validation_rejects_non_reconciling_recipe_nutrition() -> None:
    """A mismatched denormalized total cannot enter the curated dataset."""
    mismatched_recipe = replace(
        DEFAULT_DATASET.recipes[0],
        details=replace(
            DEFAULT_DATASET.recipes[0].details,
            nutrition=NutritionSeed(calories=Decimal("1.000")),
        ),
    )
    mismatched_dataset = replace(DEFAULT_DATASET, recipes=(mismatched_recipe,))

    with pytest.raises(SeedValidationError, match="nutrition does not reconcile"):
        validate_seed_input(mismatched_dataset, _seed_config())
