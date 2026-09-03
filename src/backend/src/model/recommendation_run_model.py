"""Recipe recommendation run database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import RecommendationProviderType

if TYPE_CHECKING:
    from src.model.meal_plan_item_model import MealPlanItemModel
    from src.model.recommendation_item_model import RecommendationItemModel
    from src.model.user_model import UserModel


class RecommendationRunModel(CreatedAtUUIDModel):
    """One explainable recommendation request and provider output set."""

    __tablename__ = "recommendation_runs"
    __table_args__ = (
        Index("ix_recommendation_runs_user_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    criteria: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    provider: Mapped[RecommendationProviderType] = mapped_column(
        SQLEnum(RecommendationProviderType, name="recommendation_provider_type"),
        nullable=False,
    )
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    user: Mapped["UserModel"] = relationship(back_populates="recommendation_runs")
    items: Mapped[list["RecommendationItemModel"]] = relationship(
        back_populates="recommendation_run",
    )
    meal_plan_items: Mapped[list["MealPlanItemModel"]] = relationship(
        back_populates="recommendation_run",
    )
