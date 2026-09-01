"""Request and response DTOs for manual inventory batch management."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.model.enum_model import (
    ExpirationSource,
    InventoryBatchStatus,
    MeasurementUnit,
    ShelfLifeRuleScope,
    StorageMode,
)
from src.service.shelf_life_service import FreshnessState

_MAX_TEXT_LENGTH = 1_000


class _StrictRequestDTO(BaseModel):
    """Reject unsupported fields instead of silently accepting later-task commands."""

    model_config = ConfigDict(extra="forbid")


class _BatchIdentityRequestDTO(_StrictRequestDTO):
    """The one required identity for a manually entered batch."""

    master_ingredient_id: UUID | None = None
    custom_name: Annotated[str | None, Field(max_length=255)] = None

    @field_validator("custom_name")
    @classmethod
    def normalize_custom_name(cls, value: str | None) -> str | None:
        """Trim supplied custom identities and reject blank values."""
        if value is None:
            return None
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("custom_name must not be blank")
        return normalized_value

    @model_validator(mode="after")
    def require_exactly_one_identity(self) -> "_BatchIdentityRequestDTO":
        """Require exactly one catalog or custom identity on creation."""
        if (self.master_ingredient_id is None) == (self.custom_name is None):
            raise ValueError(
                "Exactly one of master_ingredient_id and custom_name is required",
            )
        return self


class CreateInventoryBatchRequestDTO(_BatchIdentityRequestDTO):
    """Fields accepted when a user manually records an ingredient batch."""

    quantity: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    unit: MeasurementUnit
    storage_mode: StorageMode
    purchased_at: datetime | None = None
    packaged_at: datetime | None = None
    stored_at: datetime | None = None
    manufacturer_expires_at: datetime | None = None
    expiration_override_at: datetime | None = None
    unit_cost: Annotated[float | None, Field(ge=0, allow_inf_nan=False)] = None
    note: Annotated[str | None, Field(max_length=_MAX_TEXT_LENGTH)] = None
    media_url: Annotated[str | None, Field(max_length=2_048)] = None

    @field_validator(
        "purchased_at",
        "packaged_at",
        "stored_at",
        "manufacturer_expires_at",
        "expiration_override_at",
    )
    @classmethod
    def require_aware_dates(cls, value: datetime | None) -> datetime | None:
        """Persist only unambiguous timestamps."""
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_expiration_authority(self) -> "CreateInventoryBatchRequestDTO":
        """Keep a manufacturer date authoritative over a separate override input."""
        if (
            self.manufacturer_expires_at is not None
            and self.expiration_override_at is not None
        ):
            raise ValueError(
                "manufacturer_expires_at and expiration_override_at cannot both be set",
            )
        future_limit = datetime.now(UTC)
        for name in ("purchased_at", "packaged_at", "stored_at"):
            value = getattr(self, name)
            if value is not None and value > future_limit:
                raise ValueError(f"{name} cannot be in the future")
        return self


class UpdateInventoryBatchRequestDTO(_StrictRequestDTO):
    """Metadata-only patch for an existing manual batch.

    Quantity, lifecycle status, source, and batch type deliberately belong to later
    inventory commands and are rejected as unknown fields by this strict DTO.
    """

    master_ingredient_id: UUID | None = None
    custom_name: Annotated[str | None, Field(max_length=255)] = None
    unit: MeasurementUnit | None = None
    storage_mode: StorageMode | None = None
    purchased_at: datetime | None = None
    packaged_at: datetime | None = None
    stored_at: datetime | None = None
    manufacturer_expires_at: datetime | None = None
    expiration_override_at: datetime | None = None
    unit_cost: Annotated[float | None, Field(ge=0, allow_inf_nan=False)] = None
    note: Annotated[str | None, Field(max_length=_MAX_TEXT_LENGTH)] = None
    media_url: Annotated[str | None, Field(max_length=2_048)] = None

    @field_validator("custom_name")
    @classmethod
    def normalize_custom_name(cls, value: str | None) -> str | None:
        """Trim non-empty custom identities before patch application."""
        if value is None:
            return None
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("custom_name must not be blank")
        return normalized_value

    @field_validator(
        "purchased_at",
        "packaged_at",
        "stored_at",
        "manufacturer_expires_at",
        "expiration_override_at",
    )
    @classmethod
    def require_aware_dates(cls, value: datetime | None) -> datetime | None:
        """Persist only unambiguous timestamps."""
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def reject_future_acquisition_dates(self) -> "UpdateInventoryBatchRequestDTO":
        """Reject impossible acquisition timestamps when a patch supplies them."""
        future_limit = datetime.now(UTC)
        for name in ("purchased_at", "packaged_at", "stored_at"):
            value = getattr(self, name)
            if value is not None and value > future_limit:
                raise ValueError(f"{name} cannot be in the future")
        return self


class IngredientIdentityDTO(BaseModel):
    """A concise public catalog identity embedded in a batch response."""

    id: UUID
    name: str
    category_id: UUID
    category_name: str


class AppliedShelfLifeRuleDTO(BaseModel):
    """Rule metadata explaining an estimated expiration, when applicable."""

    scope: ShelfLifeRuleScope
    storage_mode: StorageMode
    default_days: int


class InventoryBatchDTO(BaseModel):
    """One independently addressable user-owned inventory batch."""

    id: UUID
    master_ingredient: IngredientIdentityDTO | None
    custom_name: str | None
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
    freshness_state: FreshnessState
    applied_shelf_life_rule: AppliedShelfLifeRuleDTO | None
    unit_cost: float | None
    note: str | None
    media_url: str | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None


class InventoryBatchListResponseDTO(BaseModel):
    """A deterministically ordered page of user-owned batch records."""

    items: list[InventoryBatchDTO]
    total: int
    page: int
    per_page: int


class InventoryBatchListQueryDTO(BaseModel):
    """Validated query parameters for a stable inventory batch list page."""

    master_ingredient_id: UUID | None = None
    category_id: UUID | None = None
    storage_mode: StorageMode | None = None
    status: InventoryBatchStatus | None = None
    freshness_state: FreshnessState | None = None
    expires_from: datetime | None = None
    expires_to: datetime | None = None
    page: Annotated[int, Field(ge=1)] = 1
    per_page: Annotated[int, Field(ge=1, le=100)] = 20

    @field_validator("expires_from", "expires_to")
    @classmethod
    def require_aware_expiration_filters(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        """Keep date-range comparison unambiguous at the database boundary."""
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("expiration filters must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_expiration_range(self) -> "InventoryBatchListQueryDTO":
        """Reject an inverted filter range before issuing a database query."""
        if (
            self.expires_from is not None
            and self.expires_to is not None
            and self.expires_from > self.expires_to
        ):
            raise ValueError("expires_from must not be after expires_to")
        return self
