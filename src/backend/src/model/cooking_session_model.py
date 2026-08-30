"""Cooking-session database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import CookingConsumptionMode, CookingSessionStatus


class CookingSessionModel(TimestampedUUIDModel):
    """A planned or completed recipe cooking action."""

    __tablename__ = "cooking_sessions"
    __table_args__ = (CheckConstraint("servings > 0"),)

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    recipe_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipes.id"),
        nullable=False,
    )
    meal_plan_item_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("meal_plan_items.id"),
        nullable=True,
    )
    servings: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[CookingSessionStatus] = mapped_column(
        SQLEnum(CookingSessionStatus, name="cooking_session_status"),
        nullable=False,
    )
    consumption_mode: Mapped[CookingConsumptionMode | None] = mapped_column(
        SQLEnum(CookingConsumptionMode, name="cooking_consumption_mode"),
        nullable=True,
    )
    nutrition_snapshot: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    idempotency_key: Mapped[str | None] = mapped_column(String, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
