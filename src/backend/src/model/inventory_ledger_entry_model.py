"""Immutable inventory ledger database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import InventoryLedgerEventType, MeasurementUnit

if TYPE_CHECKING:
    from src.model.inventory_batch_model import InventoryBatchModel
    from src.model.user_model import UserModel


class InventoryLedgerEntryModel(CreatedAtUUIDModel):
    """Append-only audit record for one inventory quantity mutation."""

    __tablename__ = "inventory_ledger_entries"
    __table_args__ = (
        CheckConstraint("quantity_after = quantity_before + quantity_delta"),
        CheckConstraint(
            "quantity_before >= 0 AND quantity_after >= 0",
            name="inventory_ledger_entry_nonnegative_balances",
        ),
        ForeignKeyConstraint(
            ["inventory_batch_id", "user_id"],
            ["inventory_batches.id", "inventory_batches.user_id"],
            name="inventory_ledger_entries_batch_owner_fk",
        ),
        Index(
            "ix_inventory_ledger_entries_inventory_batch_id_created_at",
            "inventory_batch_id",
            "created_at",
        ),
        Index(
            "ix_inventory_ledger_entries_user_id_created_at",
            "user_id",
            "created_at",
        ),
        Index(
            "uq_inventory_ledger_entries_idempotency_context",
            "user_id",
            "idempotency_key",
            "inventory_batch_id",
            "event_type",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
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
    user: Mapped["UserModel"] = relationship(back_populates="inventory_ledger_entries")
    inventory_batch: Mapped["InventoryBatchModel"] = relationship(
        back_populates="ledger_entries",
        foreign_keys=[inventory_batch_id],
    )
