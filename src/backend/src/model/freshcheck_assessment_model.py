"""Immutable FreshCheck assessment history for inventory batches."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel


class FreshCheckAssessmentModel(CreatedAtUUIDModel):
    """One reproducible FreshCheck decision, retained even after KB changes."""

    __tablename__ = "freshcheck_assessments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kb_version", "freshcheck_ingredient_id"],
            [
                "freshcheck_ingredients.kb_version",
                "freshcheck_ingredients.freshcheck_ingredient_id",
            ],
            name="fk_freshcheck_assessments_ingredient",
        ),
        UniqueConstraint(
            "user_id",
            "inventory_batch_id",
            "idempotency_key",
            name="uq_freshcheck_assessments_idempotency",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    inventory_batch_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("inventory_batches.id"),
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    kb_version: Mapped[str] = mapped_column(String(32), nullable=False)
    freshcheck_ingredient_id: Mapped[str] = mapped_column(String(128), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(64), nullable=False)
    answers: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    outcome: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    claims: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    applied_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
