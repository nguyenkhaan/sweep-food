"""Request DTOs for master ingredient and storage management."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.model.enum_model import MeasurementUnit, StorageMode


class UpdateIngredientDTO(BaseModel):
    """Patch editable catalog fields without changing category or storage policy."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    default_media_url: str | None = Field(default=None, max_length=2048)
    canonical_unit: MeasurementUnit | None = None
    calories: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    protein_g: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    fat_g: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    carbs_g: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    sugar_g: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    sodium_mg: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    other_nutrients: dict[str, object] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        """Prevent blank or null canonical names."""
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Ingredient name must not be blank")
        return value

    @model_validator(mode="after")
    def validate_update(self) -> "UpdateIngredientDTO":
        """Require a change and preserve non-nullable database fields."""
        if not self.model_fields_set:
            raise ValueError("Provide at least one ingredient field to update")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Ingredient name cannot be null")
        if "canonical_unit" in self.model_fields_set and self.canonical_unit is None:
            raise ValueError("Canonical unit cannot be null")
        if "other_nutrients" in self.model_fields_set and self.other_nutrients is None:
            raise ValueError("Other nutrients cannot be null")
        return self


class UpdateIngredientDefaultStorageDTO(BaseModel):
    """Set or clear the default storage mode for a master ingredient."""

    model_config = ConfigDict(extra="forbid")

    default_storage_mode: StorageMode | None


class AssignIngredientCategoryDTO(BaseModel):
    """Assign one existing category to a master ingredient."""

    model_config = ConfigDict(extra="forbid")

    category_id: UUID
