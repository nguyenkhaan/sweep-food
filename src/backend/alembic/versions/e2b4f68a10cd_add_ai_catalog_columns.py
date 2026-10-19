"""add ai catalog columns

Revision ID: e2b4f68a10cd
Revises: 98d6d2fdff50
Create Date: 2026-10-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e2b4f68a10cd"
down_revision: str | Sequence[str] | None = "98d6d2fdff50"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add AI feature columns and master ingredient source code index."""
    op.add_column(
        "recipes",
        sa.Column(
            "ai_features",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "recipe_ingredients",
        sa.Column(
            "ai_attributes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "master_ingredients",
        sa.Column("source_code", sa.String(length=32), nullable=True),
    )
    op.create_index(
        "uq_master_ingredients_source_code",
        "master_ingredients",
        ["source_code"],
        unique=True,
        postgresql_where=sa.text("source_code IS NOT NULL"),
    )


def downgrade() -> None:
    """Revert AI feature columns and master ingredient source code index."""
    op.drop_index(
        "uq_master_ingredients_source_code",
        table_name="master_ingredients",
        postgresql_where=sa.text("source_code IS NOT NULL"),
    )
    op.drop_column("master_ingredients", "source_code")
    op.drop_column("recipe_ingredients", "ai_attributes")
    op.drop_column("recipes", "ai_features")
