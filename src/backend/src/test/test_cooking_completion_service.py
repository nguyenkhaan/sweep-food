# pylint: disable=duplicate-code
"""Unit tests for atomic, idempotent cooking completion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.cooking_consumption_model import CookingConsumptionModel
from src.model.cooking_session_model import CookingSessionModel
from src.model.enum_model import (
    CookingConsumptionMode,
    CookingSessionStatus,
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MealPlanItemStatus,
    MealSlot,
    MeasurementUnit,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.recipe_ingredient_model import RecipeIngredientModel
from src.model.recipe_model import RecipeModel
from src.module.cooking.cooking_dto import (
    CompleteCookingSessionRequestDTO,
    CreateCookingSessionRequestDTO,
)
from src.module.cooking.cooking_helper import InsufficientInventoryError
from src.module.cooking.cooking_service import CookingService
from src.service.fefo_service import FEFOService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a031")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a032")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a033")
RECIPE_INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a034")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a035")
CATEGORY_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a036")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a037")
MEAL_PLAN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a039")
MEAL_PLAN_ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a040")


@dataclass
class FakeScalarResult:
    """Expose the scalar result shape used by session and recipe queries."""

    value: CookingSessionModel | MealPlanItemModel | RecipeModel | None

    def scalar_one_or_none(
        self,
    ) -> CookingSessionModel | MealPlanItemModel | RecipeModel | None:
        """Return the queued scalar result."""
        return self.value


@dataclass
class FakeIngredientResult:
    """Expose joined recipe-ingredient rows."""

    rows: list[tuple[RecipeIngredientModel, MasterIngredientModel]]

    def tuples(self) -> FakeIngredientResult:
        """Return the tuple result wrapper."""
        return self

    def all(self) -> list[tuple[RecipeIngredientModel, MasterIngredientModel]]:
        """Return all joined rows."""
        return self.rows


@dataclass
class FakeBatchResult:
    """Expose scalar batches and consumption rows."""

    rows: list[InventoryBatchModel] | list[CookingConsumptionModel]

    def scalars(self) -> FakeBatchResult:
        """Return the scalar result wrapper."""
        return self

    def all(self) -> list[InventoryBatchModel] | list[CookingConsumptionModel]:
        """Return all queued rows."""
        return self.rows


@dataclass
class FakeDatabaseSession:
    """Minimal transaction-aware AsyncSession substitute for completion tests."""

    results: list[FakeScalarResult | FakeIngredientResult | FakeBatchResult]
    added: list[object] = field(default_factory=list)
    commit_count: int = 0
    rollback_count: int = 0

    async def execute(
        self,
        _statement: object,
    ) -> FakeScalarResult | FakeIngredientResult | FakeBatchResult:
        """Return queued query results in their expected execution order."""
        return self.results.pop(0)

    def add(self, record: object) -> None:
        """Record a pending insert in the transaction."""
        if isinstance(record, CookingSessionModel):
            record.id = SESSION_ID
        self.added.append(record)

    async def commit(self) -> None:
        """Record a successful transaction commit."""
        self.commit_count += 1

    async def rollback(self) -> None:
        """Record a failed transaction rollback."""
        self.rollback_count += 1


def build_recipe() -> RecipeModel:
    """Build a two-serving recipe requiring 500 ml of milk."""
    return RecipeModel(
        id=RECIPE_ID,
        name="Fresh milk smoothie",
        description="Completion test recipe.",
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


def build_session(
    status: CookingSessionStatus = CookingSessionStatus.PLANNED,
    idempotency_key: str | None = None,
) -> CookingSessionModel:
    """Build a planned or completed user-owned cooking session."""
    return CookingSessionModel(
        id=SESSION_ID,
        user_id=USER_ID,
        recipe_id=RECIPE_ID,
        meal_plan_item_id=None,
        servings=2.0,
        status=status,
        consumption_mode=(
            CookingConsumptionMode.EXACT
            if status is CookingSessionStatus.COMPLETED
            else None
        ),
        nutrition_snapshot={"calories": 122.0},
        idempotency_key=idempotency_key,
        completed_at=(
            datetime.now(UTC) if status is CookingSessionStatus.COMPLETED else None
        ),
    )


def build_recipe_ingredient() -> tuple[RecipeIngredientModel, MasterIngredientModel]:
    """Build the recipe ingredient and matching master catalog ingredient."""
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
        description="Completion test ingredient.",
        category_id=CATEGORY_ID,
        canonical_unit=MeasurementUnit.ML,
        other_nutrients={},
        default_storage_mode=StorageMode.REFRIGERATED,
    )
    return recipe_ingredient, ingredient


def build_meal_plan_item() -> MealPlanItemModel:
    """Build an owned meal-plan item that selects the completion-test recipe."""
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


def build_batch(current_quantity: float = 1.0) -> InventoryBatchModel:
    """Build an eligible liter batch for the session's authenticated user."""
    now = datetime.now(UTC)
    return InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=INGREDIENT_ID,
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=1.0,
        current_quantity=current_quantity,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=now + timedelta(days=1),
        expiration_source=ExpirationSource.MANUFACTURER,
        source=InventorySource.MANUAL,
        created_at=now,
        updated_at=now,
    )


def build_completion_database(
    batch: InventoryBatchModel,
) -> FakeDatabaseSession:
    """Queue lookups for a new completion transaction and its locks."""
    recipe_ingredient, ingredient = build_recipe_ingredient()
    return FakeDatabaseSession(
        results=[
            FakeScalarResult(None),
            FakeScalarResult(build_session()),
            FakeScalarResult(None),
            FakeScalarResult(build_recipe()),
            FakeIngredientResult([(recipe_ingredient, ingredient)]),
            FakeBatchResult([batch]),
        ]
    )


