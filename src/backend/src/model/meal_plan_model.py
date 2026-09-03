"""Meal-plan database model."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel

if TYPE_CHECKING:
    from src.model.meal_plan_item_model import MealPlanItemModel
    from src.model.shopping_list_model import ShoppingListModel
    from src.model.user_model import UserModel


class MealPlanModel(TimestampedUUIDModel):
    """A user's bounded meal plan."""

    __tablename__ = "meal_plans"
    __table_args__ = (
        CheckConstraint("starts_on <= ends_on"),
        Index("ix_meal_plans_user_starts_on", "user_id", "starts_on"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date] = mapped_column(Date, nullable=False)
    user: Mapped["UserModel"] = relationship(back_populates="meal_plans")
    items: Mapped[list["MealPlanItemModel"]] = relationship(back_populates="meal_plan")
    shopping_lists: Mapped[list["ShoppingListModel"]] = relationship(
        back_populates="meal_plan",
    )
