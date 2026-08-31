# pylint: disable=duplicate-code
"""Unit tests for the read-only cooking preview service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventorySource,
    MealPlanItemStatus,
    MealSlot,
    MeasurementUnit,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.cooking.cooking_dto import CookingPreviewRequestDTO
from src.module.cooking.cooking_helper import MealPlanItemNotFoundError
from src.module.cooking.cooking_service import CookingService
from src.service.fefo_service import FEFOService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a011")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a012")
RECIPE_INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a013")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a014")
CATEGORY_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a015")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a016")
MEAL_PLAN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a017")
MEAL_PLAN_ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a018")


@dataclass
class FakeRecipeResult:
    """Expose the scalar recipe result consumed by CookingService."""

    recipe: MealPlanItemModel | RecipeModel | None

    def scalar_one_or_none(self) -> MealPlanItemModel | RecipeModel | None:
        """Return the configured recipe result."""
        return self.recipe


@dataclass
class FakeIngredientResult:
    """Expose joined recipe-ingredient rows consumed by CookingService."""

    rows: list[tuple[RecipeIngredientModel, MasterIngredientModel]]

    def tuples(self) -> FakeIngredientResult:
        """Return the tuple-shaped result wrapper."""
        return self

    def all(self) -> list[tuple[RecipeIngredientModel, MasterIngredientModel]]:
        """Return all configured joined rows."""
        return self.rows


@dataclass
class FakeBatchResult:
    """Expose inventory batch rows consumed by CookingService."""

    batches: list[InventoryBatchModel]

    def scalars(self) -> FakeBatchResult:
        """Return the scalar-shaped result wrapper."""
        return self

    def all(self) -> list[InventoryBatchModel]:
        """Return all configured inventory batches."""
        return self.batches


@dataclass
class FakeDatabaseSession:
    """Read-only subset of AsyncSession used by cooking preview unit tests."""

    results: list[FakeRecipeResult | FakeIngredientResult | FakeBatchResult]
    execution_count: int = 0
    rollback_count: int = 0
    write_method_called: bool = field(default=False)

    async def execute(
        self,
        _statement: object,
    ) -> FakeRecipeResult | FakeIngredientResult | FakeBatchResult:
        """Return queued query results in the service query order."""
        self.execution_count += 1
        return self.results.pop(0)

    async def rollback(self) -> None:
        """Record rollback calls made only after a database failure."""
        self.rollback_count += 1

    def add(self, _record: object) -> None:
        """Record an unexpected write attempt."""
        self.write_method_called = True

    async def commit(self) -> None:
        """Record an unexpected commit attempt."""
        self.write_method_called = True

    async def flush(self) -> None:
        """Record an unexpected flush attempt."""
        self.write_method_called = True


def build_recipe() -> RecipeModel:
    """Build a seeded recipe that needs 500 ml of milk for two servings."""
    return RecipeModel(
        id=RECIPE_ID,
        name="Fresh milk smoothie",
        description="Seeded preview recipe.",
        instructions={"steps": ["Blend"]},
        default_servings=2.0,
        estimated_cooking_minutes=5,
        estimated_cost=18000.0,
        total_calories=122.0,
        total_protein_g=6.4,
        total_fat_g=6.6,
        total_carbs_g=9.6,
        total_sugar_g=9.6,
        other_nutrients={"calcium_mg": 226.0},
        tags={"values": ["quick"]},
    )


def build_meal_plan_item() -> MealPlanItemModel:
    """Build the owned plan item that is the preview contract input."""
    return MealPlanItemModel(
        id=MEAL_PLAN_ITEM_ID,
        meal_plan_id=MEAL_PLAN_ID,
        recipe_id=RECIPE_ID,
        recommendation_run_id=None,
        planned_for=date(2026, 8, 31),
        meal_slot=MealSlot.LUNCH,
        servings=2.0,
        status=MealPlanItemStatus.PLANNED,
    )


def build_recipe_ingredient() -> tuple[RecipeIngredientModel, MasterIngredientModel]:
    """Build the recipe ingredient and its canonical catalog record."""
    recipe_ingredient = RecipeIngredientModel(
        id=RECIPE_INGREDIENT_ID,
        recipe_id=RECIPE_ID,
        master_ingredient_id=INGREDIENT_ID,
        required_quantity=500.0,
        unit=MeasurementUnit.ML,
        is_optional=False,
    )
    ingredient = MasterIngredientModel(
        id=INGREDIENT_ID,
        name="Fresh milk",
        description="Seeded milk ingredient.",
        category_id=CATEGORY_ID,
        canonical_unit=MeasurementUnit.ML,
        other_nutrients={},
        default_storage_mode=StorageMode.REFRIGERATED,
    )
    return recipe_ingredient, ingredient


def build_batch() -> InventoryBatchModel:
    """Build an eligible one-liter batch owned by the authenticated user."""
    now = datetime.now(UTC)
    return InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=INGREDIENT_ID,
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=1.0,
        current_quantity=1.0,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=now + timedelta(days=1),
        expiration_source=ExpirationSource.MANUFACTURER,
        source=InventorySource.MANUAL,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.anyio
async def test_preview_scales_recipe_and_does_not_write_inventory() -> None:
    """Preview returns a converted FEFO proposal without calling write methods."""
    recipe = build_recipe()
    recipe_ingredient, ingredient = build_recipe_ingredient()
    database = FakeDatabaseSession(
        results=[
            FakeRecipeResult(build_meal_plan_item()),
            FakeRecipeResult(recipe),
            FakeIngredientResult([(recipe_ingredient, ingredient)]),
            FakeBatchResult([build_batch()]),
        ],
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    response = await service.preview(
        USER_ID,
        CookingPreviewRequestDTO(meal_plan_item_id=MEAL_PLAN_ITEM_ID),
    )

    assert response.recipe_id == RECIPE_ID
    assert response.servings == 2.0
    assert response.scaled_ingredients[0].required_quantity == 500.0
    assert response.proposed_deductions[0].batch_id == BATCH_ID
    assert response.proposed_deductions[0].quantity == 0.5
    assert response.proposed_deductions[0].unit is MeasurementUnit.LITER
    assert response.proposed_deductions[0].recipe_quantity == 500.0
    assert not response.missing_ingredients
    assert response.nutrition_estimate.calories == 122.0
    assert database.execution_count == 4
    assert database.rollback_count == 0
    assert not database.write_method_called


@pytest.mark.anyio
async def test_preview_returns_not_found_for_an_unowned_meal_plan_item() -> None:
    """Plan-item ownership fails before reading recipe or inventory data."""
    database = FakeDatabaseSession(results=[FakeRecipeResult(None)])
    service = CookingService(cast(AsyncSession, database), FEFOService())

    with pytest.raises(MealPlanItemNotFoundError):
        await service.preview(
            USER_ID,
            CookingPreviewRequestDTO(meal_plan_item_id=MEAL_PLAN_ITEM_ID),
        )

    assert database.execution_count == 1
    assert database.rollback_count == 0
    assert not database.write_method_called
