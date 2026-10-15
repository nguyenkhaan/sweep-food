"""Reviewed catalog-to-FreshCheck ingredient mappings scoped by KB version."""

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel


class MasterIngredientFreshCheckMappingModel(CreatedAtUUIDModel):
    """One reviewed catalog mapping for a FreshCheck ingredient release."""

    __tablename__ = "master_ingredient_freshcheck_mappings"
    __table_args__ = (
        CheckConstraint(
            "match_method IN ('EXACT_CODE', 'EXACT_NAME', 'MANUAL_REVIEW')",
            name="master_ingredient_freshcheck_mapping_match_method",
        ),
        ForeignKeyConstraint(
            ["kb_version", "freshcheck_ingredient_id"],
            [
                "freshcheck_ingredients.kb_version",
                "freshcheck_ingredients.freshcheck_ingredient_id",
            ],
            name="fk_master_ingredient_freshcheck_mappings_ingredient",
        ),
        UniqueConstraint(
            "master_ingredient_id",
            "kb_version",
            name="uq_master_ingredient_freshcheck_mappings_version",
        ),
    )

    master_ingredient_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=False,
    )
    kb_version: Mapped[str] = mapped_column(String(32), nullable=False)
    freshcheck_ingredient_id: Mapped[str] = mapped_column(String(128), nullable=False)
    match_method: Mapped[str] = mapped_column(String(16), nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String, nullable=False)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
