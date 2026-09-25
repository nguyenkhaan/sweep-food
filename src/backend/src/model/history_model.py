"""Deletion-safe ingredient usage history snapshots."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import UUIDModel
from src.model.enum_model import MeasurementUnit


class IngredientUsageHistoryModel(UUIDModel):
    """Immutable ingredient and recipe snapshots recorded after cooking."""

    __tablename__ = "ingredient_usage_history"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ingredient_usage_history_quantity_positive",
        ),
        CheckConstraint(
            "(jsonb_typeof(ingredient) = 'object' "
            "AND jsonb_typeof(ingredient -> 'name') = 'string' "
            "AND btrim(ingredient ->> 'name') <> '' "
            "AND ingredient ->> 'type' = 'ingredient') IS TRUE",
            name="ingredient_usage_history_ingredient_snapshot_valid",
        ),
        CheckConstraint(
            "(jsonb_typeof(recipe) = 'object' "
            "AND jsonb_typeof(recipe -> 'name') = 'string' "
            "AND btrim(recipe ->> 'name') <> '' "
            "AND recipe ->> 'type' = 'recipe') IS TRUE",
            name="ingredient_usage_history_recipe_snapshot_valid",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    ingredient: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    recipe: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
