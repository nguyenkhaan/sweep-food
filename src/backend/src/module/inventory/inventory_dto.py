"""Request and response DTOs for inventory APIs."""

from datetime import datetime
from enum import Enum
from math import isfinite
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventoryLedgerEventType,
    InventorySource,
    MeasurementUnit,
    StorageMode,
)


class FreshnessState(str, Enum):
    """Shelf-life state calculated at read time."""

    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    SAFE = "SAFE"
    UNKNOWN = "UNKNOWN"


def _require_timezone(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("Datetime values must include a timezone")
    return value


class CreateInventoryBatchRequestDTO(BaseModel):
    """Create one independently tracked raw-ingredient batch."""

    model_config = ConfigDict(extra="forbid")

    master_ingredient_id: UUID | None = None
    custom_name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: float = Field(gt=0)
    unit: MeasurementUnit
    storage_mode: StorageMode
    purchased_at: datetime | None = None
    packaged_at: datetime | None = None
    stored_at: datetime | None = None
    expires_at: datetime | None = None
    unit_cost: float | None = Field(default=None, ge=0)
    note: str | None = Field(default=None, max_length=1000)
    media_url: str | None = Field(default=None, max_length=2048)

    @field_validator("purchased_at", "packaged_at", "stored_at", "expires_at")
    @classmethod
    def validate_datetime_timezone(cls, value: datetime | None) -> datetime | None:
        """Reject dates whose meaning changes with server locale."""
        return _require_timezone(value)

    @model_validator(mode="after")
    def validate_identity_and_numbers(self) -> "CreateInventoryBatchRequestDTO":
        """Require one identity and reject non-finite database quantities."""
        if (self.master_ingredient_id is None) == (self.custom_name is None):
            raise ValueError(
                "Provide exactly one of master_ingredient_id or custom_name"
            )
        if not isfinite(self.quantity) or (
            self.unit_cost is not None and not isfinite(self.unit_cost)
        ):
            raise ValueError("Numeric values must be finite")
        if self.custom_name is not None:
            self.custom_name = self.custom_name.strip()
            if not self.custom_name:
                raise ValueError("custom_name must not be blank")
        return self


class UpdateInventoryBatchRequestDTO(BaseModel):
    """Update mutable metadata without changing a batch identity or balance."""

    model_config = ConfigDict(extra="forbid")

    purchased_at: datetime | None = None
    packaged_at: datetime | None = None
    stored_at: datetime | None = None
    expires_at: datetime | None = None
    unit_cost: float | None = Field(default=None, ge=0)
    note: str | None = Field(default=None, max_length=1000)
    media_url: str | None = Field(default=None, max_length=2048)
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("purchased_at", "packaged_at", "stored_at", "expires_at")
    @classmethod
    def validate_datetime_timezone(cls, value: datetime | None) -> datetime | None:
        """Reject dates whose meaning changes with server locale."""
        return _require_timezone(value)

    @model_validator(mode="after")
    def validate_update(self) -> "UpdateInventoryBatchRequestDTO":
        """Require a real auditable metadata change and finite costs."""
        if self.unit_cost is not None and not isfinite(self.unit_cost):
            raise ValueError("unit_cost must be finite")
        if not (self.model_fields_set - {"reason"}):
            raise ValueError("Provide at least one inventory field to update")
        return self


class InventoryAdjustmentRequestDTO(BaseModel):
    """Apply one explicit, auditable quantity mutation."""

    model_config = ConfigDict(extra="forbid")

    event_type: InventoryLedgerEventType
    quantity_delta: float | None = None
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_adjustment(self) -> "InventoryAdjustmentRequestDTO":
        """Restrict clients to supported manual inventory operations."""
        allowed = {
            InventoryLedgerEventType.MANUAL_ADJUSTMENT,
            InventoryLedgerEventType.CORRECTION,
            InventoryLedgerEventType.DISCARDED,
        }
        if self.event_type not in allowed:
            raise ValueError("event_type is not a manual inventory operation")
        if self.event_type is InventoryLedgerEventType.DISCARDED:
            if self.quantity_delta is not None:
                raise ValueError("DISCARDED always consumes the full batch")
        elif (
            self.quantity_delta is None
            or not isfinite(self.quantity_delta)
            or self.quantity_delta == 0
        ):
            raise ValueError("quantity_delta must be a finite non-zero value")
        return self


class ConsumeInventoryBatchRequestDTO(BaseModel):
    """Consume a positive quantity expressed in the batch's stored unit."""

    model_config = ConfigDict(extra="forbid")

    quantity: float = Field(gt=0)
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: float) -> float:
        """Reject infinities that PostgreSQL floating columns could retain."""
        if not isfinite(value):
            raise ValueError("quantity must be finite")
        return value


class MoveInventoryBatchRequestDTO(BaseModel):
    """Move a batch to a new storage mode."""

    model_config = ConfigDict(extra="forbid")

    storage_mode: StorageMode
    reason: str = Field(min_length=1, max_length=500)


class InventoryBatchQueryDTO(BaseModel):
    """Filters and pagination for batch listing."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    batch_status: InventoryBatchStatus | None = Field(default=None, alias="status")
    storage_mode: StorageMode | None = None
    master_ingredient_id: UUID | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class InventoryLedgerQueryDTO(BaseModel):
    """Filters and pagination for immutable inventory history."""

    model_config = ConfigDict(extra="forbid")

    batch_id: UUID | None = None
    event_type: InventoryLedgerEventType | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @field_validator("created_from", "created_to")
    @classmethod
    def validate_datetime_timezone(cls, value: datetime | None) -> datetime | None:
        """Reject ambiguous ledger time filters."""
        return _require_timezone(value)


class InventoryBatchDTO(BaseModel):
    """Public state of one user-owned inventory batch."""

    id: UUID
    master_ingredient_id: UUID | None
    custom_name: str | None
    ingredient_name: str
    batch_type: InventoryBatchType
    initial_quantity: float
    current_quantity: float
    unit: MeasurementUnit
    storage_mode: StorageMode
    status: InventoryBatchStatus
    purchased_at: datetime | None
    packaged_at: datetime | None
    stored_at: datetime | None
    expires_at: datetime | None
    expiration_source: ExpirationSource
    freshness: FreshnessState
    unit_cost: float | None
    note: str | None
    media_url: str | None
    source: InventorySource
    source_cooking_session_id: UUID | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None


class InventoryBatchListResponseDTO(BaseModel):
    """Stable page of independently addressable batches."""

    items: list[InventoryBatchDTO]
    total: int
    page: int
    per_page: int


class InventoryBatchSummaryDTO(BaseModel):
    """Compatible active quantities grouped without erasing batch detail."""

    master_ingredient_id: UUID | None
    custom_name: str | None
    ingredient_name: str
    quantity: float
    unit: MeasurementUnit
    batch_count: int
    expiring_soon_count: int
    expired_count: int


class InventorySummaryResponseDTO(BaseModel):
    """Current aggregate inventory view."""

    items: list[InventoryBatchSummaryDTO]


class InventoryLedgerEntryDTO(BaseModel):
    """One immutable quantity-change record."""

    id: UUID
    inventory_batch_id: UUID
    event_type: InventoryLedgerEventType
    quantity_before: float
    quantity_delta: float
    quantity_after: float
    unit: MeasurementUnit
    cooking_session_id: UUID | None
    idempotency_key: str | None
    reason: str | None
    created_at: datetime


class InventoryLedgerListResponseDTO(BaseModel):
    """Stable page of inventory history."""

    items: list[InventoryLedgerEntryDTO]
    total: int
    page: int
    per_page: int
