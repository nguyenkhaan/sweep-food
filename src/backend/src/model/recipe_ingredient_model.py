"""Recipe ingredient database model."""

from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import MeasurementUnit


class RecipeIngredientModel(CreatedAtUUIDModel):
    """One required or optional ingredient in a recipe."""

    __tablename__ = "recipe_ingredients"
    __table_args__ = (CheckConstraint("required_quantity > 0"),)

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
    required_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preparation_note: Mapped[str | None] = mapped_column(String, nullable=True)
