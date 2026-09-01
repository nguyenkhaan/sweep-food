"""PostgreSQL integration coverage for Task 4.1 inventory persistence."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from decimal import Decimal
from typing import TypedDict, Unpack
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import selectinload

from src.model.cooking_session_model import CookingSessionModel
from src.model.enum_model import (
    CookingSessionStatus,
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
)
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_model import RecipeModel
from src.model.user_model import UserModel


@pytest.fixture(name="inventory_session")
async def _inventory_session(
    database_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a savepoint-backed session and roll back every test's data."""
    async with database_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


def _unique_value(prefix: str) -> str:
    """Return a test-local value that cannot collide with another test invocation."""
    return f"{prefix}-{uuid4().hex}"


def _user() -> UserModel:
    """Build a minimum valid user for inventory ownership tests."""
    return UserModel(
        phone_e164=f"+84{uuid4().int % 10**10:010d}",
        password_hash="inventory-test-password-hash",
    )


class _BatchOverrides(TypedDict, total=False):
    """Optional values that differ from the standard valid manual batch."""

    master_ingredient_id: UUID | None
    custom_name: str | None
    current_quantity: float
    status: InventoryBatchStatus
    expires_at: datetime | None
    expiration_source: ExpirationSource


def _batch(
    user_id: UUID,
    **overrides: Unpack[_BatchOverrides],
) -> InventoryBatchModel:
    """Build a manual raw-ingredient batch with explicit lifecycle values."""
    return InventoryBatchModel(
        user_id=user_id,
        master_ingredient_id=overrides.get("master_ingredient_id"),
        custom_name=overrides.get("custom_name"),
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=1.0,
        current_quantity=overrides.get("current_quantity", 1.0),
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=overrides.get("status", InventoryBatchStatus.ACTIVE),
        expires_at=overrides.get("expires_at"),
        expiration_source=overrides.get(
            "expiration_source",
            ExpirationSource.UNKNOWN,
        ),
        source=InventorySource.MANUAL,
    )


async def _owned_ingredient(
    session: AsyncSession,
) -> tuple[UserModel, MasterIngredientModel]:
    """Persist one user and catalog ingredient for an inventory test."""
    user = _user()
    category = IngredientCategoryModel(name=_unique_value("Inventory category"))
    ingredient = MasterIngredientModel(
        name=_unique_value("Inventory ingredient"),
        description="Inventory persistence test ingredient.",
        category=category,
        canonical_unit=MeasurementUnit.GRAM,
    )
    session.add_all([user, ingredient])
    await session.flush()
    return user, ingredient


@pytest.mark.anyio
async def test_batch_identity_and_lifecycle_constraints(
    inventory_session: AsyncSession,
) -> None:
    """Enforce identity, non-negative quantity, and depleted balance invariants."""
    user, ingredient = await _owned_ingredient(inventory_session)

    inventory_session.add_all(
        [
            _batch(user.id, master_ingredient_id=ingredient.id),
            _batch(user.id, custom_name=_unique_value("Custom ingredient")),
            _batch(
                user.id,
                master_ingredient_id=ingredient.id,
                current_quantity=0.0,
                status=InventoryBatchStatus.DEPLETED,
            ),
        ],
    )
    await inventory_session.flush()

    invalid_batches = (
        _batch(user.id),
        _batch(
            user.id,
            master_ingredient_id=ingredient.id,
            custom_name="Duplicate identity",
        ),
        _batch(user.id, custom_name="   "),
        _batch(user.id, master_ingredient_id=ingredient.id, current_quantity=-0.001),
        _batch(
            user.id,
            master_ingredient_id=ingredient.id,
            current_quantity=0.0,
            status=InventoryBatchStatus.ACTIVE,
        ),
        _batch(
            user.id,
            master_ingredient_id=ingredient.id,
            current_quantity=0.5,
            status=InventoryBatchStatus.DEPLETED,
        ),
    )
    for invalid_batch in invalid_batches:
        with pytest.raises(IntegrityError):
            async with inventory_session.begin_nested():
                inventory_session.add(invalid_batch)
                await inventory_session.flush()


@pytest.mark.anyio
async def test_expiration_source_requires_the_matching_expiration_date(
    inventory_session: AsyncSession,
) -> None:
    """Persist only UNKNOWN/null and known-source/non-null expiration combinations."""
    user, ingredient = await _owned_ingredient(inventory_session)
    manufacturer_expiry = datetime.now(UTC)

    inventory_session.add(
        _batch(
            user.id,
            master_ingredient_id=ingredient.id,
            expires_at=manufacturer_expiry,
            expiration_source=ExpirationSource.MANUFACTURER,
        ),
    )
    await inventory_session.flush()

    for invalid_batch in (
        _batch(
            user.id,
            master_ingredient_id=ingredient.id,
            expires_at=manufacturer_expiry,
            expiration_source=ExpirationSource.UNKNOWN,
        ),
        _batch(
            user.id,
            master_ingredient_id=ingredient.id,
            expiration_source=ExpirationSource.ESTIMATED,
        ),
    ):
        with pytest.raises(IntegrityError):
            async with inventory_session.begin_nested():
                inventory_session.add(invalid_batch)
                await inventory_session.flush()


