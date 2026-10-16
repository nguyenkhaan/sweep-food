"""Unit tests for FreshCheck artifact validation and sync planning."""

from copy import deepcopy
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import FreshCheckKBVersionStatus
from src.model.freshcheck_model import FreshCheckKBVersionModel
from src.service.freshcheck_sync_service import (
    ArtifactValidationError,
    FreshCheckSyncService,
    ReleaseConflictError,
    calculate_artifact_checksum,
    parse_freshcheck_artifact,
)


def _artifact() -> dict[str, object]:
    """Build the smallest valid FreshCheck artifact for a unit test."""
    artifact: dict[str, object] = {
        "kb_version": "1.2.3",
        "source_commit": "a" * 40,
        "generated_at": "2026-10-16T00:00:00+00:00",
        "stats": {
            "total_sources": 1,
            "total_claims": 1,
            "total_archetypes": 1,
            "total_ingredients": 1,
        },
        "sources": [
            {
                "id": "S-1",
                "title": "Source",
                "tier": "A",
                "license": "CC-BY-4.0",
                "accessed": "2026-10-16",
            }
        ],
        "claims": [
            {
                "id": "C-1",
                "statement_vi": "Claim",
                "source": "S-1",
                "locator": "p. 1",
                "conditions": [],
                "evidence_level": "A",
                "status": "reviewed",
                "extracted_by": "test",
                "reviewed_by": "test",
            }
        ],
        "archetypes": {
            "ARCH-1": {
                "archetype": "ARCH-1",
                "name_vi": "Archetype",
                "applies_to_groups": ["group"],
                "sensory_tiers": {},
                "inspection_rubric": [],
                "preservation_protocols": {},
                "business_rules": [],
            }
        },
        "ingredients": {
            "I-1": {
                "id": "I-1",
                "code": "ingredient",
                "names_vi": ["Ingredient"],
                "archetype": "ARCH-1",
                "base_shelf_life_hours": {"fridge": {"value": 24, "claim": "C-1"}},
            }
        },
    }
    artifact["checksum"] = calculate_artifact_checksum(artifact)
    return artifact


def test_parse_freshcheck_artifact_builds_a_versioned_sync_plan() -> None:
    """A valid artifact exposes its identity and record counts for staging."""
    artifact = parse_freshcheck_artifact(_artifact())

    assert artifact.kb_version == "1.2.3"
    assert artifact.stats == {
        "total_sources": 1,
        "total_claims": 1,
        "total_archetypes": 1,
        "total_ingredients": 1,
    }
    assert artifact.record_counts == {
        "sources": 1,
        "claims": 1,
        "archetypes": 1,
        "ingredients": 1,
    }


def test_parse_freshcheck_artifact_rejects_a_changed_checksum() -> None:
    """A changed artifact cannot masquerade as the recorded release."""
    artifact = _artifact()
    artifact["stats"] = {"total_sources": 99}

    with pytest.raises(ArtifactValidationError, match="checksum"):
        parse_freshcheck_artifact(artifact)


def test_parse_freshcheck_artifact_rejects_a_claim_without_its_source() -> None:
    """Claims must stay within the evidence scope of their release."""
    artifact = deepcopy(_artifact())
    claims = artifact["claims"]
    assert isinstance(claims, list)
    claim = claims[0]
    assert isinstance(claim, dict)
    claim["source"] = "S-missing"
    artifact["checksum"] = calculate_artifact_checksum(artifact)

    with pytest.raises(ArtifactValidationError, match="source"):
        parse_freshcheck_artifact(artifact)


@pytest.mark.anyio
async def test_stage_is_idempotent_for_the_same_version_and_checksum() -> None:
    """Replaying a staged artifact does not write duplicate KB records."""
    artifact = parse_freshcheck_artifact(_artifact())
    existing_version = FreshCheckKBVersionModel(
        kb_version=artifact.kb_version,
        status=FreshCheckKBVersionStatus.STAGED,
        checksum=artifact.checksum,
        source_commit=artifact.source_commit,
        stats=artifact.stats,
        artifact=artifact.raw,
    )
    session = AsyncMock(spec=AsyncSession)
    session.get.return_value = existing_version
    session.add_all = Mock()
    service = FreshCheckSyncService(session)

    result = await service.stage(artifact, "unit-test")

    assert result.action == "already_staged"
    session.add_all.assert_not_called()
    session.flush.assert_not_awaited()


