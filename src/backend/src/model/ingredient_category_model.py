"""Ingredient category database model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel


class IngredientCategoryModel(TimestampedUUIDModel):
    """Admin-seeded ingredient category."""

    __tablename__ = "ingredient_categories"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
