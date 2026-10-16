"""Build, seed, activate, and safely map one FreshCheck knowledge-base release."""

from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from scripts.sync_freshcheck_kb import load_artifact
from src.db import build_async_database_url
from src.model.master_ingredient_model import MasterIngredientModel
from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    ExactNameCandidate,
    FreshCheckIngredientReference,
    FreshCheckMappingSeedService,
    MappingManifest,
    ReviewedMapping,
    build_mapping_candidates,
)
from src.service.freshcheck_sync_service import (
    ArtifactValidationError,
    FreshCheckArtifact,
    FreshCheckSyncService,
    ReleaseConflictError,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_ROOT.parents[1]
FRESHNESS_ROOT = REPOSITORY_ROOT / "data_freshness"
ARTIFACT_PATH = FRESHNESS_ROOT / "build" / "freshcheck_kb.json"
MAPPING_REVIEWER = "seed_freshness"
MAPPING_NOTE = "Seeded from a unique exact-name match."


class FreshnessSeedError(ValueError):
    """Raised when the database cannot be seeded without unsafe mappings."""


@dataclass(frozen=True)
class MappingPlan:
    """Safe mapping rows and omitted catalog items for one KB version."""

    mapping_manifest: MappingManifest
    ambiguous_count: int
    unmapped_count: int


@dataclass(frozen=True)
class SeedConfiguration:
    """Runtime inputs for one FreshCheck database seed operation."""

    artifact: FreshCheckArtifact
    database_url: str
    actor: str
    apply_changes: bool


@dataclass(frozen=True)
class SeedResult:
    """Safe-to-print outcome of a FreshCheck seed operation."""

    kb_version: str
    stage_action: str
    activation_action: str
    inserted_mappings: int
    exact_mappings: int
    ambiguous_mappings: int
    unmapped_ingredients: int


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse an explicit dry-run or apply operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--actor",
        default="seed-freshness",
        help="Audit actor recorded for the KB release.",
    )
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument(
        "--dry-run",
        dest="apply_changes",
        action="store_false",
        help="Build and validate the release without writing to PostgreSQL.",
    )
    operation.add_argument(
        "--apply",
        dest="apply_changes",
        action="store_true",
        help="Stage, activate, and map the release in PostgreSQL.",
    )
    parser.set_defaults(apply_changes=False)
    return parser.parse_args(arguments)


def build_artifact() -> Path:
    """Build the immutable artifact from the reviewed FreshCheck source data."""
    subprocess.run(
        ("uv", "run", "python", "scripts/build_kb.py"),
        cwd=FRESHNESS_ROOT,
        check=True,
    )
    if not ARTIFACT_PATH.is_file():
        raise FreshnessSeedError("FreshCheck artifact was not created by the builder.")
    return ARTIFACT_PATH


def build_mapping_plan(
    kb_version: str,
    catalog_ingredients: tuple[CatalogIngredient, ...],
    freshcheck_ingredients: tuple[FreshCheckIngredientReference, ...],
) -> MappingPlan:
    """Create mappings only for one-to-one exact names in the reviewed KB."""
    candidates = build_mapping_candidates(catalog_ingredients, freshcheck_ingredients)
    mappings = tuple(
        _reviewed_mapping(candidate) for candidate in candidates.exact_name
    )
    return MappingPlan(
        MappingManifest(kb_version, mappings),
        len(candidates.ambiguous),
        len(candidates.unmapped),
    )


def _reviewed_mapping(candidate: ExactNameCandidate) -> ReviewedMapping:
    return ReviewedMapping(
        candidate.master_ingredient_id,
        candidate.freshcheck_ingredient_id,
        "EXACT_NAME",
        MAPPING_REVIEWER,
        MAPPING_NOTE,
    )


def artifact_ingredients(
    artifact: FreshCheckArtifact,
) -> tuple[FreshCheckIngredientReference, ...]:
    """Convert one validated artifact into exact-name mapping references."""
    references: list[FreshCheckIngredientReference] = []
    for ingredient_id, ingredient in artifact.ingredients.items():
        names = ingredient.get("names_vi")
        if not isinstance(names, list) or not all(
            isinstance(name, str) for name in names
        ):
            raise ArtifactValidationError(
                "Artifact ingredient names_vi must be strings."
            )
        references.append(FreshCheckIngredientReference(ingredient_id, tuple(names)))
    return tuple(references)


