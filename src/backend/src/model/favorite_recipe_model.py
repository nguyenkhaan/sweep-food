"""Favorite recipe database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel

if TYPE_CHECKING:
    from src.model.recipe_model import RecipeModel
    from src.model.user_model import UserModel


class FavoriteRecipeModel(CreatedAtUUIDModel):
    """A user's saved recipe."""

    __tablename__ = "favorite_recipes"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id"),
        Index("ix_favorite_recipes_recipe_id", "recipe_id"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    recipe_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )
    user: Mapped["UserModel"] = relationship(back_populates="favorite_recipes")
    recipe: Mapped["RecipeModel"] = relationship(back_populates="favorite_recipes")
