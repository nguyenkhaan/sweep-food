"""Immutable evidence snapshots for waste-reduction reporting."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import InventoryBatchType, MeasurementUnit


class WasteReductionEventModel(CreatedAtUUIDModel):
    """One immutable eligibility snapshot for a cooking-consumption ledger row."""

    __tablename__ = "waste_reduction_events"
    __table_args__ = (
        UniqueConstraint(
            "inventory_ledger_entry_id",
            name="uq_waste_event_ledger",
        ),
        Index("ix_waste_events_user_consumed_at", "user_id", "consumed_at"),
        CheckConstraint(
            "btrim(ingredient_name_snapshot) <> ''",
            name="waste_event_ingredient_name_nonblank",
        ),
        CheckConstraint(
            "quantity > 0 AND quantity NOT IN "
            "('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)",
            name="waste_event_quantity_positive_finite",
        ),
        CheckConstraint(
            "mass_kg IS NULL OR (mass_kg > 0 AND mass_kg NOT IN "
            "('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric))",
            name="waste_event_mass_kg_positive_finite",
        ),
        CheckConstraint(
            "warning_days >= 0",
            name="waste_event_warning_days_nonnegative",
        ),
        CheckConstraint(
            "btrim(metric_version) <> ''",
            name="waste_event_metric_version_nonblank",
        ),
        CheckConstraint(
            "(is_eligible AND mass_kg IS NOT NULL AND expires_at_snapshot IS NOT NULL "
            "AND batch_type_snapshot = 'RAW_INGREDIENT' AND exclusion_reason IS NULL) "
            "OR (NOT is_eligible AND exclusion_reason IN "
            "('COOKED_FOOD', 'UNKNOWN_EXPIRATION', 'EXPIRED', "
            "'OUTSIDE_WARNING_WINDOW', 'UNSUPPORTED_UNIT'))",
            name="waste_event_eligibility_consistent",
        ),
    )

    inventory_ledger_entry_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("inventory_ledger_entries.id"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    inventory_batch_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("inventory_batches.id"),
        nullable=False,
    )
    cooking_session_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("cooking_sessions.id"),
        nullable=False,
    )
    master_ingredient_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=True,
    )
    ingredient_name_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    batch_type_snapshot: Mapped[InventoryBatchType] = mapped_column(
        SQLEnum(InventoryBatchType, name="inventory_batch_type"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    mass_kg: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    expires_at_snapshot: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    warning_days: Mapped[int] = mapped_column(Integer, nullable=False)
    metric_version: Mapped[str] = mapped_column(String(32), nullable=False)
    is_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    exclusion_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
