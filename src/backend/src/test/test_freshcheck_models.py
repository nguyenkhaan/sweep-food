"""Metadata contracts for the versioned FreshCheck knowledge base."""

from typing import cast

from sqlalchemy import Index, Table

from src.model import Base
from src.model.freshcheck_model import (
    FreshCheckArchetypeModel,
    FreshCheckClaimModel,
    FreshCheckIngredientModel,
    FreshCheckKBVersionModel,
    FreshCheckSourceModel,
)


def test_freshcheck_models_use_versioned_primary_keys_and_foreign_keys() -> None:
    """Every runtime record remains scoped to one immutable KB version."""
    version_table = cast(Table, FreshCheckKBVersionModel.__table__)
    source_table = cast(Table, FreshCheckSourceModel.__table__)
    claim_table = cast(Table, FreshCheckClaimModel.__table__)
    archetype_table = cast(Table, FreshCheckArchetypeModel.__table__)
    ingredient_table = cast(Table, FreshCheckIngredientModel.__table__)

    assert {
        "freshcheck_kb_versions",
        "freshcheck_sources",
        "freshcheck_claims",
        "freshcheck_archetypes",
        "freshcheck_ingredients",
    } <= set(Base.metadata.tables)
    assert tuple(version_table.primary_key.columns.keys()) == ("kb_version",)
    assert tuple(source_table.primary_key.columns.keys()) == ("kb_version", "source_id")
    assert tuple(claim_table.primary_key.columns.keys()) == ("kb_version", "claim_id")
    assert tuple(archetype_table.primary_key.columns.keys()) == (
        "kb_version",
        "archetype_id",
    )
    assert tuple(ingredient_table.primary_key.columns.keys()) == (
        "kb_version",
        "freshcheck_ingredient_id",
    )

    claim_foreign_keys = {
        foreign_key.name for foreign_key in claim_table.foreign_key_constraints
    }
    ingredient_foreign_keys = {
        foreign_key.name for foreign_key in ingredient_table.foreign_key_constraints
    }
    assert "fk_freshcheck_claims_source" in claim_foreign_keys
    assert "fk_freshcheck_ingredients_archetype" in ingredient_foreign_keys
    assert source_table.c.kb_version.nullable is False
    assert claim_table.c.kb_version.nullable is False
    assert claim_table.c.source_id.nullable is False
    assert ingredient_table.c.kb_version.nullable is False
    assert ingredient_table.c.archetype_id.nullable is False


def test_freshcheck_version_model_allows_only_one_active_version() -> None:
    """A partial unique index prevents two runtime-active KB versions."""
    version_table = cast(Table, FreshCheckKBVersionModel.__table__)
    active_indexes: dict[str, Index] = {
        str(index.name): index
        for index in version_table.indexes
        if index.unique and index.name == "uq_freshcheck_kb_versions_active"
    }

    assert set(active_indexes) == {"uq_freshcheck_kb_versions_active"}
    assert (
        str(
            active_indexes["uq_freshcheck_kb_versions_active"].dialect_options[
                "postgresql"
            ]["where"]
        )
        == "status = 'ACTIVE'"
    )


def test_freshcheck_version_model_validates_release_identity() -> None:
    """Release identity fields reject malformed version and provenance data."""
    version_table = cast(Table, FreshCheckKBVersionModel.__table__)
    check_constraint_names = {
        constraint.name for constraint in version_table.constraints
    }

    assert {
        "freshcheck_kb_version_semver",
        "freshcheck_kb_version_checksum_sha256",
        "freshcheck_kb_version_source_commit_sha",
    } <= check_constraint_names