@pytest.mark.anyio
async def test_ledger_persists_quantity_context_and_relationships(
    inventory_session: AsyncSession,
) -> None:
    """Persist a complete ledger event and load its inventory ownership graph."""
    user, ingredient = await _owned_ingredient(inventory_session)
    recipe = RecipeModel(
        name=_unique_value("Inventory context recipe"),
        description="Inventory ledger context recipe.",
        instructions={"steps": []},
        default_servings=Decimal("1.00"),
        estimated_cooking_minutes=10,
        tags={"values": []},
    )
    batch = _batch(
        user.id,
        master_ingredient_id=ingredient.id,
        current_quantity=0.5,
    )
    inventory_session.add_all([recipe, batch])
    await inventory_session.flush()
    cooking_session = CookingSessionModel(
        user_id=user.id,
        recipe_id=recipe.id,
        servings=1.0,
        status=CookingSessionStatus.PLANNED,
    )
    inventory_session.add(cooking_session)
    await inventory_session.flush()
    ledger_entry = InventoryLedgerEntryModel(
        user_id=user.id,
        inventory_batch_id=batch.id,
        event_type=InventoryLedgerEventType.COOKING_CONSUMPTION,
        quantity_before=1.0,
        quantity_delta=-0.5,
        quantity_after=0.5,
        unit=MeasurementUnit.GRAM,
        cooking_session_id=cooking_session.id,
        idempotency_key=_unique_value("inventory-operation"),
    )
    inventory_session.add(ledger_entry)
    await inventory_session.flush()
    batch_id, ledger_entry_id = batch.id, ledger_entry.id
    inventory_session.expunge_all()

    stored_batch = await inventory_session.scalar(
        select(InventoryBatchModel)
        .where(InventoryBatchModel.id == batch_id)
        .options(
            selectinload(InventoryBatchModel.master_ingredient),
            selectinload(InventoryBatchModel.user),
            selectinload(InventoryBatchModel.ledger_entries).selectinload(
                InventoryLedgerEntryModel.user,
            ),
        ),
    )
    stored_entry = await inventory_session.get(
        InventoryLedgerEntryModel, ledger_entry_id
    )

    assert stored_batch is not None
    assert stored_entry is not None
    assert stored_batch.master_ingredient is not None
    assert stored_batch.master_ingredient.id == ingredient.id
    assert stored_batch.user.id == user.id
    assert len(stored_batch.ledger_entries) == 1
    assert stored_batch.ledger_entries[0].id == ledger_entry_id
    assert stored_entry.inventory_batch.id == batch_id
    assert stored_entry.user.id == user.id
    assert stored_entry.quantity_before == 1.0
    assert stored_entry.quantity_delta == -0.5
    assert stored_entry.quantity_after == 0.5
    assert stored_entry.cooking_session_id == cooking_session.id
    assert stored_entry.idempotency_key == ledger_entry.idempotency_key


@pytest.mark.anyio
async def test_ledger_rejects_invalid_arithmetic_and_cross_user_ownership(
    inventory_session: AsyncSession,
) -> None:
    """Keep ledger arithmetic non-negative and bind every entry to the batch owner."""
    user, ingredient = await _owned_ingredient(inventory_session)
    other_user = _user()
    batch = _batch(user.id, master_ingredient_id=ingredient.id)
    inventory_session.add_all([other_user, batch])
    await inventory_session.flush()

    for entry in (
        InventoryLedgerEntryModel(
            user_id=user.id,
            inventory_batch_id=batch.id,
            event_type=InventoryLedgerEventType.INITIAL_STOCK,
            quantity_before=1.0,
            quantity_delta=-0.5,
            quantity_after=0.75,
            unit=MeasurementUnit.GRAM,
        ),
        InventoryLedgerEntryModel(
            user_id=other_user.id,
            inventory_batch_id=batch.id,
            event_type=InventoryLedgerEventType.INITIAL_STOCK,
            quantity_before=0.0,
            quantity_delta=1.0,
            quantity_after=1.0,
            unit=MeasurementUnit.GRAM,
        ),
    ):
        with pytest.raises(IntegrityError):
            async with inventory_session.begin_nested():
                inventory_session.add(entry)
                await inventory_session.flush()


@pytest.mark.anyio
async def test_ledger_rows_cannot_be_updated_or_deleted(
    inventory_session: AsyncSession,
) -> None:
    """Use the database trigger to reject edits and deletion of ledger history."""
    user, ingredient = await _owned_ingredient(inventory_session)
    batch = _batch(user.id, master_ingredient_id=ingredient.id)
    inventory_session.add(batch)
    await inventory_session.flush()
    entry = InventoryLedgerEntryModel(
        user_id=user.id,
        inventory_batch_id=batch.id,
        event_type=InventoryLedgerEventType.INITIAL_STOCK,
        quantity_before=0.0,
        quantity_delta=1.0,
        quantity_after=1.0,
        unit=MeasurementUnit.GRAM,
    )
    inventory_session.add(entry)
    await inventory_session.flush()

    with pytest.raises(DBAPIError, match="inventory ledger entries are immutable"):
        async with inventory_session.begin_nested():
            await inventory_session.execute(
                update(InventoryLedgerEntryModel)
                .where(InventoryLedgerEntryModel.id == entry.id)
                .values(idempotency_key="rewritten"),
            )

    with pytest.raises(DBAPIError, match="inventory ledger entries are immutable"):
        async with inventory_session.begin_nested():
            await inventory_session.execute(
                delete(InventoryLedgerEntryModel).where(
                    InventoryLedgerEntryModel.id == entry.id,
                ),
            )
