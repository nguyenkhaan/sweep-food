"""Shelf-life rule database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import ShelfLifeRuleScope, StorageMode

if TYPE_CHECKING:
    from src.model.ingredient_category_model import IngredientCategoryModel
    from src.model.master_ingredient_model import MasterIngredientModel


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
        CheckConstraint("min_days >= 0", name="shelf_life_rule_min_days_nonnegative"),
        CheckConstraint("max_days >= 0", name="shelf_life_rule_max_days_nonnegative"),
        CheckConstraint(
            "default_days >= 0",
            name="shelf_life_rule_default_days_nonnegative",
        ),
        CheckConstraint(
            "max_days >= min_days",
            name="shelf_life_rule_max_days_at_least_min_days",
        ),
        CheckConstraint(
            "default_days BETWEEN min_days AND max_days",
            name="shelf_life_rule_default_days_in_range",
        ),
        CheckConstraint(
            "(scope = 'INGREDIENT'::shelf_life_rule_scope "
            "AND master_ingredient_id IS NOT NULL AND category_id IS NULL) "
            "OR (scope = 'CATEGORY'::shelf_life_rule_scope "
            "AND category_id IS NOT NULL AND master_ingredient_id IS NULL)",
            name="shelf_life_rule_scope_matches_target",
        ),
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
    master_ingredient: Mapped["MasterIngredientModel | None"] = relationship(
        back_populates="shelf_life_rules",
    )
    category: Mapped["IngredientCategoryModel | None"] = relationship(
        back_populates="shelf_life_rules",
    )
