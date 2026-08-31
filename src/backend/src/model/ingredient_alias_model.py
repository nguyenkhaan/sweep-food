"""Ingredient alias database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import CreatedAtUUIDModel

if TYPE_CHECKING:
    from src.model.master_ingredient_model import MasterIngredientModel


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
    master_ingredient: Mapped["MasterIngredientModel"] = relationship(
        back_populates="aliases",
    )
