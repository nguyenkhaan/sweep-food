"""Evidence classification and aggregation for waste-reduction reports."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.model.cooking_session_model import CookingSessionModel
from src.model.enum_model import (
    CookingSessionStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    MeasurementUnit,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.model.waste_reduction_event_model import WasteReductionEventModel
from src.module.inventory.inventory_service import RecordAdder
from src.module.reports.report_dto import (
    TopSavedIngredientDTO,
    WasteReductionCoverageDTO,
    WasteReductionPeriod,
    WasteReductionReportDTO,
)

METRIC_VERSION = "near-expiry-v1"
PRODUCT_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
_OUTPUT_PRECISION = Decimal("0.001")


@dataclass(frozen=True, slots=True)
class ReportPeriodBounds:
    """One current calendar period expressed in local and UTC time."""

    start_local: datetime
    end_local: datetime
    start_utc: datetime
    end_utc: datetime


@dataclass(frozen=True, slots=True)
class WasteReductionCoverage:
    """Internal, typed coverage values collected alongside report evidence."""

    data_from: datetime | None
    missing_evidence_count: int
    unsupported_unit_count: int


@dataclass(frozen=True, slots=True)
class WasteReductionBatchSnapshot:
    """Batch metadata copied before a cooking mutation changes its balance."""

    user_id: UUID
    inventory_batch_id: UUID
    master_ingredient_id: UUID | None
    ingredient_name_snapshot: str
    batch_type_snapshot: InventoryBatchType
    unit: MeasurementUnit
    expires_at_snapshot: datetime | None

    @classmethod
    def from_batch(
        cls,
        batch: InventoryBatchModel,
        ingredient_name: str,
    ) -> "WasteReductionBatchSnapshot":
        """Copy report-relevant metadata while the locked batch is unchanged."""
        return cls(
            user_id=batch.user_id,
            inventory_batch_id=batch.id,
            master_ingredient_id=batch.master_ingredient_id,
            ingredient_name_snapshot=ingredient_name,
            batch_type_snapshot=batch.batch_type,
            unit=batch.unit,
            expires_at_snapshot=batch.expires_at,
        )

    def with_ledger(
        self,
        ledger: InventoryLedgerEntryModel,
    ) -> "WasteReductionSnapshot":
        """Attach the newly staged immutable ledger to this pre-mutation snapshot."""
        return WasteReductionSnapshot(
            inventory_ledger_entry=ledger,
            user_id=self.user_id,
            inventory_batch_id=self.inventory_batch_id,
            cooking_session_id=ledger.cooking_session_id,
            master_ingredient_id=self.master_ingredient_id,
            ingredient_name_snapshot=self.ingredient_name_snapshot,
            batch_type_snapshot=self.batch_type_snapshot,
            unit=self.unit,
            expires_at_snapshot=self.expires_at_snapshot,
        )


@dataclass(frozen=True, slots=True)
class WasteReductionSnapshot:
    """Immutable evidence inputs attached to one newly created ledger record."""

    inventory_ledger_entry: InventoryLedgerEntryModel
    user_id: UUID
    inventory_batch_id: UUID
    cooking_session_id: UUID | None
    master_ingredient_id: UUID | None
    ingredient_name_snapshot: str
    batch_type_snapshot: InventoryBatchType
    unit: MeasurementUnit
    expires_at_snapshot: datetime | None

    def to_event(
        self,
        consumed_at: datetime,
        warning_days: int,
    ) -> WasteReductionEventModel:
        """Classify this one immutable snapshot using the completion timestamp."""
        ledger_id = self.inventory_ledger_entry.id
        if ledger_id is None or self.cooking_session_id is None:
            raise ValueError("Waste-reduction evidence requires a flushed cooking ledger")
        quantity = _positive_decimal(-self.inventory_ledger_entry.quantity_delta)
        mass_kg = _mass_kg(quantity, self.unit)
        exclusion_reason = _exclusion_reason(
            batch_type=self.batch_type_snapshot,
            expires_at=self.expires_at_snapshot,
            consumed_at=consumed_at,
            warning_days=warning_days,
            mass_kg=mass_kg,
        )
        return WasteReductionEventModel(
            inventory_ledger_entry_id=ledger_id,
            user_id=self.user_id,
            inventory_batch_id=self.inventory_batch_id,
            cooking_session_id=self.cooking_session_id,
            master_ingredient_id=self.master_ingredient_id,
            ingredient_name_snapshot=self.ingredient_name_snapshot,
            batch_type_snapshot=self.batch_type_snapshot,
            quantity=quantity,
            unit=self.unit,
            mass_kg=mass_kg,
            expires_at_snapshot=self.expires_at_snapshot,
            consumed_at=consumed_at,
            warning_days=warning_days,
            metric_version=METRIC_VERSION,
            is_eligible=exclusion_reason is None,
            exclusion_reason=exclusion_reason,
        )


@dataclass(slots=True)
class _IngredientAggregate:
    """Mutable aggregation state kept local to one report response."""

    identity: str
    name: str
    mass_kg: Decimal
    latest_snapshot_key: tuple[datetime, str]


def capture_waste_reduction_snapshot(
    ledger: InventoryLedgerEntryModel,
    batch: InventoryBatchModel,
    ingredient_name: str,
) -> WasteReductionSnapshot:
    """Capture a snapshot for direct classification tests and small call sites."""
    return WasteReductionBatchSnapshot.from_batch(batch, ingredient_name).with_ledger(
        ledger,
    )


def stage_waste_reduction_events(
    db_session: RecordAdder,
    snapshots: Sequence[WasteReductionSnapshot],
    *,
    consumed_at: datetime,
    warning_days: int,
) -> None:
    """Stage all evidence rows in the caller's existing transaction."""
    for snapshot in snapshots:
        db_session.add(snapshot.to_event(consumed_at, warning_days))


