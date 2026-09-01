"""Inventory batch database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
)


class InventoryBatchModel(TimestampedUUIDModel):
    """A distinct user-owned ingredient or leftover batch."""

    __tablename__ = "inventory_batches"
    __table_args__ = (
        CheckConstraint(
            "(master_ingredient_id IS NULL) <> (custom_name IS NULL)",
            name="inventory_batch_exactly_one_identity",
        ),
        CheckConstraint(
            "initial_quantity > 0", name="inventory_batch_initial_positive"
        ),
        CheckConstraint(
            "current_quantity >= 0",
            name="inventory_batch_current_nonnegative",
        ),
        CheckConstraint(
            "(status = 'ACTIVE' AND current_quantity > 0 AND archived_at IS NULL) "
            "OR (status IN ('DEPLETED', 'DISCARDED') "
            "AND current_quantity = 0 AND archived_at IS NULL) "
            "OR (status = 'ARCHIVED' AND archived_at IS NOT NULL)",
            name="inventory_batch_status_quantity_consistent",
        ),
        CheckConstraint(
            "(batch_type = 'RAW_INGREDIENT' AND source = 'MANUAL' "
            "AND source_cooking_session_id IS NULL) "
            "OR (batch_type = 'COOKED_FOOD' AND source = 'LEFTOVER' "
            "AND source_cooking_session_id IS NOT NULL)",
            name="inventory_batch_source_type_consistent",
        ),
        Index("ix_inventory_batches_status_expires_at", "status", "expires_at"),
        Index(
            "ix_inventory_batches_user_fefo",
            "user_id",
            "status",
            "expires_at",
            "created_at",
        ),
        Index(
            "ix_inventory_batches_user_ingredient",
            "user_id",
            "master_ingredient_id",
        ),
        Index(
            "ix_inventory_batches_user_storage",
            "user_id",
            "storage_mode",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    master_ingredient_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=True,
    )
    custom_name: Mapped[str | None] = mapped_column(String, nullable=True)
    batch_type: Mapped[InventoryBatchType] = mapped_column(
        SQLEnum(InventoryBatchType, name="inventory_batch_type"),
        nullable=False,
    )
    initial_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    current_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    storage_mode: Mapped[StorageMode] = mapped_column(
        SQLEnum(StorageMode, name="storage_mode"),
        nullable=False,
    )
    status: Mapped[InventoryBatchStatus] = mapped_column(
        SQLEnum(InventoryBatchStatus, name="inventory_batch_status"),
        nullable=False,
    )
    purchased_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    packaged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stored_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expiration_source: Mapped[ExpirationSource] = mapped_column(
        SQLEnum(ExpirationSource, name="expiration_source"),
        nullable=False,
    )
    unit_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[InventorySource] = mapped_column(
        SQLEnum(InventorySource, name="inventory_source"),
        nullable=False,
    )
    source_cooking_session_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("cooking_sessions.id"),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
