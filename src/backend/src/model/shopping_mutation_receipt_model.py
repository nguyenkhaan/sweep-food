"""Persistent idempotency receipts for shopping-list mutations."""

from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import CreatedAtUUIDModel


class ShoppingMutationReceiptModel(CreatedAtUUIDModel):
    """Append-only replay snapshot for one successful shopping mutation."""

    __tablename__ = "shopping_mutation_receipts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "method",
            "request_path",
            "key_hash",
            name="uq_shopping_receipt_scope_key",
        ),
        CheckConstraint(
            "method IN ('POST', 'PATCH', 'DELETE')",
            name="shopping_receipt_method_allowed",
        ),
        CheckConstraint(
            "response_status IN (200, 201, 204)",
            name="shopping_receipt_response_status_allowed",
        ),
        CheckConstraint(
            "btrim(idempotency_key) <> ''",
            name="shopping_receipt_key_nonblank",
        ),
        CheckConstraint(
            "key_hash ~ '^[0-9a-f]{64}$' AND request_fingerprint ~ '^[0-9a-f]{64}$'",
            name="shopping_receipt_hashes_valid",
        ),
        CheckConstraint(
            "(response_status = 204 AND response_body IS NULL) OR "
            "(response_status IN (200, 201) AND response_body IS NOT NULL "
            "AND jsonb_typeof(response_body) = 'object')",
            name="shopping_receipt_response_body_consistent",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    method: Mapped[str] = mapped_column(String(6), nullable=False)
    request_path: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    response_body: Mapped[dict[str, object] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