def current_period_bounds(
    period: WasteReductionPeriod,
    now: datetime | None = None,
) -> ReportPeriodBounds:
    """Return the current product-calendar period with half-open UTC bounds."""
    current_utc = _as_utc(now or datetime.now(UTC))
    end_local = current_utc.astimezone(PRODUCT_TIMEZONE)
    local_day_start = end_local.replace(hour=0, minute=0, second=0, microsecond=0)
    if period is WasteReductionPeriod.WEEK:
        start_local = local_day_start - timedelta(days=local_day_start.weekday())
    elif period is WasteReductionPeriod.MONTH:
        start_local = local_day_start.replace(day=1)
    else:
        start_local = local_day_start.replace(month=1, day=1)
    return ReportPeriodBounds(
        start_local=start_local,
        end_local=end_local,
        start_utc=start_local.astimezone(UTC),
        end_utc=current_utc,
    )


def aggregate_waste_reduction_events(
    events: Sequence[WasteReductionEventModel],
    *,
    period: WasteReductionPeriod,
    bounds: ReportPeriodBounds,
    coverage: WasteReductionCoverage,
) -> WasteReductionReportDTO:
    """Build the current-period response from already scoped immutable evidence."""
    weekly_starts = _weekly_starts(bounds)
    weekly_totals = {week_start: Decimal(0) for week_start in weekly_starts}
    ingredient_totals: dict[str, _IngredientAggregate] = {}
    total_saved_kg = Decimal(0)

    for event in events:
        if not _is_event_in_bounds(event, bounds) or not event.is_eligible:
            continue
        if event.mass_kg is None:
            continue
        mass_kg = _positive_decimal(event.mass_kg)
        total_saved_kg += mass_kg
        week_start = _monday(event.consumed_at.astimezone(PRODUCT_TIMEZONE).date())
        weekly_totals[week_start] += mass_kg
        identity = _ingredient_identity(event)
        snapshot_key = (event.consumed_at, str(event.id))
        aggregate = ingredient_totals.get(identity)
        if aggregate is None:
            ingredient_totals[identity] = _IngredientAggregate(
                identity=identity,
                name=event.ingredient_name_snapshot,
                mass_kg=mass_kg,
                latest_snapshot_key=snapshot_key,
            )
            continue
        aggregate.mass_kg += mass_kg
        if snapshot_key > aggregate.latest_snapshot_key:
            aggregate.name = event.ingredient_name_snapshot
            aggregate.latest_snapshot_key = snapshot_key

    top_ingredients = sorted(
        ingredient_totals.values(),
        key=lambda value: (-value.mass_kg, value.identity),
    )[:5]
    return WasteReductionReportDTO(
        total_saved_kg=_round_kg(total_saved_kg),
        period=period,
        weekly_series=[_round_kg(weekly_totals[week_start]) for week_start in weekly_starts],
        top_saved_ingredients=[
            TopSavedIngredientDTO(
                name=ingredient.name,
                saved_kg=_round_kg(ingredient.mass_kg),
            )
            for ingredient in top_ingredients
        ],
        weekly_labels=weekly_starts,
        period_start=bounds.start_local,
        period_end=bounds.end_local,
        timezone=PRODUCT_TIMEZONE.key,
        coverage=WasteReductionCoverageDTO(
            data_from=coverage.data_from,
            missing_evidence_count=coverage.missing_evidence_count,
            unsupported_unit_count=coverage.unsupported_unit_count,
        ),
    )


