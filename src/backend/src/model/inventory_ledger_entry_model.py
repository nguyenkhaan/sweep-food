"""Immutable inventory ledger database model."""

from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import InventoryLedgerEventType, MeasurementUnit


class InventoryLedgerEntryModel(CreatedAtUUIDModel):
    """Append-only audit record for one inventory quantity mutation."""

    __tablename__ = "inventory_ledger_entries"
    __table_args__ = (
        CheckConstraint(
            "quantity_after = quantity_before + quantity_delta",
            name="inventory_ledger_quantity_arithmetic",
        ),
        UniqueConstraint(
            "user_id",
            "idempotency_key",
            "inventory_batch_id",
            "event_type",
            name="uq_inventory_ledger_idempotent_batch_event",
        ),
        Index(
            "uq_inventory_ledger_initial_stock_key",
            "user_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text(
                "idempotency_key IS NOT NULL AND event_type = 'INITIAL_STOCK'"
            ),
        ),
        Index(
            "ix_inventory_ledger_batch_created",
            "inventory_batch_id",
            "created_at",
        ),
        Index(
            "ix_inventory_ledger_user_created",
            "user_id",
            "created_at",
        ),
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
    event_type: Mapped[InventoryLedgerEventType] = mapped_column(
        SQLEnum(InventoryLedgerEventType, name="inventory_ledger_event_type"),
        nullable=False,
    )
    quantity_before: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_delta: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_after: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    cooking_session_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("cooking_sessions.id"),
        nullable=True,
    )
    idempotency_key: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
