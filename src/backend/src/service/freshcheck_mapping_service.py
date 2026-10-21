"""Deterministic candidate generation and validation for FreshCheck mappings."""

import re
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.freshcheck_mapping_model import MasterIngredientFreshCheckMappingModel
from src.model.freshcheck_model import FreshCheckIngredientModel
from src.model.master_ingredient_model import MasterIngredientModel

_KB_VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
_MATCH_METHODS = frozenset({"EXACT_CODE", "EXACT_NAME", "MANUAL_REVIEW"})


class MappingManifestValidationError(ValueError):
    """Raised when a reviewed mapping manifest cannot be seeded safely."""


class MappingSeedError(ValueError):
    """Raised when a reviewed mapping cannot be persisted safely."""


@dataclass(frozen=True)
class CatalogIngredient:
    """The stable identity and display name of one catalog ingredient."""

    master_ingredient_id: UUID
    name: str


@dataclass(frozen=True)
class FreshCheckIngredientReference:
    """One FreshCheck ingredient and its reviewed Vietnamese names."""

    freshcheck_ingredient_id: str
    names_vi: tuple[str, ...]


@dataclass(frozen=True)
class ExactNameCandidate:
    """A safe, one-to-one exact-name mapping proposal."""

    master_ingredient_id: UUID
    freshcheck_ingredient_id: str
    match_method: str = "EXACT_NAME"


@dataclass(frozen=True)
class AmbiguousCandidate:
    """A catalog item with multiple exact FreshCheck name matches."""

    master_ingredient_id: UUID
    name: str
    freshcheck_ingredient_ids: tuple[str, ...]


@dataclass(frozen=True)
class MappingCandidateReport:
    """Candidates separated into safe, ambiguous, and unmapped groups."""

    exact_name: tuple[ExactNameCandidate, ...]
    ambiguous: tuple[AmbiguousCandidate, ...]
    unmapped: tuple[CatalogIngredient, ...]


@dataclass(frozen=True)
class ReviewedMapping:
    """One human-reviewed mapping ready for a versioned seed operation."""

    master_ingredient_id: UUID
    freshcheck_ingredient_id: str
    match_method: str
    reviewed_by: str
    note: str | None
    catalog_code: str | None = None
    optional: bool = False


@dataclass(frozen=True)
class MappingManifest:
    """A validated mapping manifest scoped to one FreshCheck KB release."""

    kb_version: str
    mappings: tuple[ReviewedMapping, ...]