class ReportService:
    """Read the current user's aggregate strictly from immutable evidence rows."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_waste_reduction(
        self,
        user_id: UUID,
        period: WasteReductionPeriod,
    ) -> WasteReductionReportDTO:
        """Return one current period with explicit historical coverage metadata."""
        bounds = current_period_bounds(period)
        try:
            event_result = await self.db_session.execute(
                select(WasteReductionEventModel)
                .where(
                    WasteReductionEventModel.user_id == user_id,
                    WasteReductionEventModel.metric_version == METRIC_VERSION,
                    WasteReductionEventModel.consumed_at >= bounds.start_utc,
                    WasteReductionEventModel.consumed_at < bounds.end_utc,
                )
                .order_by(
                    WasteReductionEventModel.consumed_at,
                    WasteReductionEventModel.id,
                ),
            )
            events = list(event_result.scalars().all())
            data_from_result = await self.db_session.execute(
                select(func.min(WasteReductionEventModel.consumed_at)).where(
                    WasteReductionEventModel.user_id == user_id,
                    WasteReductionEventModel.metric_version == METRIC_VERSION,
                ),
            )
            missing_count_result = await self.db_session.execute(
                _missing_evidence_statement(user_id, bounds),
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        coverage = WasteReductionCoverage(
            data_from=data_from_result.scalar_one_or_none(),
            missing_evidence_count=int(missing_count_result.scalar_one()),
            unsupported_unit_count=sum(event.mass_kg is None for event in events),
        )
        return aggregate_waste_reduction_events(
            events,
            period=period,
            bounds=bounds,
            coverage=coverage,
        )


def _missing_evidence_statement(
    user_id: UUID,
    bounds: ReportPeriodBounds,
):
    """Count completed cooking ledgers lacking evidence for this metric version."""
    evidence = aliased(WasteReductionEventModel)
    return (
        select(func.count(InventoryLedgerEntryModel.id))
        .select_from(InventoryLedgerEntryModel)
        .join(
            CookingSessionModel,
            CookingSessionModel.id == InventoryLedgerEntryModel.cooking_session_id,
        )
        .outerjoin(
            evidence,
            and_(
                evidence.inventory_ledger_entry_id == InventoryLedgerEntryModel.id,
                evidence.metric_version == METRIC_VERSION,
            ),
        )
        .where(
            InventoryLedgerEntryModel.user_id == user_id,
            InventoryLedgerEntryModel.event_type
            == InventoryLedgerEventType.COOKING_CONSUMPTION,
            InventoryLedgerEntryModel.quantity_delta < 0,
            CookingSessionModel.status == CookingSessionStatus.COMPLETED,
            CookingSessionModel.completed_at >= bounds.start_utc,
            CookingSessionModel.completed_at < bounds.end_utc,
            evidence.id.is_(None),
        )
    )


def _exclusion_reason(
    *,
    batch_type: InventoryBatchType,
    expires_at: datetime | None,
    consumed_at: datetime,
    warning_days: int,
    mass_kg: Decimal | None,
) -> str | None:
    """Apply metric-v1 exclusion priority using local calendar expiry dates."""
    if warning_days < 0:
        raise ValueError("warning_days must be non-negative")
    if batch_type is InventoryBatchType.COOKED_FOOD:
        return "COOKED_FOOD"
    if expires_at is None:
        return "UNKNOWN_EXPIRATION"
    local_consumed_date = _as_utc(consumed_at).astimezone(PRODUCT_TIMEZONE).date()
    local_expiry_date = _as_utc(expires_at).astimezone(PRODUCT_TIMEZONE).date()
    if local_expiry_date < local_consumed_date:
        return "EXPIRED"
    if local_expiry_date > local_consumed_date + timedelta(days=warning_days):
        return "OUTSIDE_WARNING_WINDOW"
    if mass_kg is None:
        return "UNSUPPORTED_UNIT"
    return None


def _mass_kg(quantity: Decimal, unit: MeasurementUnit) -> Decimal | None:
    """Convert only the two mass units defined by metric v1."""
    if unit is MeasurementUnit.KG:
        return quantity
    if unit is MeasurementUnit.GRAM:
        return quantity / Decimal(1000)
    return None


def _positive_decimal(value: Decimal | float) -> Decimal:
    """Reject non-finite or non-positive numeric snapshots before persistence."""
    normalized = Decimal(str(value))
    if not normalized.is_finite() or normalized <= 0:
        raise ValueError("Waste-reduction quantity must be finite and positive")
    return normalized


def _as_utc(value: datetime) -> datetime:
    """Reject naive timestamps before using them for persistence or reporting."""
    if value.tzinfo is None:
        raise ValueError("Waste-reduction timestamps must be timezone-aware")
    return value.astimezone(UTC)


def _weekly_starts(bounds: ReportPeriodBounds) -> list[date]:
    """List Monday labels for every started week intersecting the period."""
    start_week = _monday(bounds.start_local.date())
    end_week = _monday(bounds.end_local.date())
    weeks: list[date] = []
    current_week = start_week
    while current_week <= end_week:
        weeks.append(current_week)
        current_week += timedelta(days=7)
    return weeks


def _monday(value: date) -> date:
    """Return the Monday label for a product-calendar date."""
    return value - timedelta(days=value.weekday())


def _is_event_in_bounds(
    event: WasteReductionEventModel,
    bounds: ReportPeriodBounds,
) -> bool:
    """Keep aggregate callers safe if an unscoped event list is passed in tests."""
    consumed_at = _as_utc(event.consumed_at)
    return bounds.start_utc <= consumed_at < bounds.end_utc


def _ingredient_identity(event: WasteReductionEventModel) -> str:
    """Use catalog identity when present and a stable snapshot fallback otherwise."""
    if event.master_ingredient_id is not None:
        return f"ingredient:{event.master_ingredient_id}"
    return f"snapshot:{event.ingredient_name_snapshot.casefold()}"


def _round_kg(value: Decimal) -> Decimal:
    """Round public kilogram values to the nearest gram only at output time."""
    return value.quantize(_OUTPUT_PRECISION, rounding=ROUND_HALF_UP).normalize()
