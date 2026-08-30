"""Ingredient alias database model."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel


class IngredientAliasModel(CreatedAtUUIDModel):
    """A normalized synonym for one master ingredient."""

    __tablename__ = "ingredient_aliases"
    __table_args__ = (UniqueConstraint("normalized_alias"),)

    master_ingredient_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("master_ingredients.id"),
        nullable=False,
    )
    alias: Mapped[str] = mapped_column(String, nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String, nullable=False)
