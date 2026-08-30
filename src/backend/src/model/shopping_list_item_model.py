"""Shopping-list item database model."""

from uuid import UUID

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import MeasurementUnit


class ShoppingListItemModel(TimestampedUUIDModel):
    """A generated or manual shopping-list line item."""

    __tablename__ = "shopping_list_items"
    __table_args__ = (
        CheckConstraint(
            "(master_ingredient_id IS NULL) <> (custom_name IS NULL)",
            name="shopping_item_exactly_one_identity",
        ),
        CheckConstraint("required_quantity > 0"),
        CheckConstraint("available_quantity >= 0"),
        CheckConstraint("missing_quantity >= 0"),
    )

    shopping_list_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("shopping_lists.id"),
        nullable=False,
    )
    master_ingredient_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=True,
    )
    custom_name: Mapped[str | None] = mapped_column(String, nullable=True)
    required_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    available_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    missing_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_checked: Mapped[bool] = mapped_column(default=False, nullable=False)
    source_metadata: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
