"""Add versioned FreshCheck knowledge-base tables.

Revision ID: 51d87b3ea9f2
Revises: 37e7bbc6d5b6
Create Date: 2026-10-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "51d87b3ea9f2"
down_revision: str | Sequence[str] | None = "37e7bbc6d5b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

freshcheck_kb_version_status = postgresql.ENUM(
    "STAGED",
    "ACTIVE",
    "RETIRED",
    name="freshcheck_kb_version_status",
    create_type=False,
)


def upgrade() -> None:
    """Create the immutable, version-scoped FreshCheck KB schema."""
    freshcheck_kb_version_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "freshcheck_kb_versions",
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("status", freshcheck_kb_version_status, nullable=False),
        sa.Column("checksum", sa.String(length=71), nullable=False),
        sa.Column("source_commit", sa.String(length=40), nullable=False),
        sa.Column("stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("artifact", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "staged_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("staged_by", sa.String(), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_by", sa.String(), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_by", sa.String(), nullable=True),
        sa.CheckConstraint(
            "kb_version ~ '^[0-9]+\\.[0-9]+\\.[0-9]+$'",
            name="freshcheck_kb_version_semver",
        ),
        sa.CheckConstraint(
            "checksum ~ '^sha256:[0-9a-f]{64}$'",
            name="freshcheck_kb_version_checksum_sha256",
        ),
        sa.CheckConstraint(
            "source_commit ~ '^[0-9a-f]{40}$'",
            name="freshcheck_kb_version_source_commit_sha",
        ),
        sa.PrimaryKeyConstraint("kb_version"),
    )
    op.create_index(
        "ix_freshcheck_kb_versions_status",
        "freshcheck_kb_versions",
        ["status"],
        unique=False,
    )
    op.create_index(
        "uq_freshcheck_kb_versions_active",
        "freshcheck_kb_versions",
        ["status"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.create_table(
        "freshcheck_sources",
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("tier", sa.String(length=1), nullable=False),
        sa.Column("license", sa.String(), nullable=False),
        sa.Column("accessed", sa.String(length=64), nullable=False),
        sa.Column(
            "source_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_sources_version",
        ),
        sa.PrimaryKeyConstraint("kb_version", "source_id"),
    )
    op.create_table(
        "freshcheck_archetypes",
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("archetype_id", sa.String(length=128), nullable=False),
        sa.Column("name_vi", sa.String(), nullable=False),
        sa.Column(
            "applies_to_groups",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "sensory_tiers",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "inspection_rubric",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "preservation_protocols",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "business_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_archetypes_version",
        ),
        sa.PrimaryKeyConstraint("kb_version", "archetype_id"),
    )
    op.create_table(
        "freshcheck_claims",
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("claim_id", sa.String(length=128), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=False),
        sa.Column("statement_vi", sa.Text(), nullable=False),
        sa.Column("locator", sa.Text(), nullable=False),
        sa.Column(
            "conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("evidence_level", sa.String(length=1), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("extracted_by", sa.String(), nullable=False),
        sa.Column("reviewed_by", sa.String(), nullable=False),
        sa.Column(
            "claim_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_claims_version",
        ),
        sa.ForeignKeyConstraint(
            ["kb_version", "source_id"],
            ["freshcheck_sources.kb_version", "freshcheck_sources.source_id"],
            name="fk_freshcheck_claims_source",
        ),
        sa.PrimaryKeyConstraint("kb_version", "claim_id"),
    )
    op.create_index(
        "ix_freshcheck_claims_version_source",
        "freshcheck_claims",
        ["kb_version", "source_id"],
        unique=False,
    )
    op.create_table(
        "freshcheck_ingredients",
        sa.Column("kb_version", sa.String(length=32), nullable=False),
        sa.Column("freshcheck_ingredient_id", sa.String(length=128), nullable=False),
        sa.Column("archetype_id", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("names_vi", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "base_shelf_life_hours",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_ingredients_version",
        ),
        sa.ForeignKeyConstraint(
            ["kb_version", "archetype_id"],
            ["freshcheck_archetypes.kb_version", "freshcheck_archetypes.archetype_id"],
            name="fk_freshcheck_ingredients_archetype",
        ),
        sa.PrimaryKeyConstraint("kb_version", "freshcheck_ingredient_id"),
    )
    op.create_index(
        "ix_freshcheck_ingredients_version_code",
        "freshcheck_ingredients",
        ["kb_version", "code"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the FreshCheck schema without altering inventory data."""
    op.drop_index(
        "ix_freshcheck_ingredients_version_code",
        table_name="freshcheck_ingredients",
    )
    op.drop_table("freshcheck_ingredients")
    op.drop_index(
        "ix_freshcheck_claims_version_source",
        table_name="freshcheck_claims",
    )
    op.drop_table("freshcheck_claims")
    op.drop_table("freshcheck_archetypes")
    op.drop_table("freshcheck_sources")
    op.drop_index(
        "uq_freshcheck_kb_versions_active",
        table_name="freshcheck_kb_versions",
    )
    op.drop_index(
        "ix_freshcheck_kb_versions_status",
        table_name="freshcheck_kb_versions",
    )
    op.drop_table("freshcheck_kb_versions")
    freshcheck_kb_version_status.drop(op.get_bind(), checkfirst=True)
