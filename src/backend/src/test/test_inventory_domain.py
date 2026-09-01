"""Unit tests for inventory shelf-life and freshness calculations."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

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
from src.model.shelf_life_rule_model import ShelfLifeRuleModel
from src.module.inventory.inventory_dto import (
    CreateInventoryBatchRequestDTO,
    FreshnessState,
)
from src.module.inventory.inventory_service import (
    InventoryConflictError,
    InventoryQuantityChange,
    apply_quantity_change,
    calculate_freshness,
    choose_shelf_life_rule,
    resolve_expiration,
)

INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b001")
CATEGORY_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b002")
USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b003")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b004")


class FakeAddSession:
    """Capture records added by a pure transactional mutation helper."""

    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, record: object) -> None:
        """Capture one staged ORM record."""
        self.added.append(record)


def _active_batch(quantity: float = 500.0) -> InventoryBatchModel:
    return InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=INGREDIENT_ID,
        custom_name=None,
        batch_type=InventoryBatchType.RAW_INGREDIENT,
        initial_quantity=quantity,
        current_quantity=quantity,
        unit=MeasurementUnit.GRAM,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expiration_source=ExpirationSource.UNKNOWN,
        source=InventorySource.MANUAL,
    )


def test_manufacturer_expiration_is_never_replaced_by_an_estimate() -> None:
    """Manufacturer information remains authoritative when a rule exists."""
    now = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)
    manufacturer_expiration = now + timedelta(days=2)

    expires_at, source = resolve_expiration(
        manufacturer_expires_at=manufacturer_expiration,
        stored_at=now,
        purchased_at=now,
        shelf_life_days=10,
        now=now,
    )

    assert expires_at == manufacturer_expiration
    assert source is ExpirationSource.MANUFACTURER


def test_estimated_expiration_uses_stored_then_purchased_then_current_time() -> None:
    """The most inventory-specific known date anchors a shelf-life estimate."""
    now = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)
    purchased_at = now - timedelta(days=2)
    stored_at = now - timedelta(days=1)

    stored_expiration, stored_source = resolve_expiration(
        manufacturer_expires_at=None,
        stored_at=stored_at,
        purchased_at=purchased_at,
        shelf_life_days=4,
        now=now,
    )
    purchased_expiration, _ = resolve_expiration(
        manufacturer_expires_at=None,
        stored_at=None,
        purchased_at=purchased_at,
        shelf_life_days=4,
        now=now,
    )
    current_expiration, _ = resolve_expiration(
        manufacturer_expires_at=None,
        stored_at=None,
        purchased_at=None,
        shelf_life_days=4,
        now=now,
    )

    assert stored_expiration == stored_at + timedelta(days=4)
    assert purchased_expiration == purchased_at + timedelta(days=4)
    assert current_expiration == now + timedelta(days=4)
    assert stored_source is ExpirationSource.ESTIMATED


def test_missing_rule_produces_unknown_expiration() -> None:
    """The backend does not invent a hard-coded shelf life without seed data."""
    now = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)

    expires_at, source = resolve_expiration(
        manufacturer_expires_at=None,
        stored_at=now,
        purchased_at=None,
        shelf_life_days=None,
        now=now,
    )

    assert expires_at is None
    assert source is ExpirationSource.UNKNOWN


def test_freshness_boundaries_use_the_configured_warning_window() -> None:
    """Expiry states are deterministic at the exact boundary instants."""
    now = datetime(2026, 9, 1, 9, 0, tzinfo=UTC)

    assert calculate_freshness(None, now, warning_days=3) is FreshnessState.UNKNOWN
    assert (
        calculate_freshness(now - timedelta(microseconds=1), now, warning_days=3)
        is FreshnessState.EXPIRED
    )
    assert calculate_freshness(now, now, warning_days=3) is FreshnessState.EXPIRING_SOON
    assert (
        calculate_freshness(now + timedelta(days=3), now, warning_days=3)
        is FreshnessState.EXPIRING_SOON
    )
    assert (
        calculate_freshness(
            now + timedelta(days=3, microseconds=1),
            now,
            warning_days=3,
        )
        is FreshnessState.SAFE
    )


def test_ingredient_rule_takes_precedence_over_category_rule() -> None:
    """The narrowest seeded rule controls estimation for a catalog ingredient."""
    category_rule = ShelfLifeRuleModel(
        scope=ShelfLifeRuleScope.CATEGORY,
        master_ingredient_id=None,
        category_id=CATEGORY_ID,
        storage_mode=StorageMode.REFRIGERATED,
        min_days=3,
        max_days=5,
        default_days=4,
    )
    ingredient_rule = ShelfLifeRuleModel(
        scope=ShelfLifeRuleScope.INGREDIENT,
        master_ingredient_id=INGREDIENT_ID,
        category_id=None,
        storage_mode=StorageMode.REFRIGERATED,
        min_days=1,
        max_days=2,
        default_days=2,
    )

    selected = choose_shelf_life_rule(
        [category_rule, ingredient_rule],
        master_ingredient_id=INGREDIENT_ID,
    )

    assert selected is ingredient_rule


def test_quantity_change_updates_batch_and_creates_matching_ledger() -> None:
    """Inventory and ledger arithmetic use one shared mutation implementation."""
    batch = _active_batch()
    database = FakeAddSession()

    ledger = apply_quantity_change(
        database,
        batch,
        InventoryQuantityChange(
            user_id=USER_ID,
            quantity_delta=-200.0,
            event_type=InventoryLedgerEventType.MANUAL_ADJUSTMENT,
            idempotency_key="adjust-1",
            reason="Used for lunch",
        ),
    )

    assert batch.current_quantity == 300.0
    assert batch.status is InventoryBatchStatus.ACTIVE
    assert database.added == [ledger]
    assert isinstance(ledger, InventoryLedgerEntryModel)
    assert ledger.quantity_before == 500.0
    assert ledger.quantity_delta == -200.0
    assert ledger.quantity_after == 300.0
    assert ledger.reason == "Used for lunch"


def test_quantity_change_rejects_negative_stock_without_mutation() -> None:
    """A stale or invalid deduction cannot partially change batch state."""
    batch = _active_batch(quantity=100.0)
    database = FakeAddSession()

    with pytest.raises(InventoryConflictError):
        apply_quantity_change(
            database,
            batch,
            InventoryQuantityChange(
                user_id=USER_ID,
                quantity_delta=-101.0,
                event_type=InventoryLedgerEventType.MANUAL_ADJUSTMENT,
                idempotency_key="adjust-2",
                reason="Too much",
            ),
        )

    assert batch.current_quantity == 100.0
    assert batch.status is InventoryBatchStatus.ACTIVE
    assert not database.added


def test_discard_consumes_full_balance_and_sets_discarded_status() -> None:
    """Discarding preserves the batch while removing it from usable stock."""
    batch = _active_batch(quantity=100.0)
    database = FakeAddSession()

    apply_quantity_change(
        database,
        batch,
        InventoryQuantityChange(
            user_id=USER_ID,
            quantity_delta=-100.0,
            event_type=InventoryLedgerEventType.DISCARDED,
            idempotency_key="discard-1",
            reason="Spoiled",
        ),
    )

    assert batch.current_quantity == 0.0
    assert batch.status is InventoryBatchStatus.DISCARDED


def test_inventory_dates_must_include_a_timezone() -> None:
    """Naive client dates cannot shift shelf-life calculations by server locale."""
    with pytest.raises(ValidationError):
        CreateInventoryBatchRequestDTO(
            custom_name="Milk",
            quantity=1.0,
            unit=MeasurementUnit.LITER,
            storage_mode=StorageMode.REFRIGERATED,
            expires_at=datetime.fromisoformat("2026-09-03T09:00:00"),
        )