async def seed_freshness(configuration: SeedConfiguration) -> SeedResult:
    """Plan or atomically write one KB release and its safe exact-name mappings."""
    engine = create_async_engine(
        build_async_database_url(configuration.database_url),
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        catalog_ingredients = await _catalog_ingredients(session_factory)
        plan = build_mapping_plan(
            configuration.artifact.kb_version,
            catalog_ingredients,
            artifact_ingredients(configuration.artifact),
        )
        _require_exact_mapping(plan)
        if not configuration.apply_changes:
            return _dry_run_result(configuration.artifact.kb_version, plan)
        return await _apply_seed(session_factory, configuration, plan)
    finally:
        await engine.dispose()


async def _catalog_ingredients(
    session_factory: async_sessionmaker[AsyncSession],
) -> tuple[CatalogIngredient, ...]:
    async with session_factory() as session:
        records = (await session.scalars(select(MasterIngredientModel))).all()
    return tuple(CatalogIngredient(record.id, record.name) for record in records)


def _require_exact_mapping(plan: MappingPlan) -> None:
    if not plan.mapping_manifest.mappings:
        raise FreshnessSeedError(
            "No unique exact-name FreshCheck mapping was found. "
            "Seed or review master ingredients before applying this release."
        )


def _dry_run_result(kb_version: str, plan: MappingPlan) -> SeedResult:
    return SeedResult(
        kb_version,
        "dry_run",
        "dry_run",
        0,
        len(plan.mapping_manifest.mappings),
        plan.ambiguous_count,
        plan.unmapped_count,
    )


async def _apply_seed(
    session_factory: async_sessionmaker[AsyncSession],
    configuration: SeedConfiguration,
    plan: MappingPlan,
) -> SeedResult:
    async with session_factory() as session, session.begin():
        sync_service = FreshCheckSyncService(session)
        stage_result = await sync_service.stage(
            configuration.artifact, configuration.actor
        )
        inserted_mappings = await FreshCheckMappingSeedService(session).seed(
            plan.mapping_manifest
        )
        activation_result = await sync_service.activate(
            configuration.artifact,
            configuration.actor,
        )
    return SeedResult(
        configuration.artifact.kb_version,
        stage_result.action,
        activation_result.action,
        inserted_mappings,
        len(plan.mapping_manifest.mappings),
        plan.ambiguous_count,
        plan.unmapped_count,
    )


def print_result(result: SeedResult) -> None:
    """Print a release summary without exposing credentials or ingredient data."""
    print(f"FreshCheck KB version: {result.kb_version}")
    print(f"KB stage: {result.stage_action}")
    print(f"KB activation: {result.activation_action}")
    print(f"Exact mappings: {result.exact_mappings}")
    print(f"Inserted mappings: {result.inserted_mappings}")
    print(f"Ambiguous mappings skipped: {result.ambiguous_mappings}")
    print(f"Unmapped ingredients skipped: {result.unmapped_ingredients}")


def main(arguments: list[str] | None = None) -> int:
    """Build and seed FreshCheck data using DATABASE_URL from the backend .env file."""
    load_dotenv(BACKEND_ROOT / ".env")
    parsed_arguments = parse_arguments(arguments)
    try:
        artifact = load_artifact(build_artifact())
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise FreshnessSeedError("DATABASE_URL is required in src/backend/.env.")
        result = asyncio.run(
            seed_freshness(
                SeedConfiguration(
                    artifact,
                    database_url,
                    parsed_arguments.actor,
                    parsed_arguments.apply_changes,
                )
            )
        )
    except (
        ArtifactValidationError,
        FreshnessSeedError,
        ReleaseConflictError,
        OSError,
        subprocess.CalledProcessError,
        ValueError,
    ) as error:
        print(f"FreshCheck seed failed: {error}", file=sys.stderr)
        return 2
    except Exception:  # noqa: BLE001 - do not expose database driver details.
        print(
            "FreshCheck seed failed before completing its transaction.", file=sys.stderr
        )
        return 1
    print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
