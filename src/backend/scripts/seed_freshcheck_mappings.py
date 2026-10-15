"""Seed reviewed FreshCheck mappings into an Alembic-managed schema."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db import build_async_database_url
from src.model.freshcheck_mapping_model import MasterIngredientFreshCheckMappingModel
from src.model.freshcheck_model import FreshCheckIngredientModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    FreshCheckIngredientReference,
    FreshCheckMappingSeedService,
    MappingManifestValidationError,
    MappingSeedError,
    build_mapping_candidates,
    parse_mapping_manifest,
)


def parse_arguments() -> argparse.Namespace:
    """Parse the reviewed-manifest seed command."""
    parser = argparse.ArgumentParser(description="Seed reviewed FreshCheck mappings.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--database-url-env", required=True)
    parser.add_argument("--coverage-output", required=True, type=Path)
    return parser.parse_args()


async def seed(arguments: argparse.Namespace) -> tuple[int, dict[str, object]]:
    """Validate and persist a reviewed manifest in one transaction."""
    payload = yaml.safe_load(arguments.manifest.read_text(encoding="utf-8"))
    manifest = parse_mapping_manifest(payload)
    database_url = os.getenv(arguments.database_url_env)
    if not database_url:
        raise MappingManifestValidationError(
            f"Environment variable {arguments.database_url_env} is required."
        )
    engine = create_async_engine(build_async_database_url(database_url), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            async with session.begin():
                inserted_count = await FreshCheckMappingSeedService(session).seed(manifest)
        async with session_factory() as session:
            coverage = await _coverage_report(session, manifest.kb_version)
    finally:
        await engine.dispose()
    return inserted_count, coverage


async def _coverage_report(session: AsyncSession, kb_version: str) -> dict[str, object]:
    """Return reviewed coverage without inferring mappings from ambiguous names."""
    masters = tuple(
        CatalogIngredient(record.id, record.name)
        for record in (
            await session.scalars(select(MasterIngredientModel))
        ).all()
    )
    freshcheck = tuple(
        FreshCheckIngredientReference(record.freshcheck_ingredient_id, tuple(record.names_vi))
        for record in (
            await session.scalars(
                select(FreshCheckIngredientModel).where(
                    FreshCheckIngredientModel.kb_version == kb_version
                )
            )
        ).all()
    )
    mapped_ids = set(
        (
            await session.scalars(
                select(MasterIngredientFreshCheckMappingModel.master_ingredient_id).where(
                    MasterIngredientFreshCheckMappingModel.kb_version == kb_version
                )
            )
        ).all()
    )
    candidates = build_mapping_candidates(masters, freshcheck)
    return {
        "kb_version": kb_version,
        "mapped": sorted(str(master_id) for master_id in mapped_ids),
        "unmapped": [
            str(item.master_ingredient_id)
            for item in candidates.unmapped
            if item.master_ingredient_id not in mapped_ids
        ],
        "ambiguous": [
            str(item.master_ingredient_id)
            for item in candidates.ambiguous
            if item.master_ingredient_id not in mapped_ids
        ],
    }


def main() -> int:
    """Report safe seed errors without exposing database credentials."""
    arguments = parse_arguments()
    try:
        inserted_count, coverage = asyncio.run(seed(arguments))
    except (MappingManifestValidationError, MappingSeedError, OSError, yaml.YAMLError) as error:
        print(f"FreshCheck mapping seed failed: {error}")
        return 2
    except Exception:
        print("FreshCheck mapping seed failed before completing its transaction.")
        return 1
    arguments.coverage_output.write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"FreshCheck mapping seed result: inserted={inserted_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
