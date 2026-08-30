"""create user and auth-session models.

Revision ID: 6470957327a3
Revises: 20260830_0001
Create Date: 2026-08-30 14:52:37.154661
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6470957327a3"
down_revision: str | Sequence[str] | None = "20260830_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create persistence for password-authenticated users and refresh sessions."""
    user_role = postgresql.ENUM(
        "USER",
        "ADMIN",
        name="user_role",
        create_type=False,
    )
    account_status = postgresql.ENUM(
        "ACTIVE",
        "BANNED",
        name="account_status",
        create_type=False,
    )
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    account_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("phone_e164", sa.String(), nullable=False),
        sa.Column("phone_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("status", account_status, nullable=False),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.CheckConstraint(
            "status <> 'ACTIVE' OR phone_verified_at IS NOT NULL",
            name="active_user_requires_verified_phone",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_e164"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(), nullable=False),
        sa.Column("token_family_id", sa.UUID(), nullable=False),
        sa.Column("device_label", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_auth_sessions_token_family_id",
        "auth_sessions",
        ["token_family_id"],
    )
    op.create_index(
        "ix_auth_sessions_user_id_expires_at",
        "auth_sessions",
        ["user_id", "expires_at"],
    )


def downgrade() -> None:
    """Remove user/session persistence and their PostgreSQL enum types."""
    op.drop_index("ix_auth_sessions_user_id_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_token_family_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("users")
    bind = op.get_bind()
    sa.Enum(name="account_status").drop(bind, checkfirst=True)
    sa.Enum(name="user_role").drop(bind, checkfirst=True)
