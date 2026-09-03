"""Favorite menu item database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel

if TYPE_CHECKING:
    from src.model.favorite_menu_model import FavoriteMenuModel
    from src.model.recipe_model import RecipeModel


class FavoriteMenuItemModel(CreatedAtUUIDModel):
    """A recipe entry in a favorite menu."""

    __tablename__ = "favorite_menu_items"
    __table_args__ = (
        UniqueConstraint("favorite_menu_id", "recipe_id"),
        Index("ix_favorite_menu_items_recipe_id", "recipe_id"),
    )

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
    favorite_menu: Mapped["FavoriteMenuModel"] = relationship(back_populates="items")
    recipe: Mapped["RecipeModel"] = relationship(
        back_populates="favorite_menu_items",
    )
