"""Ingredient category database model."""

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel

if TYPE_CHECKING:
    from src.model.master_ingredient_model import MasterIngredientModel
    from src.model.shelf_life_rule_model import ShelfLifeRuleModel


class IngredientCategoryModel(TimestampedUUIDModel):
    """Admin-seeded ingredient category."""

    __tablename__ = "ingredient_categories"
    __table_args__ = (
        Index("uq_ingredient_categories_name_lower", text("lower(name)"), unique=True),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    master_ingredients: Mapped[list["MasterIngredientModel"]] = relationship(
        back_populates="category",
    )
    shelf_life_rules: Mapped[list["ShelfLifeRuleModel"]] = relationship(
        back_populates="category",
    )