@pytest.mark.anyio
async def test_complete_session_atomically_deducts_and_records_ledger() -> None:
    """An exact completion commits batch, consumption, and ledger changes together."""
    batch = build_batch()
    database = build_completion_database(batch)
    service = CookingService(cast(AsyncSession, database), FEFOService())

    response = await service.complete_session(
        USER_ID,
        SESSION_ID,
        "completion-test-key",
        CompleteCookingSessionRequestDTO(consumption_mode=CookingConsumptionMode.EXACT),
    )

    assert batch.current_quantity == 0.5
    assert batch.status is InventoryBatchStatus.ACTIVE
    assert response.session.status is CookingSessionStatus.COMPLETED
    assert response.consumptions[0].quantity == 0.5
    assert response.consumptions[0].unit is MeasurementUnit.LITER
    assert response.updated_batches[0].current_quantity == 0.5
    assert database.commit_count == 1
    assert database.rollback_count == 0
    assert len(database.added) == 2
    assert isinstance(database.added[0], CookingConsumptionModel)
    assert isinstance(database.added[1], InventoryLedgerEntryModel)
    ledger_entry = database.added[1]
    assert ledger_entry.event_type is InventoryLedgerEventType.COOKING_CONSUMPTION
    assert ledger_entry.quantity_before == 1.0
    assert ledger_entry.quantity_delta == -0.5
    assert ledger_entry.quantity_after == 0.5


@pytest.mark.anyio
async def test_create_session_derives_recipe_from_an_owned_meal_plan_item() -> None:
    """Session creation persists the recipe linked by the supplied plan item."""
    recipe_ingredient, ingredient = build_recipe_ingredient()
    database = FakeDatabaseSession(
        results=[
            FakeScalarResult(build_meal_plan_item()),
            FakeScalarResult(build_recipe()),
            FakeIngredientResult([(recipe_ingredient, ingredient)]),
            FakeBatchResult([build_batch()]),
        ]
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    response = await service.create_session(
        USER_ID,
        CreateCookingSessionRequestDTO(
            meal_plan_item_id=MEAL_PLAN_ITEM_ID,
            servings=2.0,
        ),
    )

    assert response.id == SESSION_ID
    assert response.recipe_id == RECIPE_ID
    assert response.meal_plan_item_id == MEAL_PLAN_ITEM_ID
    assert response.status is CookingSessionStatus.PLANNED
    assert database.commit_count == 1
    assert database.rollback_count == 0
    assert isinstance(database.added[0], CookingSessionModel)


@pytest.mark.anyio
async def test_create_session_rejects_missing_inventory_without_writes() -> None:
    """A planned session is not persisted when its recipe lacks eligible stock."""
    recipe_ingredient, ingredient = build_recipe_ingredient()
    database = FakeDatabaseSession(
        results=[
            FakeScalarResult(build_meal_plan_item()),
            FakeScalarResult(build_recipe()),
            FakeIngredientResult([(recipe_ingredient, ingredient)]),
            FakeBatchResult([]),
        ]
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    with pytest.raises(InsufficientInventoryError) as error:
        await service.create_session(
            USER_ID,
            CreateCookingSessionRequestDTO(
                meal_plan_item_id=MEAL_PLAN_ITEM_ID,
                servings=2.0,
            ),
        )

    assert error.value.status_code == 409
    assert error.value.detail == (
        "Insufficient inventory to create cooking session: "
        "Fresh milk: missing 500 ML"
    )
    assert database.commit_count == 0
    assert database.rollback_count == 1
    assert not database.added


@pytest.mark.anyio
async def test_complete_session_rejects_insufficient_stock_without_writes() -> None:
    """Stock revalidation fails before any mutable record is created or committed."""
    database = build_completion_database(build_batch(current_quantity=0.25))
    service = CookingService(cast(AsyncSession, database), FEFOService())

    with pytest.raises(InsufficientInventoryError):
        await service.complete_session(
            USER_ID,
            SESSION_ID,
            "insufficient-stock-key",
            CompleteCookingSessionRequestDTO(
                consumption_mode=CookingConsumptionMode.EXACT
            ),
        )

    assert database.commit_count == 0
    assert database.rollback_count == 1
    assert not database.added


@pytest.mark.anyio
async def test_complete_session_returns_saved_result_for_an_idempotency_retry() -> None:
    """A retry returns saved records without a second deduction or commit."""
    session = build_session(
        status=CookingSessionStatus.COMPLETED,
        idempotency_key="retry-key",
    )
    consumption = CookingConsumptionModel(
        id=UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a038"),
        cooking_session_id=SESSION_ID,
        recipe_ingredient_id=RECIPE_INGREDIENT_ID,
        inventory_batch_id=BATCH_ID,
        quantity=0.5,
        unit=MeasurementUnit.LITER,
    )
    database = FakeDatabaseSession(
        results=[
            FakeScalarResult(session),
            FakeBatchResult([consumption]),
            FakeBatchResult([build_batch(current_quantity=0.5)]),
        ]
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    response = await service.complete_session(
        USER_ID,
        SESSION_ID,
        "retry-key",
        CompleteCookingSessionRequestDTO(consumption_mode=CookingConsumptionMode.EXACT),
    )

    assert response.session.id == SESSION_ID
    assert response.consumptions[0].inventory_batch_id == BATCH_ID
    assert response.updated_batches[0].current_quantity == 0.5
    assert database.commit_count == 0
    assert database.rollback_count == 0
    assert not database.added
