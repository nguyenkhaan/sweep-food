"""Establish Alembic revision control before application tables are introduced.

Revision ID: 20260830_0001
Revises:
Create Date: 2026-08-30 00:00:00
"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "20260830_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create no tables; subsequent migrations introduce the approved schema."""


def downgrade() -> None:
    """Revert no schema objects for the bootstrap revision."""
