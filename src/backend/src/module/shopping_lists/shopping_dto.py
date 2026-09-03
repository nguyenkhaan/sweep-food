"""Request and response DTOs for shopping lists and purchase confirmation."""

from datetime import datetime
from math import isfinite
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.model.enum_model import MeasurementUnit, ShoppingListStatus, StorageMode


def _require_timezone(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("Datetime values must include a timezone")
    return value


class GenerateShoppingListRequestDTO(BaseModel):
    """Generate one shopping list from an owned meal plan."""

    model_config = ConfigDict(extra="forbid")

    meal_plan_id: UUID


class CreateShoppingItemRequestDTO(BaseModel):
    """Add one manual reminder item that does not yet change inventory."""

    model_config = ConfigDict(extra="forbid")

    master_ingredient_id: UUID | None = None
    custom_name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: float = Field(gt=0)
    unit: MeasurementUnit
    estimated_cost: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_identity_and_quantity(self) -> "CreateShoppingItemRequestDTO":
        """Keep manual items identifiable and quantities safe to persist."""
        if (self.master_ingredient_id is None) == (self.custom_name is None):
            raise ValueError(
                "Provide exactly one of master_ingredient_id or custom_name"
            )
        if not isfinite(self.quantity) or (
            self.estimated_cost is not None and not isfinite(self.estimated_cost)
        ):
            raise ValueError("Numeric values must be finite")
        if self.custom_name is not None:
            self.custom_name = self.custom_name.strip()
            if not self.custom_name:
                raise ValueError("custom_name must not be blank")
        return self


class ShoppingPurchaseDTO(BaseModel):
    """Batch metadata needed when a bought item enters inventory."""

    model_config = ConfigDict(extra="forbid")

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
        """Reject dates whose storage meaning depends on server locale."""
        return _require_timezone(value)

    @field_validator("unit_cost")
    @classmethod
    def validate_unit_cost(cls, value: float | None) -> float | None:
        """Reject non-finite costs before storing an inventory batch."""
        if value is not None and not isfinite(value):
            raise ValueError("unit_cost must be finite")
        return value


class UpdateShoppingListItemRequestDTO(BaseModel):
    """Check a purchased item or edit one unchecked manual reminder."""

    model_config = ConfigDict(extra="forbid")

    checked: bool | None = None
    quantity: float | None = Field(default=None, gt=0)
    estimated_cost: float | None = Field(default=None, ge=0)
    purchase: ShoppingPurchaseDTO | None = None

    @field_validator("quantity", "estimated_cost")
    @classmethod
    def validate_number(cls, value: float | None) -> float | None:
        """Reject infinity and NaN in values held by float columns."""
        if value is not None and not isfinite(value):
            raise ValueError("Numeric values must be finite")
        return value

    @model_validator(mode="after")
    def validate_change(self) -> "UpdateShoppingListItemRequestDTO":
        """Require a change and batch metadata for a purchase confirmation."""
        if not self.model_fields_set:
            raise ValueError("Provide at least one item field to update")
        if self.checked is True and self.purchase is None:
            raise ValueError("purchase is required when checked is true")
        if self.purchase is not None and self.checked is not True:
            raise ValueError("purchase is allowed only when checked is true")
        return self


class ShoppingListItemDTO(BaseModel):
    """Public state and stock traceability of one shopping line."""

    id: UUID
    master_ingredient_id: UUID | None
    custom_name: str | None
    name: str
    required_quantity: float
    available_quantity: float
    missing_quantity: float
    unit: MeasurementUnit
    estimated_cost: float | None
    is_checked: bool
    is_generated: bool
    source_recipe_ids: list[str]
    inventory_batch_id: UUID | None


class ShoppingListDTO(BaseModel):
    """A user-owned list generated from a meal plan or managed manually."""

    id: UUID
    meal_plan_id: UUID | None
    status: ShoppingListStatus
    generated_at: datetime | None
    items: list[ShoppingListItemDTO]
