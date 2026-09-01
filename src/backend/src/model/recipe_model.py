"""Recipe database model."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, Index, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel

if TYPE_CHECKING:
    from src.model.recipe_ingredient_model import RecipeIngredientModel


class RecipeModel(TimestampedUUIDModel):
    """Admin-seeded recipe with denormalized nutrition estimates."""

    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint(
            "default_servings > 0", name="recipe_default_servings_positive"
        ),
        Index("uq_recipes_name_lower", text("lower(name)"), unique=True),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    media_url: Mapped[str | None] = mapped_column(String, nullable=True)
    default_servings: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    estimated_cooking_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_calories: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3), nullable=True
    )
    total_protein_g: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3), nullable=True
    )
    total_fat_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    total_carbs_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    total_sugar_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    other_nutrients: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    tags: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    recipe_ingredients: Mapped[list["RecipeIngredientModel"]] = relationship(
        back_populates="recipe",
    )
