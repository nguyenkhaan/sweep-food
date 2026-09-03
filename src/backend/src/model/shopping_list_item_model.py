"""Shopping-list item database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import MeasurementUnit

if TYPE_CHECKING:
    from src.model.master_ingredient_model import MasterIngredientModel
    from src.model.shopping_list_model import ShoppingListModel


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
        CheckConstraint(
            "custom_name IS NULL OR btrim(custom_name) <> ''",
            name="shopping_item_custom_name_nonblank",
        ),
        Index("ix_shopping_list_items_list_id", "shopping_list_id"),
        Index("ix_shopping_list_items_master_ingredient_id", "master_ingredient_id"),
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
    shopping_list: Mapped["ShoppingListModel"] = relationship(back_populates="items")
    master_ingredient: Mapped["MasterIngredientModel | None"] = relationship(
        back_populates="shopping_list_items",
    )
