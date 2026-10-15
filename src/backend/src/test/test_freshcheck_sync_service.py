"""Unit tests for FreshCheck artifact validation and sync planning."""

from copy import deepcopy

import pytest

from src.service.freshcheck_sync_service import (
    ArtifactValidationError,
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
