"""Master ingredient database model."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, Numeric, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import MeasurementUnit, StorageMode

if TYPE_CHECKING:
    from src.model.ingredient_alias_model import IngredientAliasModel
    from src.model.ingredient_category_model import IngredientCategoryModel
    from src.model.recipe_ingredient_model import RecipeIngredientModel
    from src.model.shelf_life_rule_model import ShelfLifeRuleModel


class MasterIngredientModel(TimestampedUUIDModel):
    """Canonical ingredient used by recipes and inventory batches."""

    __tablename__ = "master_ingredients"
    __table_args__ = (
        Index("ix_master_ingredients_category_id", "category_id"),
        Index(
            "uq_master_ingredients_category_name_lower",
            "category_id",
            text("lower(name)"),
            unique=True,
        ),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("ingredient_categories.id"),
        nullable=False,
    )
    default_media_url: Mapped[str | None] = mapped_column(String, nullable=True)
    canonical_unit: Mapped[MeasurementUnit] = mapped_column(
        SQLEnum(MeasurementUnit, name="measurement_unit"),
        nullable=False,
    )
    calories: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    protein_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    fat_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    carbs_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    sugar_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    sodium_mg: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    other_nutrients: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    default_storage_mode: Mapped[StorageMode | None] = mapped_column(
        SQLEnum(StorageMode, name="storage_mode"),
        nullable=True,
    )
    category: Mapped["IngredientCategoryModel"] = relationship(
        back_populates="master_ingredients",
    )
    aliases: Mapped[list["IngredientAliasModel"]] = relationship(
        back_populates="master_ingredient",
    )
    shelf_life_rules: Mapped[list["ShelfLifeRuleModel"]] = relationship(
        back_populates="master_ingredient",
    )
    recipe_ingredients: Mapped[list["RecipeIngredientModel"]] = relationship(
        back_populates="master_ingredient",
    )
