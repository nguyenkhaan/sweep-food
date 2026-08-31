"""Unit tests for reusable FEFO preview allocation logic."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.model.enum_model import MeasurementUnit
from src.service.fefo_service import FEFOCandidate, FEFOService

EARLY_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a001")
LATER_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a002")
EXPIRED_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a003")
UNKNOWN_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a004")
INCOMPATIBLE_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a005")


def test_fefo_prefers_expiring_compatible_batches_and_reports_warnings() -> None:
    """FEFO excludes expired stock and allocates dated stock before unknown expiry."""
    now = datetime(2026, 8, 31, 10, 0, tzinfo=UTC)
    service = FEFOService()

    result = service.allocate(
        required_quantity=750.0,
        required_unit=MeasurementUnit.ML,
        candidates=[
            FEFOCandidate(
                batch_id=LATER_BATCH_ID,
                current_quantity=0.5,
                unit=MeasurementUnit.LITER,
                expires_at=now + timedelta(days=2),
                created_at=now - timedelta(days=2),
            ),
            FEFOCandidate(
                batch_id=UNKNOWN_BATCH_ID,
                current_quantity=1.0,
                unit=MeasurementUnit.LITER,
                expires_at=None,
                created_at=now - timedelta(days=4),
            ),
            FEFOCandidate(
                batch_id=EARLY_BATCH_ID,
                current_quantity=0.5,
                unit=MeasurementUnit.LITER,
                expires_at=now + timedelta(days=1),
                created_at=now - timedelta(days=1),
            ),
            FEFOCandidate(
                batch_id=EXPIRED_BATCH_ID,
                current_quantity=1.0,
                unit=MeasurementUnit.LITER,
                expires_at=now - timedelta(days=1),
                created_at=now - timedelta(days=5),
            ),
            FEFOCandidate(
                batch_id=INCOMPATIBLE_BATCH_ID,
                current_quantity=1.0,
                unit=MeasurementUnit.KG,
                expires_at=now + timedelta(days=1),
                created_at=now - timedelta(days=3),
            ),
        ],
        now=now,
    )

    assert [allocation.batch_id for allocation in result.allocations] == [
        EARLY_BATCH_ID,
        LATER_BATCH_ID,
    ]
    assert [allocation.batch_quantity for allocation in result.allocations] == [
        0.5,
        0.25,
    ]
    assert result.missing_quantity == 0.0
    assert [candidate.batch_id for candidate in result.expired_candidates] == [
        EXPIRED_BATCH_ID,
    ]
    assert [
        candidate.batch_id for candidate in result.unknown_expiration_candidates
    ] == [
        UNKNOWN_BATCH_ID,
    ]
    assert [candidate.batch_id for candidate in result.incompatible_candidates] == [
        INCOMPATIBLE_BATCH_ID,
    ]
