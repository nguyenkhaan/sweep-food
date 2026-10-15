"""Versioned persistence models for the FreshCheck knowledge base."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import Base
from src.model.enum_model import FreshCheckKBVersionStatus


class FreshCheckKBVersionModel(Base):
    """One staged, active, or retired immutable FreshCheck KB release."""

    __tablename__ = "freshcheck_kb_versions"
    __table_args__ = (
        CheckConstraint(
            "kb_version ~ '^[0-9]+\\.[0-9]+\\.[0-9]+$'",
            name="freshcheck_kb_version_semver",
        ),
        CheckConstraint(
            "checksum ~ '^sha256:[0-9a-f]{64}$'",
            name="freshcheck_kb_version_checksum_sha256",
        ),
        CheckConstraint(
            "source_commit ~ '^[0-9a-f]{40}$'",
            name="freshcheck_kb_version_source_commit_sha",
        ),
        Index("ix_freshcheck_kb_versions_status", "status"),
        Index(
            "uq_freshcheck_kb_versions_active",
            "status",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    kb_version: Mapped[str] = mapped_column(String(32), primary_key=True)
    status: Mapped[FreshCheckKBVersionStatus] = mapped_column(
        SQLEnum(FreshCheckKBVersionStatus, name="freshcheck_kb_version_status"),
        nullable=False,
    )
    checksum: Mapped[str] = mapped_column(String(71), nullable=False)
    source_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    stats: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    artifact: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    staged_by: Mapped[str | None] = mapped_column(String, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    retired_by: Mapped[str | None] = mapped_column(String, nullable=True)


class FreshCheckSourceModel(Base):
    """An evidence source belonging to one FreshCheck KB release."""

    __tablename__ = "freshcheck_sources"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_sources_version",
        ),
        PrimaryKeyConstraint("kb_version", "source_id"),
    )

    kb_version: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    tier: Mapped[str] = mapped_column(String(1), nullable=False)
    license: Mapped[str] = mapped_column(String, nullable=False)
    accessed: Mapped[str] = mapped_column(String(64), nullable=False)
    source_data: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class FreshCheckClaimModel(Base):
    """A reviewed KB claim with an evidence source in the same release."""

    __tablename__ = "freshcheck_claims"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_claims_version",
        ),
        ForeignKeyConstraint(
            ["kb_version", "source_id"],
            ["freshcheck_sources.kb_version", "freshcheck_sources.source_id"],
            name="fk_freshcheck_claims_source",
        ),
        PrimaryKeyConstraint("kb_version", "claim_id"),
        Index("ix_freshcheck_claims_version_source", "kb_version", "source_id"),
    )

    kb_version: Mapped[str] = mapped_column(String(32), nullable=False)
    claim_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    statement_vi: Mapped[str] = mapped_column(Text, nullable=False)
    locator: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    evidence_level: Mapped[str] = mapped_column(String(1), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    extracted_by: Mapped[str] = mapped_column(String, nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String, nullable=False)
    claim_data: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class FreshCheckArchetypeModel(Base):
    """Sensory rubric and preservation protocol for one KB archetype."""

    __tablename__ = "freshcheck_archetypes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_archetypes_version",
        ),
        PrimaryKeyConstraint("kb_version", "archetype_id"),
    )

    kb_version: Mapped[str] = mapped_column(String(32), nullable=False)
    archetype_id: Mapped[str] = mapped_column(String(128), nullable=False)
    name_vi: Mapped[str] = mapped_column(String, nullable=False)
    applies_to_groups: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    sensory_tiers: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    inspection_rubric: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    preservation_protocols: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False
    )
    business_rules: Mapped[list[object]] = mapped_column(JSONB, nullable=False)


class FreshCheckIngredientModel(Base):
    """Ingredient shelf-life data assigned to an archetype in one KB release."""

    __tablename__ = "freshcheck_ingredients"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kb_version"],
            ["freshcheck_kb_versions.kb_version"],
            name="fk_freshcheck_ingredients_version",
        ),
        ForeignKeyConstraint(
            ["kb_version", "archetype_id"],
            ["freshcheck_archetypes.kb_version", "freshcheck_archetypes.archetype_id"],
            name="fk_freshcheck_ingredients_archetype",
        ),
        PrimaryKeyConstraint("kb_version", "freshcheck_ingredient_id"),
        Index("ix_freshcheck_ingredients_version_code", "kb_version", "code"),
    )

    kb_version: Mapped[str] = mapped_column(String(32), nullable=False)
    freshcheck_ingredient_id: Mapped[str] = mapped_column(String(128), nullable=False)
    archetype_id: Mapped[str] = mapped_column(String(128), nullable=False)
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    names_vi: Mapped[list[object]] = mapped_column(JSONB, nullable=False)
    base_shelf_life_hours: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False
    )
