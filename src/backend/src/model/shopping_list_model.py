"""Shopping-list database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import ShoppingListStatus


class ShoppingListModel(TimestampedUUIDModel):
    """A generated or manually managed shopping list."""

    __tablename__ = "shopping_lists"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    meal_plan_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("meal_plans.id"),
        nullable=True,
    )
    status: Mapped[ShoppingListStatus] = mapped_column(
        SQLEnum(ShoppingListStatus, name="shopping_list_status"),
        nullable=False,
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
