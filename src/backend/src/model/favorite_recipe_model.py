"""Favorite recipe database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel


class FavoriteRecipeModel(CreatedAtUUIDModel):
    """A user's saved recipe."""

    __tablename__ = "favorite_recipes"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id"),)

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
