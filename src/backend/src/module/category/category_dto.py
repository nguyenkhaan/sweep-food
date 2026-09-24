"""Request and response DTOs for ingredient categories."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateCategoryRequestDTO(BaseModel):
    """Create one ingredient category."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=2000)


class UpdateCategoryRequestDTO(BaseModel):
    """Update only explicitly supplied category fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_validator(mode="after")
    def validate_update(self) -> "UpdateCategoryRequestDTO":
        """Require a change and preserve the non-nullable category name."""
        if not self.model_fields_set:
            raise ValueError("Provide at least one category field to update")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Category name cannot be null")
        return self


class CategoryDTO(BaseModel):
    """Public ingredient category information."""

    id: UUID
    name: str
    description: str | None
