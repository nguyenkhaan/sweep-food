"""Meal-plan item database model."""

from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import MealPlanItemStatus, MealSlot


class MealPlanItemModel(TimestampedUUIDModel):
    """One planned recipe/date/meal slot."""

    __tablename__ = "meal_plan_items"
    __table_args__ = (
        CheckConstraint("servings > 0"),
        UniqueConstraint("meal_plan_id", "planned_for", "meal_slot"),
    )

    meal_plan_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("meal_plans.id"),
        nullable=False,
    )
    recipe_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )
    recommendation_run_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recommendation_runs.id"),
        nullable=True,
    )
    planned_for: Mapped[date] = mapped_column(Date, nullable=False)
    meal_slot: Mapped[MealSlot] = mapped_column(
        SQLEnum(MealSlot, name="meal_slot"),
        nullable=False,
    )
    servings: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[MealPlanItemStatus] = mapped_column(
        SQLEnum(MealPlanItemStatus, name="meal_plan_item_status"),
        nullable=False,
    )
