"""Ranked recipe recommendation database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel

if TYPE_CHECKING:
    from src.model.recipe_model import RecipeModel
    from src.model.recommendation_run_model import RecommendationRunModel


class RecommendationItemModel(CreatedAtUUIDModel):
    """One ranked recipe in a recommendation run."""

    __tablename__ = "recommendation_items"
    __table_args__ = (
        UniqueConstraint("recommendation_run_id", "rank"),
        Index("ix_recommendation_items_recipe_id", "recipe_id"),
    )

    recommendation_run_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recommendation_runs.id"),
        nullable=False,
    )
    recipe_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    expiration_utilization_score: Mapped[float] = mapped_column(Float, nullable=False)
    availability_score: Mapped[float] = mapped_column(Float, nullable=False)
    preference_fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_minimization_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    recommendation_run: Mapped["RecommendationRunModel"] = relationship(
        back_populates="items",
    )
    recipe: Mapped["RecipeModel"] = relationship(back_populates="recommendation_items")
