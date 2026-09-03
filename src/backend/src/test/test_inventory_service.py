"""Unit tests for transactional inventory service behavior."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MeasurementUnit,
    ShelfLifeRuleScope,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.module.inventory.inventory_dto import (
    ConsumeInventoryBatchRequestDTO,
    CreateInventoryBatchRequestDTO,
    InventoryAdjustmentRequestDTO,
    MoveInventoryBatchRequestDTO,
    UpdateInventoryBatchRequestDTO,
)
from src.module.inventory.inventory_service import (
    InventoryBatchNotFoundError,
    InventoryConflictError,
    InventoryService,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b201")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b202")
NOW = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)


def _custom_batch(
    *,
    expiration_source: ExpirationSource = ExpirationSource.UNKNOWN,
) -> InventoryBatchModel:
    """Build one mutable custom batch for focused mutation tests."""
    return InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="Home-made sauce",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=2.0,
        current_quantity=2.0,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=(
            NOW + timedelta(days=3)
            if expiration_source is ExpirationSource.MANUFACTURER
            else None
        ),
        expiration_source=expiration_source,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )


class FakeResult:
    """Expose only SQLAlchemy result operations used by InventoryService."""

    def __init__(self, value: object) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object:
        """Return the configured optional scalar."""
        return self.value

    def scalar_one(self) -> object:
        """Return the configured required scalar."""
        return self.value

    def scalars(self) -> FakeResult:
        """Mirror SQLAlchemy's scalar-result adapter."""
        return self

    def all(self) -> list[object]:
        """Return the configured result list."""
        assert isinstance(self.value, list)
        return self.value


class FakeDatabaseSession:
    """Provide deterministic query results and capture committed model state."""

    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.added: list[object] = []
        self.statements: list[object] = []
        self.refreshed: list[object] = []
        self.commit_count = 0
        self.rollback_count = 0

    async def execute(self, statement: object) -> FakeResult:
        """Capture the query and return its queued result."""
        self.statements.append(statement)
        return self.results.pop(0)

    def add(self, record: object) -> None:
        """Capture a staged record and emulate generated values."""
        self.added.append(record)
        if isinstance(record, InventoryBatchModel):
            record.id = BATCH_ID
            record.created_at = NOW
            record.updated_at = NOW
        if isinstance(record, InventoryLedgerEntryModel):
            record.id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b203")
            record.created_at = NOW

    async def flush(self) -> None:
        """Emulate a successful flush."""
        return

    async def commit(self) -> None:
        """Record a committed transaction."""
        self.commit_count += 1

    async def refresh(self, instance: object) -> None:
        """Record the explicit post-commit ORM refresh."""
        self.refreshed.append(instance)

    async def rollback(self) -> None:
        """Record a rolled-back transaction."""
        self.rollback_count += 1


@pytest.mark.anyio
async def test_create_custom_batch_persists_initial_stock_atomically() -> None:
    """A manual custom batch and matching ledger share one commit."""
    database = FakeDatabaseSession([FakeResult(None)])
    service = InventoryService(cast(AsyncSession, database))

    response = await service.create_batch(
        USER_ID,
        CreateInventoryBatchRequestDTO(
            custom_name="Home-made sauce",
            quantity=2.0,
            unit=MeasurementUnit.LITER,
            storage_mode=StorageMode.REFRIGERATED,
        ),
        "create-custom-1",
    )

    batch = next(
        item for item in database.added if isinstance(item, InventoryBatchModel)
    )
    ledger = next(
        item for item in database.added if isinstance(item, InventoryLedgerEntryModel)
    )
    assert response.id == BATCH_ID
    assert response.ingredient_name == "Home-made sauce"
    assert response.expiration_source is ExpirationSource.UNKNOWN
    assert batch.current_quantity == 2.0
    assert ledger.event_type is InventoryLedgerEventType.INITIAL_STOCK
    assert ledger.quantity_before == 0.0
    assert ledger.quantity_after == 2.0
    assert database.commit_count == 1
    assert database.rollback_count == 0


@pytest.mark.anyio
async def test_create_catalog_batch_uses_ingredient_shelf_life_rule() -> None:
    """Missing manufacturer expiry is estimated from the narrowest seeded rule."""
    ingredient_id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b208")
    category_id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b209")
    ingredient = MasterIngredientModel(
        id=ingredient_id,
        name="Spinach",
        description="Leafy vegetable",
        category_id=category_id,
        canonical_unit=MeasurementUnit.GRAM,
        default_storage_mode=StorageMode.REFRIGERATED,
        other_nutrients={},
    )
    rule = ShelfLifeRuleModel(
        master_ingredient_id=ingredient_id,
        category_id=None,
        scope=ShelfLifeRuleScope.INGREDIENT,
        storage_mode=StorageMode.REFRIGERATED,
        min_days=3,
        max_days=5,
        default_days=4,
    )
    database = FakeDatabaseSession(
        [
            FakeResult(None),
            FakeResult(ingredient),
            FakeResult([rule]),
            FakeResult(ingredient),
        ]
    )
    service = InventoryService(cast(AsyncSession, database))

    response = await service.create_batch(
        USER_ID,
        CreateInventoryBatchRequestDTO(
            master_ingredient_id=ingredient_id,
            quantity=500.0,
            unit=MeasurementUnit.GRAM,
            storage_mode=StorageMode.REFRIGERATED,
            stored_at=NOW,
        ),
        "create-catalog-1",
    )

    assert response.expiration_source is ExpirationSource.ESTIMATED
    assert response.expires_at == NOW + timedelta(days=4)


