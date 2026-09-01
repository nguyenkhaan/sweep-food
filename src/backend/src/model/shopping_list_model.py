"""Shopping-list database model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import ShoppingListStatus

if TYPE_CHECKING:
    from src.model.meal_plan_model import MealPlanModel
    from src.model.shopping_list_item_model import ShoppingListItemModel
    from src.model.user_model import UserModel


class ShoppingListModel(TimestampedUUIDModel):
    """A generated or manually managed shopping list."""

    __tablename__ = "shopping_lists"
    __table_args__ = (Index("ix_shopping_lists_user_status", "user_id", "status"),)

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    meal_plan_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("meal_plans.id"),
        nullable=True,
    )
    status: Mapped[ShoppingListStatus] = mapped_column(
        SQLEnum(ShoppingListStatus, name="shopping_list_status"),
        nullable=False,
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    user: Mapped["UserModel"] = relationship(back_populates="shopping_lists")
    meal_plan: Mapped["MealPlanModel | None"] = relationship(
        back_populates="shopping_lists",
    )
    items: Mapped[list["ShoppingListItemModel"]] = relationship(
        back_populates="shopping_list",
    )
