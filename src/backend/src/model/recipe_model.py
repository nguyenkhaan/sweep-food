"""Recipe database model."""

from sqlalchemy import Float, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel


class RecipeModel(TimestampedUUIDModel):
    """Admin-seeded recipe with denormalized nutrition estimates."""

    __tablename__ = "recipes"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    media_url: Mapped[str | None] = mapped_column(String, nullable=True)
    default_servings: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cooking_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_carbs_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_sugar_g: Mapped[float | None] = mapped_column(Float, nullable=True)
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