@pytest.mark.anyio
async def test_stage_flushes_the_kb_version_before_its_dependent_records() -> None:
    """The database must receive the release parent before children with FK references."""
    artifact = parse_freshcheck_artifact(_artifact())
    session = AsyncMock(spec=AsyncSession)
    session.get.return_value = None
    session.add = Mock()
    session.add_all = Mock()
    service = FreshCheckSyncService(session)

    await service.stage(artifact, "unit-test")

    staged_version = session.add.call_args.args[0]
    child_records = session.add_all.call_args_list[-1].args[0]
    assert staged_version.kb_version == artifact.kb_version
    assert all(record is not staged_version for record in child_records)
    assert session.add_all.call_count == 4
    assert session.flush.await_count == 5


@pytest.mark.anyio
async def test_stage_rejects_a_checksum_collision() -> None:
    """An existing version cannot be overwritten with another artifact."""
    artifact = parse_freshcheck_artifact(_artifact())
    existing_version = FreshCheckKBVersionModel(
        kb_version=artifact.kb_version,
        status=FreshCheckKBVersionStatus.STAGED,
        checksum=f"sha256:{'b' * 64}",
        source_commit=artifact.source_commit,
        stats=artifact.stats,
        artifact=artifact.raw,
    )
    session = AsyncMock(spec=AsyncSession)
    session.get.return_value = existing_version
    service = FreshCheckSyncService(session)

    with pytest.raises(ReleaseConflictError, match="checksum"):
        await service.stage(artifact, "unit-test")


@pytest.mark.anyio
async def test_activate_retires_the_prior_active_release() -> None:
    """Activation atomically changes the active release while retaining history."""
    artifact = parse_freshcheck_artifact(_artifact())
    target_version = FreshCheckKBVersionModel(
        kb_version=artifact.kb_version,
        status=FreshCheckKBVersionStatus.STAGED,
        checksum=artifact.checksum,
        source_commit=artifact.source_commit,
        stats=artifact.stats,
        artifact=artifact.raw,
    )
    prior_active_version = FreshCheckKBVersionModel(
        kb_version="1.2.2",
        status=FreshCheckKBVersionStatus.ACTIVE,
        checksum=f"sha256:{'b' * 64}",
        source_commit="b" * 40,
        stats={},
        artifact={},
    )
    session = AsyncMock(spec=AsyncSession)
    session.get.return_value = target_version
    session.scalar.return_value = prior_active_version
    service = FreshCheckSyncService(session)

    result = await service.activate(artifact, "unit-test")

    assert result.action == "activated"
    assert target_version.status is FreshCheckKBVersionStatus.ACTIVE
    assert target_version.activated_by == "unit-test"
    assert prior_active_version.status is FreshCheckKBVersionStatus.RETIRED
    assert prior_active_version.retired_by == "unit-test"
    assert session.flush.await_count == 2


@pytest.mark.anyio
async def test_rollback_reactivates_a_retired_release() -> None:
    """Rollback restores an exact prior artifact and retires the current release."""
    artifact = parse_freshcheck_artifact(_artifact())
    target_version = FreshCheckKBVersionModel(
        kb_version=artifact.kb_version,
        status=FreshCheckKBVersionStatus.RETIRED,
        checksum=artifact.checksum,
        source_commit=artifact.source_commit,
        stats=artifact.stats,
        artifact=artifact.raw,
    )
    current_version = FreshCheckKBVersionModel(
        kb_version="1.2.4",
        status=FreshCheckKBVersionStatus.ACTIVE,
        checksum=f"sha256:{'b' * 64}",
        source_commit="b" * 40,
        stats={},
        artifact={},
    )
    session = AsyncMock(spec=AsyncSession)
    session.get.return_value = target_version
    session.scalar.return_value = current_version
    service = FreshCheckSyncService(session)

    result = await service.rollback(artifact, "unit-test-rollback")

    assert result.action == "rolled_back"
    assert target_version.status is FreshCheckKBVersionStatus.ACTIVE
    assert target_version.activated_by == "unit-test-rollback"
    assert target_version.retired_at is None
    assert current_version.status is FreshCheckKBVersionStatus.RETIRED
    assert current_version.retired_by == "unit-test-rollback"
