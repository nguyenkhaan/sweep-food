"""Add the SQLAlchemy-compatible unverified account status.

Revision ID: 20260830_0003
Revises: 20260830_0002
Create Date: 2026-08-30
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260830_0003"
down_revision: str | Sequence[str] | None = "20260830_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the uppercase enum label used by SQLAlchemy's default enum mapping."""
    op.execute("ALTER TYPE account_status ADD VALUE IF NOT EXISTS 'UNVERIFIED'")


def downgrade() -> None:
    """Leave the additive PostgreSQL enum label intact for safe rollback."""
    # PostgreSQL does not support removing an enum value without replacing the type.
