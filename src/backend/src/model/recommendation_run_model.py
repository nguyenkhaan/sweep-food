"""Recipe recommendation run database model."""

from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import RecommendationProviderType


class RecommendationRunModel(CreatedAtUUIDModel):
    """One explainable recommendation request and provider output set."""

    __tablename__ = "recommendation_runs"

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
