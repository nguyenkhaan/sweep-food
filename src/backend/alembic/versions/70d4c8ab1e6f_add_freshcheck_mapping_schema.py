"""Add versioned catalog-to-FreshCheck ingredient mappings.

Revision ID: 70d4c8ab1e6f
Revises: 51d87b3ea9f2
Create Date: 2026-10-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "70d4c8ab1e6f"
down_revision: str | Sequence[str] | None = "51d87b3ea9f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create reviewed mappings without modifying catalog or KB data."""
    op.create_table(
        "master_ingredient_freshcheck_mappings",
        sa.Column("master_ingredient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("freshcheck_ingredient_id", sa.String(length=128), nullable=False),
        sa.Column("match_method", sa.String(length=16), nullable=False),
        sa.Column("reviewed_by", sa.String(), nullable=False),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "match_method IN ('EXACT_CODE', 'EXACT_NAME', 'MANUAL_REVIEW')",
            name="master_ingredient_freshcheck_mapping_match_method",
        ),
        sa.ForeignKeyConstraint(
            ["master_ingredient_id"],
            ["master_ingredients.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kb_version", "freshcheck_ingredient_id"],
            [
                "freshcheck_ingredients.kb_version",
                "freshcheck_ingredients.freshcheck_ingredient_id",
            ],
            name="fk_master_ingredient_freshcheck_mappings_ingredient",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "master_ingredient_id",
            "kb_version",
            name="uq_master_ingredient_freshcheck_mappings_version",
        ),
    )


def downgrade() -> None:
    """Remove only the mapping table created by this revision."""
    op.drop_table("master_ingredient_freshcheck_mappings")
