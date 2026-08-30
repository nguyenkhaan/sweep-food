"""Establish Alembic revision control before application tables are introduced.

Revision ID: 20260830_0001
Revises:
Create Date: 2026-08-30 00:00:00
"""

# revision identifiers, used by Alembic.
revision: str = "20260830_0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create no tables; subsequent migrations introduce the approved schema."""


def downgrade() -> None:
    """Revert no schema objects for the bootstrap revision."""
