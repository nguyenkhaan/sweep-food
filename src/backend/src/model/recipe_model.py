"""Recipe database model."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import CheckConstraint, Float, Index, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel

if TYPE_CHECKING:
    from src.model.favorite_menu_item_model import FavoriteMenuItemModel
    from src.model.favorite_recipe_model import FavoriteRecipeModel
    from src.model.meal_plan_item_model import MealPlanItemModel
    from src.model.recipe_ingredient_model import RecipeIngredientModel
    from src.model.recommendation_item_model import RecommendationItemModel


class RecipeModel(TimestampedUUIDModel):
    """Admin-seeded recipe with denormalized nutrition estimates."""

    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint(
            "default_servings > 0", name="recipe_default_servings_positive"
        ),
        CheckConstraint(
            "nutrition_status IN ('COMPLETE', 'PARTIAL', 'INCOMPLETE')",
            name="recipe_nutrition_status_valid",
        ),
        Index("uq_recipes_name_lower", text("lower(name)"), unique=True),
        Index("uq_recipes_source_url", "source_url", unique=True),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    media_url: Mapped[str | None] = mapped_column(String, nullable=True)
    source_platform: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        server_default=text("'internal'"),
        nullable=False,
    )
    source_url: Mapped[str] = mapped_column(
        String,
        default=lambda: f"internal://recipe/{uuid4()}",
        nullable=False,
    )
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
    nutrition_status: Mapped[str] = mapped_column(
        String(20),
        default="INCOMPLETE",
        server_default=text("'INCOMPLETE'"),
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
    recommendation_items: Mapped[list["RecommendationItemModel"]] = relationship(
        back_populates="recipe",
    )
    meal_plan_items: Mapped[list["MealPlanItemModel"]] = relationship(
        back_populates="recipe",
    )
    favorite_recipes: Mapped[list["FavoriteRecipeModel"]] = relationship(
        back_populates="recipe",
    )
    favorite_menu_items: Mapped[list["FavoriteMenuItemModel"]] = relationship(
        back_populates="recipe",
    )
