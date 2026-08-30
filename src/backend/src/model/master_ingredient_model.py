"""Master ingredient database model."""

from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import MeasurementUnit, StorageMode


class MasterIngredientModel(TimestampedUUIDModel):
    """Canonical ingredient used by recipes and inventory batches."""

    __tablename__ = "master_ingredients"

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
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sugar_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
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
