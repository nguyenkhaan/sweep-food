"""Meal-plan item database model."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Index, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import MealPlanItemStatus, MealSlot

if TYPE_CHECKING:
    from src.model.meal_plan_model import MealPlanModel
    from src.model.recipe_model import RecipeModel
    from src.model.recommendation_run_model import RecommendationRunModel


class MealPlanItemModel(TimestampedUUIDModel):
    """One planned recipe/date/meal slot."""

    __tablename__ = "meal_plan_items"
    __table_args__ = (
        CheckConstraint("servings > 0"),
        UniqueConstraint("meal_plan_id", "planned_for", "meal_slot"),
        Index("ix_meal_plan_items_plan_planned_for", "meal_plan_id", "planned_for"),
        Index("ix_meal_plan_items_recipe_id", "recipe_id"),
        Index("ix_meal_plan_items_recommendation_run_id", "recommendation_run_id"),
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
    meal_plan: Mapped["MealPlanModel"] = relationship(back_populates="items")
    recipe: Mapped["RecipeModel"] = relationship(back_populates="meal_plan_items")
    recommendation_run: Mapped["RecommendationRunModel | None"] = relationship(
        back_populates="meal_plan_items",
    )
