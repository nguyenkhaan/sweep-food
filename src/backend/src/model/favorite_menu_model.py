"""Favorite recipe menu database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel

if TYPE_CHECKING:
    from src.model.favorite_menu_item_model import FavoriteMenuItemModel
    from src.model.user_model import UserModel


class FavoriteMenuModel(TimestampedUUIDModel):
    """A user-named set of favorite recipes."""

    __tablename__ = "favorite_menus"
    __table_args__ = (
        Index("ix_favorite_menus_user_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    user: Mapped["UserModel"] = relationship(back_populates="favorite_menus")
    items: Mapped[list["FavoriteMenuItemModel"]] = relationship(
        back_populates="favorite_menu",
    )