class FreshCheckMappingSeedService:
    """Persist reviewed mappings without updating an existing release mapping."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def seed(self, manifest: MappingManifest) -> int:
        """Insert missing mappings and reject invalid or conflicting references."""
        inserted_count = 0
        for mapping in manifest.mappings:
            resolved_master_id = await self._resolve_master_ingredient_id(
                manifest.kb_version, mapping
            )
            if resolved_master_id is None:
                continue
            existing_mapping = await self._session.scalar(
                select(MasterIngredientFreshCheckMappingModel).where(
                    MasterIngredientFreshCheckMappingModel.master_ingredient_id
                    == resolved_master_id,
                    MasterIngredientFreshCheckMappingModel.kb_version
                    == manifest.kb_version,
                )
            )
            if existing_mapping is not None:
                self._assert_idempotent(existing_mapping, mapping)
                continue
            self._session.add(
                MasterIngredientFreshCheckMappingModel(
                    master_ingredient_id=resolved_master_id,
                    kb_version=manifest.kb_version,
                    freshcheck_ingredient_id=mapping.freshcheck_ingredient_id,
                    match_method=mapping.match_method,
                    reviewed_by=mapping.reviewed_by,
                    note=mapping.note,
                )
            )
            inserted_count += 1
        await self._session.flush()
        return inserted_count

    async def _resolve_master_ingredient_id(
        self,
        kb_version: str,
        mapping: ReviewedMapping,
    ) -> UUID | None:
        master_ingredient = await self._session.get(
            MasterIngredientModel,
            mapping.master_ingredient_id,
        )
        freshcheck_ingredient = await self._session.get(
            FreshCheckIngredientModel,
            (kb_version, mapping.freshcheck_ingredient_id),
        )
        if freshcheck_ingredient is None:
            raise MappingSeedError(
                "Mapping references a missing FreshCheck ingredient."
            )

        # 1. Exact UUID lookup (matches legacy host identity directly)
        if master_ingredient is not None:
            return getattr(master_ingredient, "id", mapping.master_ingredient_id)
        # 2. Source catalog code lookup (matches fresh install AI bundle importer)
        source_code = mapping.catalog_code or (
            getattr(freshcheck_ingredient, "code", None)
            if mapping.match_method == "EXACT_CODE"
            else None
        )
        if source_code:
            matching_masters = (
                await self._session.scalars(
                    select(MasterIngredientModel).where(
                        MasterIngredientModel.source_code == str(source_code)
                    )
                )
            ).all()
            if len(matching_masters) == 1:
                return matching_masters[0].id
            if len(matching_masters) > 1:
                raise MappingSeedError(
                    f"Mapping catalog_code '{source_code}' matches multiple master ingredients."
                )

        if getattr(mapping, "optional", False):
            return None

        raise MappingSeedError(
            f"Mapping references a missing master ingredient: {mapping.master_ingredient_id}"
        )

    @staticmethod
    def _assert_idempotent(
        existing_mapping: MasterIngredientFreshCheckMappingModel,
        mapping: ReviewedMapping,
    ) -> None:
        if (
            existing_mapping.freshcheck_ingredient_id
            != mapping.freshcheck_ingredient_id
            or existing_mapping.match_method != mapping.match_method
            or existing_mapping.reviewed_by != mapping.reviewed_by
            or existing_mapping.note != mapping.note
        ):
            raise MappingSeedError(
                "Mapping already exists with different reviewed content."
            )


def build_mapping_candidates(
    catalog_ingredients: tuple[CatalogIngredient, ...],
    freshcheck_ingredients: tuple[FreshCheckIngredientReference, ...],
) -> MappingCandidateReport:
    """Propose only one-to-one exact-name mappings without fuzzy matching."""
    freshcheck_ids_by_name = _freshcheck_ids_by_name(freshcheck_ingredients)
    exact_name: list[ExactNameCandidate] = []
    ambiguous: list[AmbiguousCandidate] = []
    unmapped: list[CatalogIngredient] = []
    for catalog_ingredient in catalog_ingredients:
        matching_ids = freshcheck_ids_by_name.get(
            _comparison_name(catalog_ingredient.name), ()
        )
        if len(matching_ids) == 1:
            exact_name.append(
                ExactNameCandidate(
                    catalog_ingredient.master_ingredient_id,
                    matching_ids[0],
                )
            )
        elif matching_ids:
            ambiguous.append(
                AmbiguousCandidate(
                    catalog_ingredient.master_ingredient_id,
                    catalog_ingredient.name,
                    matching_ids,
                )
            )
        else:
            unmapped.append(catalog_ingredient)
    return MappingCandidateReport(
        tuple(exact_name),
        tuple(ambiguous),
        tuple(unmapped),
    )


async def resolve_manifest_mappings_to_catalog(
    session: AsyncSession,
    manifest: MappingManifest,
    artifact_ingredients_by_id: dict[str, Any],
) -> MappingManifest:
    """Resolve reviewed manifest master IDs to current catalog identities before planning."""
    resolved_mappings: list[ReviewedMapping] = []
    resolved_by_master_id: dict[UUID, ReviewedMapping] = {}

    for mapping in manifest.mappings:
        target_fc = artifact_ingredients_by_id.get(mapping.freshcheck_ingredient_id)
        if target_fc is None:
            raise MappingSeedError(
                f"Mapping references unknown FreshCheck ingredient: {mapping.freshcheck_ingredient_id}"
            )

        # 1. Direct UUID lookup (host identity)
        master = await session.get(MasterIngredientModel, mapping.master_ingredient_id)
        master_id: UUID | None = master.id if master is not None else None

        # Verify source_code matches catalog_code if both present
        if (
            master is not None
            and mapping.catalog_code is not None
            and master.source_code is not None
            and str(master.source_code) != mapping.catalog_code
        ):
            raise MappingSeedError(
                f"Reviewed mapping catalog_code '{mapping.catalog_code}' does not match "
                f"master ingredient source_code '{master.source_code}' for {mapping.master_ingredient_id}."
            )

        # 2. Source catalog code lookup (AI code-based identity)
        if master_id is None:
            source_code = mapping.catalog_code or (
                target_fc.get("code") if mapping.match_method == "EXACT_CODE" else None
            )
            if source_code:
                matching = (
                    await session.scalars(
                        select(MasterIngredientModel).where(
                            MasterIngredientModel.source_code == str(source_code)
                        )
                    )
                ).all()
                if len(matching) == 1:
                    master_id = matching[0].id
                elif len(matching) > 1:
                    raise MappingSeedError(
                        f"Mapping catalog_code '{source_code}' matches multiple master ingredients."
                    )

        if master_id is None:
            if mapping.optional:
                continue
            raise MappingSeedError(
                f"Reviewed mapping '{mapping.freshcheck_ingredient_id}' could not be resolved "
                f"against current catalog (UUID: {mapping.master_ingredient_id}, code: {mapping.catalog_code})"
            )

        if master_id in resolved_by_master_id:
            existing = resolved_by_master_id[master_id]
            if (
                existing.freshcheck_ingredient_id != mapping.freshcheck_ingredient_id
                or existing.match_method != mapping.match_method
                or existing.reviewed_by != mapping.reviewed_by
                or existing.note != mapping.note
            ):
                raise MappingSeedError(
                    f"Conflicting reviewed mappings resolved to the same master ingredient '{master_id}'."
                )
            continue

        resolved_item = ReviewedMapping(
            master_ingredient_id=master_id,
            freshcheck_ingredient_id=mapping.freshcheck_ingredient_id,
            match_method=mapping.match_method,
            reviewed_by=mapping.reviewed_by,
            note=mapping.note,
            catalog_code=mapping.catalog_code,
            optional=mapping.optional,
        )
        resolved_by_master_id[master_id] = resolved_item
        resolved_mappings.append(resolved_item)

    return MappingManifest(manifest.kb_version, tuple(resolved_mappings))


def parse_mapping_manifest(payload: object) -> MappingManifest:
    """Validate a reviewed YAML manifest before it can create mappings."""
    if not isinstance(payload, dict):
        raise MappingManifestValidationError("Mapping manifest must be an object.")
    if _contains_null(payload):
        raise MappingManifestValidationError(
            "Mapping manifest cannot contain null values."
        )
    kb_version = _manifest_string(payload, "kb_version")
    if not _KB_VERSION_PATTERN.fullmatch(kb_version):
        raise MappingManifestValidationError("Mapping manifest kb_version is invalid.")
    mappings_value = payload.get("mappings")
    if not isinstance(mappings_value, list):
        raise MappingManifestValidationError(
            "Mapping manifest mappings must be a list."
        )
    mappings = tuple(_parse_reviewed_mapping(item) for item in mappings_value)
    master_ingredient_ids = [mapping.master_ingredient_id for mapping in mappings]
    if len(set(master_ingredient_ids)) != len(master_ingredient_ids):
        raise MappingManifestValidationError(
            "Mapping manifest contains duplicate master_ingredient_id values."
        )
    return MappingManifest(kb_version, mappings)


def _freshcheck_ids_by_name(
    freshcheck_ingredients: tuple[FreshCheckIngredientReference, ...],
) -> dict[str, tuple[str, ...]]:
    ids_by_name: dict[str, set[str]] = {}
    for ingredient in freshcheck_ingredients:
        for name in ingredient.names_vi:
            comparison_name = _comparison_name(name)
            ids_by_name.setdefault(comparison_name, set()).add(
                ingredient.freshcheck_ingredient_id
            )
    return {
        name: tuple(sorted(ingredient_ids))
        for name, ingredient_ids in ids_by_name.items()
    }


def _comparison_name(name: str) -> str:
    """Return a case-insensitive exact-name key without fuzzy normalization."""
    return name.strip().casefold()


def _parse_reviewed_mapping(value: object) -> ReviewedMapping:
    if not isinstance(value, dict):
        raise MappingManifestValidationError("Each mapping must be an object.")
    master_ingredient_id = _parse_uuid(_manifest_string(value, "master_ingredient_id"))
    freshcheck_ingredient_id = _manifest_string(value, "freshcheck_ingredient_id")
    match_method = _manifest_string(value, "match_method")
    if match_method not in _MATCH_METHODS:
        raise MappingManifestValidationError("Mapping match_method is not supported.")
    note = value.get("note")
    if note is not None and (not isinstance(note, str) or not note.strip()):
        raise MappingManifestValidationError("Mapping note must be a non-empty string.")
    catalog_code = value.get("catalog_code")
    if catalog_code is not None and (
        not isinstance(catalog_code, str) or not catalog_code.strip()
    ):
        raise MappingManifestValidationError(
            "Mapping catalog_code must be a non-empty string."
        )
    optional = value.get("optional", False)
    if not isinstance(optional, bool):
        raise MappingManifestValidationError("Mapping optional must be a boolean.")
    return ReviewedMapping(
        master_ingredient_id,
        freshcheck_ingredient_id,
        match_method,
        _manifest_string(value, "reviewed_by"),
        note,
        catalog_code.strip() if catalog_code else None,
        optional=optional,
    )


def _manifest_string(record: dict[object, object], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise MappingManifestValidationError(
            f"Mapping manifest field {key} must be a non-empty string."
        )
    return value


def _parse_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as error:
        raise MappingManifestValidationError(
            "Mapping master_ingredient_id must be a UUID."
        ) from error


def _contains_null(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, dict):
        return any(_contains_null(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_null(item) for item in value)
    return False
