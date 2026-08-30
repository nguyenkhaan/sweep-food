"""Favorite menu item database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel


class FavoriteMenuItemModel(CreatedAtUUIDModel):
    """A recipe entry in a favorite menu."""

    __tablename__ = "favorite_menu_items"
    __table_args__ = (UniqueConstraint("favorite_menu_id", "recipe_id"),)

    favorite_menu_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("favorite_menus.id"),
        nullable=False,
    )
    recipe_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )
