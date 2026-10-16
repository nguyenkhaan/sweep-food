"""Validation and persistence helpers for FreshCheck KB releases."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import FreshCheckKBVersionStatus
from src.model.freshcheck_model import (
    FreshCheckArchetypeModel,
    FreshCheckClaimModel,
    FreshCheckIngredientModel,
    FreshCheckKBVersionModel,
    FreshCheckSourceModel,
)

JsonRecord = dict[str, object]

_CHECKSUM_EXCLUDED_KEYS: Final = frozenset({"checksum", "generated_at"})
_CHECKSUM_PATTERN: Final = re.compile(r"sha256:[0-9a-f]{64}")
_COMMIT_PATTERN: Final = re.compile(r"[0-9a-f]{40}")
_VERSION_PATTERN: Final = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


class ArtifactValidationError(ValueError):
    """Raised when a FreshCheck artifact cannot be staged safely."""


class ReleaseConflictError(ValueError):
    """Raised when a release version conflicts with a different artifact."""


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


@dataclass(frozen=True)
class SyncResult:
    """Outcome of staging or activating one KB release."""

    action: str
    kb_version: str
    record_counts: dict[str, int]


@dataclass(frozen=True)
class ReleaseModels:
    """Database rows grouped in the order required by their foreign keys."""

    version: FreshCheckKBVersionModel
    sources: tuple[FreshCheckSourceModel, ...]
    claims: tuple[FreshCheckClaimModel, ...]
    archetypes: tuple[FreshCheckArchetypeModel, ...]
    ingredients: tuple[FreshCheckIngredientModel, ...]


class FreshCheckSyncService:
    """Stage and activate validated FreshCheck artifacts in a caller-owned transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def stage(self, artifact: FreshCheckArtifact, actor: str) -> SyncResult:
        """Persist a release once, rejecting a version with another checksum."""
        _require_actor(actor)
        existing_version = await self._session.get(
            FreshCheckKBVersionModel,
            artifact.kb_version,
        )
        if existing_version is not None:
            _assert_matching_checksum(existing_version, artifact)
            return _sync_result("already_staged", artifact)

        await _persist_release(self._session, _release_models(artifact, actor))
        return _sync_result("staged", artifact)

    async def activate(self, artifact: FreshCheckArtifact, actor: str) -> SyncResult:
        """Make a staged release active and retire the formerly active release."""
        _require_actor(actor)
        target_version = await self._session.get(
            FreshCheckKBVersionModel,
            artifact.kb_version,
            with_for_update=True,
        )
        if target_version is None:
            raise ReleaseConflictError("Release must be staged before activation.")
        _assert_matching_checksum(target_version, artifact)
        if target_version.status is FreshCheckKBVersionStatus.RETIRED:
            raise ReleaseConflictError("A retired release cannot be activated again.")
        if target_version.status is FreshCheckKBVersionStatus.ACTIVE:
            return _sync_result("already_active", artifact)

        await self._replace_active_version(target_version, actor)
        return _sync_result("activated", artifact)

    async def rollback(self, artifact: FreshCheckArtifact, actor: str) -> SyncResult:
        """Reactivate one retired release after verifying its exact artifact."""
        _require_actor(actor)
        target_version = await self._session.get(
            FreshCheckKBVersionModel,
            artifact.kb_version,
            with_for_update=True,
        )
        if target_version is None:
            raise ReleaseConflictError("Rollback release does not exist.")
        _assert_matching_checksum(target_version, artifact)
        if target_version.status is FreshCheckKBVersionStatus.STAGED:
            raise ReleaseConflictError("Rollback release must have been active before.")
        if target_version.status is FreshCheckKBVersionStatus.ACTIVE:
            return _sync_result("already_active", artifact)

        await self._replace_active_version(target_version, actor)
        return _sync_result("rolled_back", artifact)

    async def _replace_active_version(
        self,
        target_version: FreshCheckKBVersionModel,
        actor: str,
    ) -> None:
        """Switch the singleton ACTIVE status without violating its unique index."""

        active_version = await self._session.scalar(
            select(FreshCheckKBVersionModel)
            .where(FreshCheckKBVersionModel.status == FreshCheckKBVersionStatus.ACTIVE)
            .with_for_update()
        )
        activated_at = datetime.now(UTC)
        if active_version is not None:
            active_version.status = FreshCheckKBVersionStatus.RETIRED
            active_version.retired_at = activated_at
            active_version.retired_by = actor
            await self._session.flush()
        target_version.status = FreshCheckKBVersionStatus.ACTIVE
        target_version.activated_at = activated_at
        target_version.activated_by = actor
        target_version.retired_at = None
        target_version.retired_by = None
        await self._session.flush()