@pytest.mark.anyio
async def test_expiration_override_is_audited_without_changing_quantity() -> None:
    """A user-provided expiry becomes authoritative and leaves a correction audit."""
    batch = InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="Home-made sauce",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=2.0,
        current_quantity=2.0,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    database = FakeDatabaseSession([FakeResult(None), FakeResult(batch)])
    service = InventoryService(cast(AsyncSession, database))
    overridden_expiry = NOW + timedelta(days=7)

    response = await service.update_batch(
        USER_ID,
        BATCH_ID,
        UpdateInventoryBatchRequestDTO(
            expires_at=overridden_expiry,
            reason="Manufacturer sticker checked",
        ),
        "expiry-override-1",
    )

    ledger = next(
        item for item in database.added if isinstance(item, InventoryLedgerEntryModel)
    )
    assert response.expires_at == overridden_expiry
    assert response.expiration_source is ExpirationSource.USER_OVERRIDE
    assert response.current_quantity == 2.0
    assert ledger.event_type is InventoryLedgerEventType.METADATA_UPDATED
    assert ledger.quantity_delta == 0.0
    assert ledger.reason == "Manufacturer sticker checked"


@pytest.mark.anyio
async def test_manufacturer_expiration_cannot_be_cleared_into_an_estimate() -> None:
    """Clearing an authoritative manufacturer date fails before any write."""
    database = FakeDatabaseSession(
        [
            FakeResult(None),
            FakeResult(_custom_batch(expiration_source=ExpirationSource.MANUFACTURER)),
        ]
    )
    service = InventoryService(cast(AsyncSession, database))

    with pytest.raises(
        InventoryConflictError,
        match="Manufacturer expiration cannot be cleared",
    ):
        await service.update_batch(
            USER_ID,
            BATCH_ID,
            UpdateInventoryBatchRequestDTO(
                expires_at=None,
                reason="Sticker damaged",
            ),
            "clear-manufacturer-1",
        )

    assert not database.added
    assert database.commit_count == 0
    assert database.rollback_count == 1


@pytest.mark.anyio
async def test_manual_consumption_has_its_own_idempotent_ledger_event() -> None:
    """The consume command deducts stock and is distinguishable from correction."""
    database = FakeDatabaseSession([FakeResult(None), FakeResult(_custom_batch())])
    service = InventoryService(cast(AsyncSession, database))

    response = await service.consume_batch(
        USER_ID,
        BATCH_ID,
        ConsumeInventoryBatchRequestDTO(quantity=0.5, reason="Tasted sauce"),
        "manual-consume-1",
    )

    ledger = next(
        item for item in database.added if isinstance(item, InventoryLedgerEntryModel)
    )
    assert response.current_quantity == 1.5
    assert ledger.event_type is InventoryLedgerEventType.MANUAL_CONSUMPTION
    assert ledger.quantity_delta == -0.5
    assert ledger.idempotency_key == "manual-consume-1"


@pytest.mark.anyio
async def test_move_and_archive_append_distinct_zero_delta_audits() -> None:
    """Lifecycle metadata operations retain their own idempotency scopes."""
    moved_batch = _custom_batch(expiration_source=ExpirationSource.MANUFACTURER)
    move_database = FakeDatabaseSession([FakeResult(None), FakeResult(moved_batch)])
    move_service = InventoryService(cast(AsyncSession, move_database))

    await move_service.move_batch(
        USER_ID,
        BATCH_ID,
        MoveInventoryBatchRequestDTO(
            storage_mode=StorageMode.FROZEN,
            reason="Moved to freezer",
        ),
        "move-1",
    )

    move_ledger = next(
        item
        for item in move_database.added
        if isinstance(item, InventoryLedgerEntryModel)
    )
    assert move_ledger.event_type is InventoryLedgerEventType.MOVED
    assert move_ledger.quantity_delta == 0.0

    archive_database = FakeDatabaseSession(
        [FakeResult(None), FakeResult(_custom_batch())]
    )
    archive_service = InventoryService(cast(AsyncSession, archive_database))
    await archive_service.archive_batch(
        USER_ID,
        BATCH_ID,
        "archive-1",
        "No longer tracked",
    )

    archive_ledger = next(
        item
        for item in archive_database.added
        if isinstance(item, InventoryLedgerEntryModel)
    )
    assert archive_ledger.event_type is InventoryLedgerEventType.ARCHIVED
    assert archive_ledger.quantity_delta == 0.0


