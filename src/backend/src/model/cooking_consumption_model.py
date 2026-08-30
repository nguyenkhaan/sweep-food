"""Cooking consumption database model."""

from uuid import UUID

from sqlalchemy import CheckConstraint, Float, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel
from src.model.enum_model import MeasurementUnit


class CookingConsumptionModel(CreatedAtUUIDModel):
    """Exact inventory batch quantity consumed by a cooking session."""

    __tablename__ = "cooking_consumptions"
    __table_args__ = (CheckConstraint("quantity > 0"),)

    cooking_session_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("cooking_sessions.id"),
        nullable=False,
    )
    recipe_ingredient_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("recipe_ingredients.id"),
        nullable=True,
    )
    inventory_batch_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("inventory_batches.id"),
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
