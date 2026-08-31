"""Add indexes used by notification API and expiration worker queries.

Revision ID: 20260831_0004
Revises: 446cf3ac3439
Create Date: 2026-08-31
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260831_0004"
down_revision: str | None = "446cf3ac3439"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create indexes supporting owned device, list, delivery, and expiry scans."""
    op.create_index(
        "ix_device_registrations_user_enabled",
        "device_registrations",
        ["user_id", "is_enabled"],
    )
    op.create_index(
        "ix_notifications_user_created_at",
        "notifications",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_notifications_delivery_scheduled",
        "notifications",
        ["delivery_status", "scheduled_at"],
    )
    op.create_index(
        "ix_inventory_batches_status_expires_at",
        "inventory_batches",
        ["status", "expires_at"],
    )


def downgrade() -> None:
    """Remove only the notification workflow indexes added by this revision."""
    op.drop_index(
        "ix_inventory_batches_status_expires_at",
        table_name="inventory_batches",
    )
    op.drop_index(
        "ix_notifications_delivery_scheduled",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_user_created_at",
        table_name="notifications",
    )
    op.drop_index(
        "ix_device_registrations_user_enabled",
        table_name="device_registrations",
    )