@pytest.mark.anyio
async def test_adjustment_locks_current_batch_and_keeps_ledger_in_sync() -> None:
    """A manual deduction updates status and ledger from the same locked balance."""
    batch = InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="Home-made sauce",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=2.0,
        current_quantity=2.0,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    database = FakeDatabaseSession([FakeResult(None), FakeResult(batch)])
    service = InventoryService(cast(AsyncSession, database))

    response = await service.adjust_batch(
        USER_ID,
        BATCH_ID,
        InventoryAdjustmentRequestDTO(
            event_type=InventoryLedgerEventType.MANUAL_ADJUSTMENT,
            quantity_delta=-2.0,
            reason="Consumed manually",
        ),
        "consume-1",
    )

    ledger = next(
        item for item in database.added if isinstance(item, InventoryLedgerEntryModel)
    )
    assert response.current_quantity == 0.0
    assert response.status is InventoryBatchStatus.DEPLETED
    assert ledger.quantity_before == 2.0
    assert ledger.quantity_delta == -2.0
    assert ledger.quantity_after == 0.0
    assert database.commit_count == 1
    assert database.refreshed == [batch]
    locked_statement = cast(Select[tuple[InventoryBatchModel]], database.statements[1])
    compiled = str(locked_statement)
    assert "FOR UPDATE" in compiled


@pytest.mark.anyio
async def test_unknown_or_cross_user_batch_returns_non_disclosing_not_found() -> None:
    """Ownership is applied inside the query and does not disclose other users."""
    database = FakeDatabaseSession([FakeResult(None)])
    service = InventoryService(cast(AsyncSession, database))

    with pytest.raises(InventoryBatchNotFoundError):
        await service.get_batch(USER_ID, BATCH_ID)


@pytest.mark.anyio
async def test_adjustment_retry_returns_current_batch_without_second_write() -> None:
    """A repeated idempotency key cannot duplicate its quantity or ledger change."""
    batch = InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="Home-made sauce",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=2.0,
        current_quantity=1.0,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    database = FakeDatabaseSession([FakeResult(batch)])
    service = InventoryService(cast(AsyncSession, database))

    response = await service.adjust_batch(
        USER_ID,
        BATCH_ID,
        InventoryAdjustmentRequestDTO(
            event_type=InventoryLedgerEventType.MANUAL_ADJUSTMENT,
            quantity_delta=-1.0,
            reason="Repeated request",
        ),
        "already-applied",
    )

    assert response.current_quantity == 1.0
    assert database.commit_count == 0
    assert not database.added


@pytest.mark.anyio
async def test_summary_converts_compatible_batches_to_catalog_unit() -> None:
    """Aggregate quantities convert to one canonical unit without merging batches."""
    ingredient_id = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b204")
    ingredient = MasterIngredientModel(
        id=ingredient_id,
        name="Spinach",
        description="Leafy vegetable",
        category_id=UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b205"),
        canonical_unit=MeasurementUnit.KG,
        default_storage_mode=StorageMode.REFRIGERATED,
        other_nutrients={},
    )
    gram_batch = InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=ingredient_id,
        custom_name=None,
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=500.0,
        current_quantity=500.0,
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=1),
        expiration_source=ExpirationSource.MANUFACTURER,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    kilogram_batch = InventoryBatchModel(
        id=UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b206"),
        user_id=USER_ID,
        master_ingredient_id=ingredient_id,
        custom_name=None,
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=1.0,
        current_quantity=1.0,
        unit=MeasurementUnit.KG,
        storage_mode=StorageMode.FROZEN,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=10),
        expiration_source=ExpirationSource.MANUFACTURER,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    database = FakeDatabaseSession(
        [FakeResult([gram_batch, kilogram_batch]), FakeResult([ingredient])]
    )
    service = InventoryService(cast(AsyncSession, database), warning_days=3)

    response = await service.get_summary(USER_ID)

    assert len(response.items) == 1
    assert response.items[0].quantity == 1.5
    assert response.items[0].unit is MeasurementUnit.KG
    assert response.items[0].batch_count == 2
    assert response.items[0].expiring_soon_count == 1


@pytest.mark.anyio
async def test_summary_groups_compatible_custom_ingredient_units() -> None:
    """Custom batches with the same name aggregate across compatible mass units."""
    gram_batch = InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="Garden tomato",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=500.0,
        current_quantity=500.0,
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    kilogram_batch = InventoryBatchModel(
        id=UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b207"),
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="garden TOMATO",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=1.0,
        current_quantity=1.0,
        unit=MeasurementUnit.KG,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )
    database = FakeDatabaseSession([FakeResult([gram_batch, kilogram_batch])])
    service = InventoryService(cast(AsyncSession, database))

    response = await service.get_summary(USER_ID)

    assert len(response.items) == 1
    assert response.items[0].quantity == 1500.0
    assert response.items[0].unit is MeasurementUnit.GRAM
    assert response.items[0].batch_count == 2
