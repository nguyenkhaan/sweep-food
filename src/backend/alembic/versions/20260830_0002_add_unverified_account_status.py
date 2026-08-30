"""Add the temporary unverified account status.

Revision ID: 20260830_0002
Revises: 6470957327a3
Create Date: 2026-08-30
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260830_0002"
down_revision: str | Sequence[str] | None = "6470957327a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Allow newly registered users to remain unverified before OTP validation."""
    op.execute("ALTER TYPE account_status ADD VALUE IF NOT EXISTS 'unverified'")


def downgrade() -> None:
    """Leave PostgreSQL enum values intact because they cannot be safely removed."""
    # PostgreSQL does not support removing an enum value without replacing the type.
