"""Focused aggregation tests for the waste-reduction report."""

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from src.model.enum_model import InventoryBatchType, MeasurementUnit
from src.model.waste_reduction_event_model import WasteReductionEventModel
from src.module.reports import report_service
from src.module.reports.report_dto import WasteReductionPeriod
from src.module.reports.report_service import (
    METRIC_VERSION,
    ReportService,
    WasteReductionCoverage,
    aggregate_waste_reduction_events,
    current_period_bounds,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a111")
INGREDIENT_A_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a112")
INGREDIENT_B_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a113")


class FakeEventResult:
    """Expose the scalar collection shape returned by the event query."""

    def __init__(self, events: list[WasteReductionEventModel]) -> None:
        self.events = events

    def scalars(self) -> "FakeEventResult":
        """Return the scalar collection wrapper."""
        return self

    def all(self) -> list[WasteReductionEventModel]:
        """Return all fixture events."""
        return self.events


class FakeScalarResult:
    """Expose scalar result methods used by report coverage queries."""

    def __init__(self, value: datetime | int | None) -> None:
        self.value = value

    def scalar_one_or_none(self) -> datetime | None:
        """Return a nullable earliest-evidence timestamp."""
        assert self.value is None or isinstance(self.value, datetime)
        return self.value

    def scalar_one(self) -> int:
        """Return the non-null count selected by SQL COUNT."""
        assert isinstance(self.value, int)
        return self.value


class FakeReportDatabase:
    """Queue report query results and retain statements for scope assertions."""

    def __init__(
        self,
        results: list[FakeEventResult | FakeScalarResult],
    ) -> None:
        self.results = results
        self.statements: list[object] = []

    async def execute(self, statement: object) -> FakeEventResult | FakeScalarResult:
        """Return the next deterministic result for one service query."""
        self.statements.append(statement)
        return self.results.pop(0)

    async def rollback(self) -> None:
        """Satisfy the AsyncSession surface; successful reads do not roll back."""


def build_event(
    *,
    event_id: int,
    consumed_at: datetime,
    name: str,
    ingredient_id: UUID | None,
    mass_kg: Decimal | None,
    is_eligible: bool,
) -> WasteReductionEventModel:
    """Build a report event already scoped to the requested metric version."""
    return WasteReductionEventModel(
        id=UUID(f"018f0f90-26e6-7ce7-8f61-{event_id:012d}"),
        inventory_ledger_entry_id=UUID(
            f"018f0f90-26e6-7ce7-8f62-{event_id:012d}"
        ),
        user_id=USER_ID,
        inventory_batch_id=UUID(f"018f0f90-26e6-7ce7-8f63-{event_id:012d}"),
        cooking_session_id=UUID(f"018f0f90-26e6-7ce7-8f64-{event_id:012d}"),
        master_ingredient_id=ingredient_id,
        ingredient_name_snapshot=name,
        batch_type_snapshot=InventoryBatchType.RAW_INGREDIENT,
        quantity=Decimal(1),
        unit=MeasurementUnit.KG,
        mass_kg=mass_kg,
        expires_at_snapshot=consumed_at,
        consumed_at=consumed_at,
        warning_days=3,
        metric_version="near-expiry-v1",
        is_eligible=is_eligible,
        exclusion_reason=None if is_eligible else "UNSUPPORTED_UNIT",
    )


@pytest.mark.parametrize(
    ("period", "expected_start"),
    [
        (WasteReductionPeriod.WEEK, datetime(2026, 8, 30, 17, tzinfo=UTC)),
        (WasteReductionPeriod.MONTH, datetime(2026, 8, 31, 17, tzinfo=UTC)),
        (WasteReductionPeriod.YEAR, datetime(2025, 12, 31, 17, tzinfo=UTC)),
    ],
)
def test_current_period_bounds_use_vietnam_calendar_boundaries(
    period: WasteReductionPeriod,
    expected_start: datetime,
) -> None:
    """Week, month, and year all start in Asia/Ho_Chi_Minh before UTC querying."""
    now = datetime(2026, 9, 3, 5, tzinfo=UTC)

    bounds = current_period_bounds(period, now)

    assert bounds.start_utc == expected_start
    assert bounds.end_utc == now


def test_aggregate_uses_all_eligible_mass_but_returns_only_top_five() -> None:
    """The response keeps M7 fields while adding deterministic coverage metadata."""
    now = datetime(2026, 9, 3, 5, tzinfo=UTC)
    bounds = current_period_bounds(WasteReductionPeriod.MONTH, now)
    response = aggregate_waste_reduction_events(
        [
            build_event(
                event_id=1,
                consumed_at=datetime(2026, 9, 1, 1, tzinfo=UTC),
                name="Tomato",
                ingredient_id=INGREDIENT_A_ID,
                mass_kg=Decimal("0.5"),
                is_eligible=True,
            ),
            build_event(
                event_id=2,
                consumed_at=datetime(2026, 9, 2, 1, tzinfo=UTC),
                name="Tomato ripe",
                ingredient_id=INGREDIENT_A_ID,
                mass_kg=Decimal("1.0"),
                is_eligible=True,
            ),
            build_event(
                event_id=3,
                consumed_at=datetime(2026, 9, 2, 2, tzinfo=UTC),
                name="Spinach",
                ingredient_id=INGREDIENT_B_ID,
                mass_kg=Decimal("0.1014"),
                is_eligible=True,
            ),
            build_event(
                event_id=4,
                consumed_at=datetime(2026, 9, 2, 3, tzinfo=UTC),
                name="Milk",
                ingredient_id=None,
                mass_kg=None,
                is_eligible=False,
            ),
        ],
        period=WasteReductionPeriod.MONTH,
        bounds=bounds,
        coverage=WasteReductionCoverage(
            data_from=datetime(2026, 9, 1, 1, tzinfo=UTC),
            missing_evidence_count=2,
            unsupported_unit_count=1,
        ),
    )

    assert response.total_saved_kg == Decimal("1.601")
    assert response.weekly_series == [Decimal("1.601")]
    assert response.weekly_labels == [date(2026, 8, 31)]
    assert response.top_saved_ingredients[0].name == "Tomato ripe"
    assert response.top_saved_ingredients[0].saved_kg == Decimal("1.5")
    assert response.coverage.missing_evidence_count == 2
    assert response.coverage.unsupported_unit_count == 1


def test_empty_period_returns_zero_series_for_every_started_week() -> None:
    """No evidence remains an honest 200-shaped response rather than mock data."""
    now = datetime(2026, 9, 10, 5, tzinfo=UTC)
    bounds = current_period_bounds(WasteReductionPeriod.MONTH, now)

    response = aggregate_waste_reduction_events(
        [],
        period=WasteReductionPeriod.MONTH,
        bounds=bounds,
        coverage=WasteReductionCoverage(None, 0, 0),
    )

    assert response.total_saved_kg == Decimal(0)
    assert response.weekly_series == [Decimal(0), Decimal(0)]
    assert response.top_saved_ingredients == []


@pytest.mark.anyio
async def test_report_service_queries_only_current_user_and_metric_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Database aggregation never accepts an event from another user or version."""
    now = datetime(2026, 9, 3, 5, tzinfo=UTC)
    bounds = current_period_bounds(WasteReductionPeriod.MONTH, now)
    database = FakeReportDatabase(
        [
            FakeEventResult(
                [
                    build_event(
                        event_id=9,
                        consumed_at=datetime(2026, 9, 2, 1, tzinfo=UTC),
                        name="Tomato",
                        ingredient_id=INGREDIENT_A_ID,
                        mass_kg=Decimal("0.5"),
                        is_eligible=True,
                    ),
                ]
            ),
            FakeScalarResult(datetime(2026, 9, 1, 1, tzinfo=UTC)),
            FakeScalarResult(3),
        ]
    )
    monkeypatch.setattr(
        report_service,
        "current_period_bounds",
        lambda _period: bounds,
    )

    response = await ReportService(cast(AsyncSession, database)).get_waste_reduction(
        USER_ID,
        WasteReductionPeriod.MONTH,
    )

    first_statement = cast(ClauseElement, database.statements[0])
    first_query_parameters = first_statement.compile().params
    assert USER_ID in first_query_parameters.values()
    assert METRIC_VERSION in first_query_parameters.values()
    assert response.total_saved_kg == Decimal("0.5")
    assert response.coverage.missing_evidence_count == 3
