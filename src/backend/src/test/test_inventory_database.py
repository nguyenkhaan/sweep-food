"""PostgreSQL integration tests for Phase 4 inventory safety invariants."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql.functions import count

from src.model.enum_model import (
    AccountStatus,
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
    UserRole,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.user_model import UserModel
from src.module.inventory.inventory_dto import InventoryAdjustmentRequestDTO
from src.module.inventory.inventory_service import InventoryService


def _user() -> UserModel:
    """Build a unique active user for a disposable integration database."""
    suffix = str(uuid4().int)[-9:]
    return UserModel(
        phone_e164=f"+84{suffix}",
        phone_verified_at=datetime.now(UTC),
        password_hash="integration-test-hash",
        role=UserRole.USER,
        status=AccountStatus.ACTIVE,
        preferences={},
    )


def _batch(
    user_id: UUID,
    quantity: float = 100.0,
    *,
    current_quantity: float | None = None,
) -> InventoryBatchModel:
    """Build a valid active custom batch."""
    return InventoryBatchModel(
        user_id=user_id,
        master_ingredient_id=None,
        custom_name=f"Concurrency ingredient {uuid4().hex}",
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=quantity,
        current_quantity=(
            quantity if current_quantity is None else current_quantity
        ),
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
    )


@pytest.mark.anyio
async def test_database_rejects_active_batch_with_zero_quantity(
    database_engine: AsyncEngine,
) -> None:
    """The lifecycle check constraint rejects inconsistent persisted state."""
    async with AsyncSession(database_engine) as session:
        user = _user()
        session.add(user)
        await session.flush()
        session.add(_batch(user.id, current_quantity=0.0))

        with pytest.raises(IntegrityError):
            await session.flush()
        await session.rollback()


@pytest.mark.anyio
async def test_database_rejects_inventory_ledger_update(
    database_engine: AsyncEngine,
) -> None:
    """The database trigger makes prior inventory history immutable."""
    async with AsyncSession(database_engine) as session:
        user = _user()
        session.add(user)
        await session.flush()
        batch = _batch(user.id)
        session.add(batch)
        await session.flush()
        ledger = InventoryLedgerEntryModel(
            user_id=user.id,
            inventory_batch_id=batch.id,
            event_type=InventoryLedgerEventType.INITIAL_STOCK,
            quantity_before=0.0,
            quantity_delta=100.0,
            quantity_after=100.0,
            unit=MeasurementUnit.GRAM,
            idempotency_key=f"immutable-{uuid4().hex}",
            reason="Initial stock",
        )
        session.add(ledger)
        await session.flush()

        with pytest.raises(DBAPIError):
            await session.execute(
                update(InventoryLedgerEntryModel)
                .where(InventoryLedgerEntryModel.id == ledger.id)
                .values(reason="Changed history")
            )
            await session.flush()
        await session.rollback()


@pytest.mark.anyio
async def test_concurrent_adjustments_never_double_consume(
    database_engine: AsyncEngine,
) -> None:
    """Row locking lets one competing deduction win without negative stock."""
    async with AsyncSession(database_engine, expire_on_commit=False) as setup:
        user = _user()
        setup.add(user)
        await setup.flush()
        batch = _batch(user.id)
        setup.add(batch)
        await setup.flush()
        setup.add(
            InventoryLedgerEntryModel(
                user_id=user.id,
                inventory_batch_id=batch.id,
                event_type=InventoryLedgerEventType.INITIAL_STOCK,
                quantity_before=0.0,
                quantity_delta=100.0,
                quantity_after=100.0,
                unit=MeasurementUnit.GRAM,
                idempotency_key=f"concurrency-create-{uuid4().hex}",
                reason="Initial stock",
            )
        )
        await setup.commit()
        user_id = user.id
        batch_id = batch.id

    async def deduct(idempotency_key: str) -> object:
        async with AsyncSession(database_engine) as session:
            service = InventoryService(session)
            return await service.adjust_batch(
                user_id,
                batch_id,
                InventoryAdjustmentRequestDTO(
                    event_type=InventoryLedgerEventType.MANUAL_ADJUSTMENT,
                    quantity_delta=-80.0,
                    reason="Concurrent deduction",
                ),
                idempotency_key,
            )

    outcomes = await asyncio.gather(
        deduct(f"concurrency-a-{uuid4().hex}"),
        deduct(f"concurrency-b-{uuid4().hex}"),
        return_exceptions=True,
    )

    assert sum(not isinstance(outcome, Exception) for outcome in outcomes) == 1
    async with AsyncSession(database_engine) as verification:
        quantity = await verification.scalar(
            select(InventoryBatchModel.current_quantity).where(
                InventoryBatchModel.id == batch_id
            )
        )
        ledger_count = await verification.scalar(
            select(count())
            .select_from(InventoryLedgerEntryModel)
            .where(
                InventoryLedgerEntryModel.inventory_batch_id == batch_id,
                InventoryLedgerEntryModel.event_type
                == InventoryLedgerEventType.MANUAL_ADJUSTMENT,
            )
        )

    assert quantity == 20.0
    assert ledger_count == 1
