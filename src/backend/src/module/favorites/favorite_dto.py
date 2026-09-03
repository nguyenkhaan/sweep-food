"""Response DTOs for recipe favourite mutations."""

from uuid import UUID

from pydantic import BaseModel


class FavoriteRecipeDTO(BaseModel):
    """Confirm whether a recipe is saved for the current user."""

    recipe_id: UUID
    is_favorite: bool
