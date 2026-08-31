"""Recipe ingredient database model."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import MeasurementUnit

if TYPE_CHECKING:
    from src.model.master_ingredient_model import MasterIngredientModel
    from src.model.recipe_model import RecipeModel


class RecipeIngredientModel(CreatedAtUUIDModel):
    """One required or optional ingredient in a recipe."""

    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        CheckConstraint("required_quantity > 0"),
        Index("ix_recipe_ingredients_recipe_id", "recipe_id"),
        Index("ix_recipe_ingredients_master_ingredient_id", "master_ingredient_id"),
    )

    recipe_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )
    master_ingredient_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=False,
    )
    required_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preparation_note: Mapped[str | None] = mapped_column(String, nullable=True)
    recipe: Mapped["RecipeModel"] = relationship(back_populates="recipe_ingredients")
    master_ingredient: Mapped["MasterIngredientModel"] = relationship(
        back_populates="recipe_ingredients",
    )