def calculate_artifact_checksum(payload: JsonRecord) -> str:
    """Calculate the canonical checksum emitted by the KB build process."""
    checksum_payload = {
        key: value
        for key, value in payload.items()
        if key not in _CHECKSUM_EXCLUDED_KEYS
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
        raise ArtifactValidationError(
            "Artifact kb_version must use semantic versioning."
        )
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
            raise ArtifactValidationError(
                "Archetype key does not match its record identifier."
            )
        _require_string_fields(archetype, ("name_vi",))
        _required_list(archetype, "applies_to_groups")
        _required_record(archetype, "sensory_tiers")
        _required_list(archetype, "inspection_rubric")
        _required_record(archetype, "preservation_protocols")
        _required_list(archetype, "business_rules")
    for ingredient_id, ingredient in artifact.ingredients.items():
        if _required_string(ingredient, "id") != ingredient_id:
            raise ArtifactValidationError(
                "Ingredient key does not match its record identifier."
            )
        _require_string_fields(ingredient, ("code", "archetype"))
        _required_list(ingredient, "names_vi")
        _required_record(ingredient, "base_shelf_life_hours")


def _validate_references(artifact: FreshCheckArtifact) -> None:
    source_ids = {_required_string(source, "id") for source in artifact.sources}
    claim_ids = {_required_string(claim, "id") for claim in artifact.claims}
    for claim in artifact.claims:
        if _required_string(claim, "source") not in source_ids:
            raise ArtifactValidationError(
                "Claim references a source outside this artifact."
            )
    for ingredient in artifact.ingredients.values():
        if _required_string(ingredient, "archetype") not in artifact.archetypes:
            raise ArtifactValidationError("Ingredient references an unknown archetype.")
        shelf_life = _required_record(ingredient, "base_shelf_life_hours")
        for rule in shelf_life.values():
            if not isinstance(rule, dict):
                raise ArtifactValidationError("Shelf-life rules must be objects.")
            if _required_string(rule, "claim") not in claim_ids:
                raise ArtifactValidationError(
                    "Shelf-life rule references an unknown claim."
                )


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
        raise ArtifactValidationError(
            f"Artifact field {key} must be a non-empty string."
        )
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
    return tuple(dict(cast(dict[str, object], item)) for item in records)


def _required_record(record: JsonRecord, key: str) -> JsonRecord:
    value = record.get(key)
    if not isinstance(value, dict):
        raise ArtifactValidationError(f"Artifact field {key} must be an object.")
    return dict(cast(dict[str, object], value))


def _required_record_map(record: JsonRecord, key: str) -> dict[str, JsonRecord]:
    value = _required_record(record, key)
    if not all(
        isinstance(name, str) and isinstance(item, dict) for name, item in value.items()
    ):
        raise ArtifactValidationError(
            f"Artifact field {key} must map strings to objects."
        )
    return {name: dict(cast(dict[str, object], item)) for name, item in value.items()}


def _require_actor(actor: str) -> None:
    if not actor.strip():
        raise ValueError("A non-empty actor is required for KB audit fields.")


def _assert_matching_checksum(
    existing_version: FreshCheckKBVersionModel,
    artifact: FreshCheckArtifact,
) -> None:
    if existing_version.checksum != artifact.checksum:
        raise ReleaseConflictError(
            "KB version already exists with a different checksum."
        )


def _sync_result(action: str, artifact: FreshCheckArtifact) -> SyncResult:
    return SyncResult(
        action=action,
        kb_version=artifact.kb_version,
        record_counts=artifact.record_counts,
    )


async def _persist_release(session: AsyncSession, release: ReleaseModels) -> None:
    """Flush each FK dependency layer before adding its dependent rows."""
    session.add(release.version)
    await session.flush()
    for records in (
        release.sources,
        release.claims,
        release.archetypes,
        release.ingredients,
    ):
        session.add_all(records)
        await session.flush()


def _release_models(
    artifact: FreshCheckArtifact,
    actor: str,
) -> ReleaseModels:
    return ReleaseModels(
        FreshCheckKBVersionModel(
            kb_version=artifact.kb_version,
            status=FreshCheckKBVersionStatus.STAGED,
            checksum=artifact.checksum,
            source_commit=artifact.source_commit,
            stats=artifact.stats,
            artifact=artifact.raw,
            staged_by=actor,
        ),
        tuple(
            _source_model(artifact.kb_version, source) for source in artifact.sources
        ),
        tuple(_claim_model(artifact.kb_version, claim) for claim in artifact.claims),
        tuple(
            _archetype_model(artifact.kb_version, archetype_id, archetype)
            for archetype_id, archetype in artifact.archetypes.items()
        ),
        tuple(
            _ingredient_model(artifact.kb_version, ingredient_id, ingredient)
            for ingredient_id, ingredient in artifact.ingredients.items()
        ),
    )


def _source_model(kb_version: str, source: JsonRecord) -> FreshCheckSourceModel:
    return FreshCheckSourceModel(
        kb_version=kb_version,
        source_id=_required_string(source, "id"),
        title=_required_string(source, "title"),
        tier=_required_string(source, "tier"),
        license=_required_string(source, "license"),
        accessed=_required_string(source, "accessed"),
        source_data=source,
    )


def _claim_model(kb_version: str, claim: JsonRecord) -> FreshCheckClaimModel:
    return FreshCheckClaimModel(
        kb_version=kb_version,
        claim_id=_required_string(claim, "id"),
        source_id=_required_string(claim, "source"),
        statement_vi=_required_string(claim, "statement_vi"),
        locator=_required_string(claim, "locator"),
        conditions=cast(list[object], claim["conditions"]),
        evidence_level=_required_string(claim, "evidence_level"),
        status=_required_string(claim, "status"),
        extracted_by=_required_string(claim, "extracted_by"),
        reviewed_by=_required_string(claim, "reviewed_by"),
        claim_data=claim,
    )


def _archetype_model(
    kb_version: str,
    archetype_id: str,
    archetype: JsonRecord,
) -> FreshCheckArchetypeModel:
    return FreshCheckArchetypeModel(
        kb_version=kb_version,
        archetype_id=archetype_id,
        name_vi=_required_string(archetype, "name_vi"),
        applies_to_groups=cast(list[object], archetype["applies_to_groups"]),
        sensory_tiers=_required_record(archetype, "sensory_tiers"),
        inspection_rubric=cast(list[object], archetype["inspection_rubric"]),
        preservation_protocols=_required_record(archetype, "preservation_protocols"),
        business_rules=cast(list[object], archetype["business_rules"]),
    )


def _ingredient_model(
    kb_version: str,
    ingredient_id: str,
    ingredient: JsonRecord,
) -> FreshCheckIngredientModel:
    return FreshCheckIngredientModel(
        kb_version=kb_version,
        freshcheck_ingredient_id=ingredient_id,
        archetype_id=_required_string(ingredient, "archetype"),
        code=_required_string(ingredient, "code"),
        names_vi=cast(list[object], ingredient["names_vi"]),
        base_shelf_life_hours=_required_record(ingredient, "base_shelf_life_hours"),
    )
