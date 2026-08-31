# pylint: disable=duplicate-code
"""Unit tests for leftovers creation and cooking history APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
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
    MeasurementUnit,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.recipe_model import RecipeModel
from src.module.cooking.cooking_dto import CreateCookedLeftoverRequestDTO
from src.module.cooking.cooking_helper import (
    CookingCompletionConflictError,
    CookingSessionNotFoundError,
)
from src.module.cooking.cooking_service import CookingService
from src.service.fefo_service import FEFOService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a031")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a032")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a033")
LEFTOVER_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a037")
CONSUMED_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a038")


@dataclass
class FakeScalarResult:
    """Expose queued scalar result for query."""

    value: CookingSessionModel | RecipeModel | InventoryBatchModel | None

    def scalar_one_or_none(
        self,
    ) -> CookingSessionModel | RecipeModel | InventoryBatchModel | None:
        """Return the queued scalar result."""
        return self.value


@dataclass
class FakeListResult:
    """Expose queued list result for query."""

    rows: (
        list[CookingSessionModel]
        | list[CookingConsumptionModel]
        | list[InventoryBatchModel]
        | list[RecipeModel]
    )

    def scalars(self) -> FakeListResult:
        """Return the scalar list wrapper."""
        return self

    def scalar_one_or_none(
        self,
    ) -> (
        CookingSessionModel
        | RecipeModel
        | CookingConsumptionModel
        | InventoryBatchModel
        | None
    ):
        """Return the first queued row or None, matching a single-row query."""
        if not self.rows:
            return None
        return self.rows[0]

    def all(
        self,
    ) -> (
        list[CookingSessionModel]
        | list[CookingConsumptionModel]
        | list[InventoryBatchModel]
        | list[RecipeModel]
    ):
        """Return all queued rows."""
        return self.rows


@dataclass
class FakeDatabaseSession:
    """Minimal transaction-aware AsyncSession substitute for history & leftover tests."""

    results: list[FakeScalarResult | FakeListResult]
    added: list[object] = field(default_factory=list)
    commit_count: int = 0
    rollback_count: int = 0

    async def execute(
        self,
        _statement: object,
    ) -> FakeScalarResult | FakeListResult:
        """Return queued query results."""
        return self.results.pop(0)

    def add(self, record: object) -> None:
        """Record a pending insert in the transaction, applying ORM-style defaults."""
        if isinstance(record, InventoryBatchModel):
            if getattr(record, "id", None) is None:
                record.id = LEFTOVER_BATCH_ID
            if record.created_at is None:
                record.created_at = datetime.now(UTC)
        self.added.append(record)

    async def commit(self) -> None:
        """Record a successful transaction commit."""
        self.commit_count += 1

    async def rollback(self) -> None:
        """Record a failed transaction rollback."""
        self.rollback_count += 1

    async def flush(self) -> None:
        """No-op for unit tests that do not need ORM flush behaviour."""
        return


def build_completed_session() -> CookingSessionModel:
    """Build a completed user-owned cooking session."""
    return CookingSessionModel(
        id=SESSION_ID,
        user_id=USER_ID,
        recipe_id=RECIPE_ID,
        meal_plan_item_id=None,
        servings=2.0,
        status=CookingSessionStatus.COMPLETED,
        consumption_mode=CookingConsumptionMode.EXACT,
        nutrition_snapshot={"calories": 250.0},
        idempotency_key="completed-key",
        completed_at=datetime.now(UTC),
    )


def build_recipe() -> RecipeModel:
    """Build a recipe for testing."""
    return RecipeModel(
        id=RECIPE_ID,
        name="Beef Stew",
        description="Leftover test recipe",
        instructions={"steps": ["Cook"]},
        default_servings=2.0,
        estimated_cooking_minutes=30,
        other_nutrients={},
        tags={},
    )


@pytest.mark.anyio
async def test_create_leftover_for_completed_session_creates_cooked_food_batch() -> (
    None
):
    """Creating a leftover for a completed session creates a COOKED_FOOD batch and ledger entry."""
    session = build_completed_session()
    recipe = build_recipe()
    database = FakeDatabaseSession(
        results=[
            FakeScalarResult(session),
            FakeScalarResult(recipe),
        ]
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    request = CreateCookedLeftoverRequestDTO(
        quantity=1.0,
        unit=MeasurementUnit.PIECE,
        storage_mode=StorageMode.REFRIGERATED,
        expires_at=datetime.now(UTC) + timedelta(days=2),
        note="Saved portion",
    )
    response = await service.create_leftover(USER_ID, SESSION_ID, request)

    assert response.batch_id == LEFTOVER_BATCH_ID
    assert response.cooking_session_id == SESSION_ID
    assert response.batch_type == InventoryBatchType.COOKED_FOOD
    assert response.quantity == 1.0
    assert response.unit == MeasurementUnit.PIECE
    assert response.storage_mode == StorageMode.REFRIGERATED
    assert database.commit_count == 1
    assert len(database.added) == 2
    assert isinstance(database.added[0], InventoryBatchModel)
    batch = database.added[0]
    assert batch.source == InventorySource.LEFTOVER
    assert batch.source_cooking_session_id == SESSION_ID
    assert isinstance(database.added[1], InventoryLedgerEntryModel)
    ledger = database.added[1]
    assert ledger.event_type == InventoryLedgerEventType.LEFTOVER_CREATED


@pytest.mark.anyio
async def test_create_leftover_rejects_incomplete_session() -> None:
    """Creating a leftover for a PLANNED session raises an error."""
    session = build_completed_session()
    session.status = CookingSessionStatus.PLANNED
    database = FakeDatabaseSession(results=[FakeScalarResult(session)])
    service = CookingService(cast(AsyncSession, database), FEFOService())

    request = CreateCookedLeftoverRequestDTO(
        quantity=1.0,
        unit=MeasurementUnit.PIECE,
    )
    with pytest.raises(CookingCompletionConflictError):
        await service.create_leftover(USER_ID, SESSION_ID, request)


@pytest.mark.anyio
async def test_get_cooking_history_returns_user_sessions() -> None:
    """Getting cooking history returns a list of completed sessions."""
    session = build_completed_session()
    recipe = build_recipe()
    database = FakeDatabaseSession(
        results=[
            FakeListResult([session]),
            FakeListResult([recipe]),
        ]
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    history = await service.get_cooking_history(USER_ID)

    assert len(history.items) == 1
    assert history.items[0].session_id == SESSION_ID
    assert history.items[0].recipe_name == "Beef Stew"


@pytest.mark.anyio
async def test_get_cooking_history_detail_returns_session_and_consumptions() -> None:
    """Getting history detail returns session, recipe, consumptions, and leftover info."""
    session = build_completed_session()
    recipe = build_recipe()
    consumption = CookingConsumptionModel(
        id=UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a039"),
        cooking_session_id=SESSION_ID,
        recipe_ingredient_id=None,
        inventory_batch_id=CONSUMED_BATCH_ID,
        quantity=500.0,
        unit=MeasurementUnit.GRAM,
    )
    leftover = InventoryBatchModel(
        id=LEFTOVER_BATCH_ID,
        user_id=USER_ID,
        batch_type=InventoryBatchType.COOKED_FOOD,
        initial_quantity=1.0,
        current_quantity=1.0,
        unit=MeasurementUnit.PIECE,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.ESTIMATED,
        source=InventorySource.LEFTOVER,
        source_cooking_session_id=SESSION_ID,
    )
    database = FakeDatabaseSession(
        results=[
            FakeScalarResult(session),
            FakeScalarResult(recipe),
            FakeListResult([consumption]),
            FakeListResult([leftover]),
        ]
    )
    service = CookingService(cast(AsyncSession, database), FEFOService())

    detail = await service.get_cooking_history_detail(USER_ID, SESSION_ID)

    assert detail.session.id == SESSION_ID
    assert detail.recipe_name == "Beef Stew"
    assert len(detail.consumptions) == 1
    assert detail.consumptions[0].quantity == 500.0
    assert detail.leftover_batch_id == LEFTOVER_BATCH_ID


@pytest.mark.anyio
async def test_get_cooking_history_detail_raises_not_found_for_unowned_session() -> (
    None
):
    """Requesting detail for an unowned or non-existent session raises NotFoundError."""
    database = FakeDatabaseSession(results=[FakeScalarResult(None)])
    service = CookingService(cast(AsyncSession, database), FEFOService())

    with pytest.raises(CookingSessionNotFoundError):
        await service.get_cooking_history_detail(USER_ID, SESSION_ID)
