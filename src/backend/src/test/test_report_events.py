"""Unit tests for immutable waste-reduction evidence snapshots."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest

from src.model.enum_model import (
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
from src.model.waste_reduction_event_model import WasteReductionEventModel
from src.module.reports.report_service import (
    METRIC_VERSION,
    capture_waste_reduction_snapshot,
    stage_waste_reduction_events,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a101")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a102")
LEDGER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a103")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a104")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a105")

CONSUMED_AT = datetime(2026, 9, 1, 5, tzinfo=UTC)


class FakeDatabaseSession:
    """Capture staged ORM instances without a database transaction."""

    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, instance: object) -> None:
        """Record one staged instance."""
        self.added.append(instance)


def build_batch(
    *,
    batch_type: InventoryBatchType = InventoryBatchType.RAW_INGREDIENT,
    unit: MeasurementUnit = MeasurementUnit.GRAM,
    expires_at: datetime | None = CONSUMED_AT + timedelta(days=2),
) -> InventoryBatchModel:
    """Build a batch whose snapshot fields are easy to assert."""
    return InventoryBatchModel(
        id=BATCH_ID,
        user_id=USER_ID,
        master_ingredient_id=INGREDIENT_ID,
        batch_type=batch_type,
        initial_quantity=500.0,
        current_quantity=500.0,
        unit=unit,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=expires_at,
        expiration_source=ExpirationSource.MANUFACTURER,
        source=(
            InventorySource.LEFTOVER
            if batch_type is InventoryBatchType.COOKED_FOOD
            else InventorySource.MANUAL
        ),
        source_cooking_session_id=(
            SESSION_ID if batch_type is InventoryBatchType.COOKED_FOOD else None
        ),
    )


def build_ledger(
    *,
    unit: MeasurementUnit = MeasurementUnit.GRAM,
    quantity_delta: float = -500.0,
) -> InventoryLedgerEntryModel:
    """Build one flushed cooking-consumption ledger row."""
    return InventoryLedgerEntryModel(
        id=LEDGER_ID,
        user_id=USER_ID,
        inventory_batch_id=BATCH_ID,
        event_type=InventoryLedgerEventType.COOKING_CONSUMPTION,
        quantity_before=500.0,
        quantity_delta=quantity_delta,
        quantity_after=0.0,
        unit=unit,
        cooking_session_id=SESSION_ID,
        idempotency_key="report-event-test",
        reason="Cooking session completion",
    )


@pytest.mark.parametrize(
    ("batch_type", "expires_at", "unit", "expected_reason", "expected_mass"),
    [
        (
            InventoryBatchType.RAW_INGREDIENT,
            CONSUMED_AT + timedelta(days=3),
            MeasurementUnit.GRAM,
            None,
            Decimal("0.5"),
        ),
        (
            InventoryBatchType.COOKED_FOOD,
            None,
            MeasurementUnit.LITER,
            "COOKED_FOOD",
            None,
        ),
        (
            InventoryBatchType.RAW_INGREDIENT,
            None,
            MeasurementUnit.KG,
            "UNKNOWN_EXPIRATION",
            Decimal(500),
        ),
        (
            InventoryBatchType.RAW_INGREDIENT,
            CONSUMED_AT - timedelta(days=1),
            MeasurementUnit.KG,
            "EXPIRED",
            Decimal(500),
        ),
        (
            InventoryBatchType.RAW_INGREDIENT,
            CONSUMED_AT + timedelta(days=4),
            MeasurementUnit.GRAM,
            "OUTSIDE_WARNING_WINDOW",
            Decimal("0.5"),
        ),
        (
            InventoryBatchType.RAW_INGREDIENT,
            CONSUMED_AT + timedelta(days=1),
            MeasurementUnit.LITER,
            "UNSUPPORTED_UNIT",
            None,
        ),
    ],
)
def test_waste_reduction_event_uses_priority_and_snapshots(
    batch_type: InventoryBatchType,
    expires_at: datetime | None,
    unit: MeasurementUnit,
    expected_reason: str | None,
    expected_mass: Decimal | None,
) -> None:
    """Every cooking consumption receives one immutable, classified snapshot."""
    batch = build_batch(batch_type=batch_type, unit=unit, expires_at=expires_at)
    ledger = build_ledger(unit=unit)
    snapshot = capture_waste_reduction_snapshot(ledger, batch, "Tomato")

    event = snapshot.to_event(CONSUMED_AT, warning_days=3)

    assert event.inventory_ledger_entry_id == LEDGER_ID
    assert event.ingredient_name_snapshot == "Tomato"
    assert event.quantity == Decimal("500.0")
    assert event.mass_kg == expected_mass
    assert event.metric_version == METRIC_VERSION
    assert event.is_eligible is (expected_reason is None)
    assert event.exclusion_reason == expected_reason


def test_waste_reduction_snapshot_uses_local_expiry_day_boundary() -> None:
    """A batch expiring on the consumption day remains eligible in product time."""
    expires_at = datetime(2026, 8, 31, 18, tzinfo=UTC)
    snapshot = capture_waste_reduction_snapshot(
        build_ledger(),
        build_batch(expires_at=expires_at),
        "Tomato",
    )

    event = snapshot.to_event(CONSUMED_AT, warning_days=0)

    assert event.is_eligible is True
    assert event.exclusion_reason is None


def test_event_writer_stages_only_after_receiving_a_flushed_ledger() -> None:
    """The writer stages evidence in the caller transaction without committing."""
    database = FakeDatabaseSession()
    snapshot = capture_waste_reduction_snapshot(
        build_ledger(),
        build_batch(),
        "Tomato",
    )

    stage_waste_reduction_events(
        database,
        [snapshot],
        consumed_at=CONSUMED_AT,
        warning_days=3,
    )

    assert len(database.added) == 1
    event = cast(WasteReductionEventModel, database.added[0])
    assert event.cooking_session_id == SESSION_ID
