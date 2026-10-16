"""Persist immutable FreshCheck assessments for inventory batches.

Revision ID: 98d6d2fdff50
Revises: 70d4c8ab1e6f
Create Date: 2026-10-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "98d6d2fdff50"
down_revision: str | Sequence[str] | None = "70d4c8ab1e6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create immutable assessment records linked to reviewed KB ingredients."""
    op.create_table(
        "freshcheck_assessments",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inventory_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("freshcheck_ingredient_id", sa.String(length=128), nullable=False),
        sa.Column("rule_version", sa.String(length=64), nullable=False),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("outcome", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("claims", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("applied_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["inventory_batch_id"], ["inventory_batches.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["kb_version", "freshcheck_ingredient_id"],
            [
                "freshcheck_ingredients.kb_version",
                "freshcheck_ingredients.freshcheck_ingredient_id",
            ],
            name="fk_freshcheck_assessments_ingredient",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "inventory_batch_id",
            "idempotency_key",
            name="uq_freshcheck_assessments_idempotency",
        ),
    )
    op.execute(
        """
        CREATE FUNCTION prevent_freshcheck_assessment_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'freshcheck assessments are immutable';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER freshcheck_assessments_immutable
        BEFORE UPDATE OR DELETE ON freshcheck_assessments
        FOR EACH ROW EXECUTE FUNCTION prevent_freshcheck_assessment_mutation();
        """
    )


def downgrade() -> None:
    """Remove the assessment history schema created by this revision."""
    op.execute(
        "DROP TRIGGER freshcheck_assessments_immutable ON freshcheck_assessments"
    )
    op.execute("DROP FUNCTION prevent_freshcheck_assessment_mutation()")
    op.drop_table("freshcheck_assessments")
