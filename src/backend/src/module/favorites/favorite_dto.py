"""Request and response DTOs for the authenticated favourites module."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _normalized_name(value: str) -> str:
    """Keep favourite-menu names meaningful after whitespace is removed."""
    normalized = value.strip()
    if not normalized:
        raise ValueError("name must not be blank")
    return normalized


def _normalized_description(value: str | None) -> str | None:
    """Store an omitted or blank menu description as null."""
    if value is None:
        return None
    return value.strip() or None


class FavoriteRecipeDTO(BaseModel):
    """Confirm whether a recipe is saved for the current user."""

    recipe_id: UUID
    is_favorite: bool


class FavoriteRecipeListItemDTO(BaseModel):
    """A saved recipe with enough card data to render a favourites list."""

    recipe_id: UUID
    recipe_name: str
    recipe_description: str
    media_url: str | None
    created_at: datetime


class FavoriteRecipeListDTO(BaseModel):
    """A bounded page of saved recipes."""

    items: list[FavoriteRecipeListItemDTO]
    total: int
    limit: int
    offset: int


class CreateFavoriteMenuRequestDTO(BaseModel):
    """Create one named group of saved recipes."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Reject names that contain only whitespace."""
        return _normalized_name(value)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        """Avoid persisting empty descriptions."""
        return _normalized_description(value)


class UpdateFavoriteMenuRequestDTO(BaseModel):
    """Change the name and/or description of an owned favourite menu."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        """Reject blank replacement names while allowing an omitted field."""
        return _normalized_name(value) if value is not None else None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        """Normalize a supplied menu description."""
        return _normalized_description(value)

    @model_validator(mode="after")
    def validate_change(self) -> "UpdateFavoriteMenuRequestDTO":
        """Require an actual field to update."""
        if not self.model_fields_set:
            raise ValueError("Provide name or description to update")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name must not be null")
        return self


class FavoriteMenuDTO(BaseModel):
    """A named owned favourite menu without its recipe entries."""

    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class FavoriteMenuListDTO(BaseModel):
    """A bounded page of named favourite menus."""

    items: list[FavoriteMenuDTO]
    total: int
    limit: int
    offset: int


class CreateFavoriteMenuItemRequestDTO(BaseModel):
    """Add one recipe to an owned favourite menu."""

    model_config = ConfigDict(extra="forbid")

    recipe_id: UUID


class UpdateFavoriteMenuItemRequestDTO(BaseModel):
    """Replace the recipe represented by one favourite-menu item."""

    model_config = ConfigDict(extra="forbid")

    recipe_id: UUID


class FavoriteMenuItemDTO(BaseModel):
    """One recipe entry in a favourite menu, in creation order."""

    id: UUID
    recipe_id: UUID
    recipe_name: str
    recipe_description: str
    media_url: str | None
    created_at: datetime


class FavoriteMenuDetailDTO(FavoriteMenuDTO):
    """A favourite menu together with all of its saved recipes."""

    items: list[FavoriteMenuItemDTO]
