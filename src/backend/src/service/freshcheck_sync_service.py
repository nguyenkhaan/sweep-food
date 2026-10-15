"""Validation and persistence helpers for FreshCheck KB releases."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Final

JsonRecord = dict[str, object]

_CHECKSUM_EXCLUDED_KEYS: Final = frozenset({"checksum", "generated_at"})
_CHECKSUM_PATTERN: Final = re.compile(r"sha256:[0-9a-f]{64}")
_COMMIT_PATTERN: Final = re.compile(r"[0-9a-f]{40}")
_VERSION_PATTERN: Final = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


class ArtifactValidationError(ValueError):
    """Raised when a FreshCheck artifact cannot be staged safely."""


@dataclass(frozen=True)
class FreshCheckArtifact:
    """A validated FreshCheck release ready for staging or activation."""

    raw: JsonRecord
    kb_version: str
    checksum: str
    source_commit: str
    stats: JsonRecord
    sources: tuple[JsonRecord, ...]
    claims: tuple[JsonRecord, ...]
    archetypes: dict[str, JsonRecord]
    ingredients: dict[str, JsonRecord]

    @property
    def record_counts(self) -> dict[str, int]:
        """Return the persisted record counts for dry-run output and audit logs."""
        return {
            "sources": len(self.sources),
            "claims": len(self.claims),
            "archetypes": len(self.archetypes),
            "ingredients": len(self.ingredients),
        }


def calculate_artifact_checksum(payload: JsonRecord) -> str:
    """Calculate the canonical checksum emitted by the KB build process."""
    checksum_payload = {
        key: value for key, value in payload.items() if key not in _CHECKSUM_EXCLUDED_KEYS
    }
    serialized_payload = json.dumps(
        checksum_payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized_payload).hexdigest()}"


def parse_freshcheck_artifact(payload: JsonRecord) -> FreshCheckArtifact:
    """Validate a built artifact before any database connection is opened."""
    kb_version = _required_string(payload, "kb_version")
    checksum = _required_string(payload, "checksum")
    source_commit = _required_string(payload, "source_commit")
    _validate_release_identity(kb_version, checksum, source_commit, payload)

    artifact = FreshCheckArtifact(
        raw=dict(payload),
        kb_version=kb_version,
        checksum=checksum,
        source_commit=source_commit,
        stats=_required_record(payload, "stats"),
        sources=_required_records(payload, "sources"),
        claims=_required_records(payload, "claims"),
        archetypes=_required_record_map(payload, "archetypes"),
        ingredients=_required_record_map(payload, "ingredients"),
    )
    _validate_record_shapes(artifact)
    _validate_references(artifact)
    _validate_stats(artifact)
    return artifact


def _validate_release_identity(
    kb_version: str,
    checksum: str,
    source_commit: str,
    payload: JsonRecord,
) -> None:
    if not _VERSION_PATTERN.fullmatch(kb_version):
        raise ArtifactValidationError("Artifact kb_version must use semantic versioning.")
    if not _CHECKSUM_PATTERN.fullmatch(checksum):
        raise ArtifactValidationError("Artifact checksum has an invalid format.")
    if not _COMMIT_PATTERN.fullmatch(source_commit):
        raise ArtifactValidationError("Artifact source_commit has an invalid format.")
    if checksum != calculate_artifact_checksum(payload):
        raise ArtifactValidationError("Artifact checksum does not match its content.")


def _validate_record_shapes(artifact: FreshCheckArtifact) -> None:
    for source in artifact.sources:
        _require_string_fields(source, ("id", "title", "tier", "license", "accessed"))
    for claim in artifact.claims:
        _require_string_fields(
            claim,
            (
                "id",
                "statement_vi",
                "source",
                "locator",
                "evidence_level",
                "status",
                "extracted_by",
                "reviewed_by",
            ),
        )
        _required_list(claim, "conditions")
    for archetype_id, archetype in artifact.archetypes.items():
        if _required_string(archetype, "archetype") != archetype_id:
            raise ArtifactValidationError("Archetype key does not match its record identifier.")
        _require_string_fields(archetype, ("name_vi",))
        _required_list(archetype, "applies_to_groups")
        _required_record(archetype, "sensory_tiers")
        _required_list(archetype, "inspection_rubric")
        _required_record(archetype, "preservation_protocols")
        _required_list(archetype, "business_rules")
    for ingredient_id, ingredient in artifact.ingredients.items():
        if _required_string(ingredient, "id") != ingredient_id:
            raise ArtifactValidationError("Ingredient key does not match its record identifier.")
        _require_string_fields(ingredient, ("code", "archetype"))
        _required_list(ingredient, "names_vi")
        _required_record(ingredient, "base_shelf_life_hours")


def _validate_references(artifact: FreshCheckArtifact) -> None:
    source_ids = {_required_string(source, "id") for source in artifact.sources}
    claim_ids = {_required_string(claim, "id") for claim in artifact.claims}
    for claim in artifact.claims:
        if _required_string(claim, "source") not in source_ids:
            raise ArtifactValidationError("Claim references a source outside this artifact.")
    for ingredient in artifact.ingredients.values():
        if _required_string(ingredient, "archetype") not in artifact.archetypes:
            raise ArtifactValidationError("Ingredient references an unknown archetype.")
        shelf_life = _required_record(ingredient, "base_shelf_life_hours")
        for rule in shelf_life.values():
            if not isinstance(rule, dict):
                raise ArtifactValidationError("Shelf-life rules must be objects.")
            if _required_string(rule, "claim") not in claim_ids:
                raise ArtifactValidationError("Shelf-life rule references an unknown claim.")


def _validate_stats(artifact: FreshCheckArtifact) -> None:
    for record_type, expected_count in artifact.record_counts.items():
        stats_key = f"total_{record_type}"
        actual_count = artifact.stats.get(stats_key)
        if actual_count != expected_count:
            raise ArtifactValidationError(
                f"Artifact stats {stats_key} does not match its records."
            )


def _required_string(record: JsonRecord, key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ArtifactValidationError(f"Artifact field {key} must be a non-empty string.")
    return value


def _require_string_fields(record: JsonRecord, keys: tuple[str, ...]) -> None:
    for key in keys:
        _required_string(record, key)


def _required_list(record: JsonRecord, key: str) -> tuple[object, ...]:
    value = record.get(key)
    if not isinstance(value, list):
        raise ArtifactValidationError(f"Artifact field {key} must be a list.")
    return tuple(value)


def _required_records(record: JsonRecord, key: str) -> tuple[JsonRecord, ...]:
    records = _required_list(record, key)
    if not all(isinstance(item, dict) for item in records):
        raise ArtifactValidationError(f"Artifact field {key} must contain objects.")
    return tuple(dict(item) for item in records)


def _required_record(record: JsonRecord, key: str) -> JsonRecord:
    value = record.get(key)
    if not isinstance(value, dict):
        raise ArtifactValidationError(f"Artifact field {key} must be an object.")
    return dict(value)


def _required_record_map(record: JsonRecord, key: str) -> dict[str, JsonRecord]:
    value = _required_record(record, key)
    if not all(isinstance(name, str) and isinstance(item, dict) for name, item in value.items()):
        raise ArtifactValidationError(f"Artifact field {key} must map strings to objects.")
    return {name: dict(item) for name, item in value.items()}
