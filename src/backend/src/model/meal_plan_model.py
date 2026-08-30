"""Meal-plan database model."""

from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel


class MealPlanModel(TimestampedUUIDModel):
    """A user's bounded meal plan."""

    __tablename__ = "meal_plans"
    __table_args__ = (CheckConstraint("starts_on <= ends_on"),)

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date] = mapped_column(Date, nullable=False)
