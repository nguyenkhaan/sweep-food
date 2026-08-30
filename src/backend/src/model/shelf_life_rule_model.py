"""Shelf-life rule database model."""

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import ShelfLifeRuleScope, StorageMode


class ShelfLifeRuleModel(TimestampedUUIDModel):
    """Ingredient- or category-specific shelf-life rule."""

    __tablename__ = "shelf_life_rules"
    __table_args__ = (
        CheckConstraint(
            "(master_ingredient_id IS NULL) <> (category_id IS NULL)",
            name="shelf_life_rule_exactly_one_target",
        ),
        UniqueConstraint("master_ingredient_id", "storage_mode"),
        UniqueConstraint("category_id", "storage_mode"),
    )

    scope: Mapped[ShelfLifeRuleScope] = mapped_column(
        SQLEnum(ShelfLifeRuleScope, name="shelf_life_rule_scope"),
        nullable=False,
    )
    master_ingredient_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=True,
    )
    category_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ingredient_categories.id"),
        nullable=True,
    )
    storage_mode: Mapped[StorageMode] = mapped_column(
        SQLEnum(StorageMode, name="storage_mode"),
        nullable=False,
    )
    min_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_days: Mapped[int] = mapped_column(Integer, nullable=False)
    default_days: Mapped[int] = mapped_column(Integer, nullable=False)
