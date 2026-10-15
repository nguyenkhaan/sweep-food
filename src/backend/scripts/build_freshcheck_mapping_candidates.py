"""Create a review-only report of deterministic FreshCheck mapping candidates."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db import build_async_database_url
from src.model.freshcheck_model import FreshCheckIngredientModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    FreshCheckIngredientReference,
    build_mapping_candidates,
)


def parse_arguments() -> argparse.Namespace:
    """Parse a read-only candidate-report command."""
    parser = argparse.ArgumentParser(description="Build FreshCheck mapping candidates.")
    parser.add_argument("--database-url-env", required=True)
    parser.add_argument("--kb-version", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


async def build_report(arguments: argparse.Namespace) -> None:
    """Read catalog and KB rows, then write only a local review report."""
    database_url = os.getenv(arguments.database_url_env)
    if not database_url:
        raise ValueError(f"Environment variable {arguments.database_url_env} is required.")
    engine = create_async_engine(build_async_database_url(database_url), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
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
                            FreshCheckIngredientModel.kb_version == arguments.kb_version
                        )
                    )
                ).all()
            )
    finally:
        await engine.dispose()
    report = build_mapping_candidates(masters, freshcheck)
    arguments.output.write_text(
        json.dumps(
            {
                "kb_version": arguments.kb_version,
                "exact_name": [item.__dict__ | {"master_ingredient_id": str(item.master_ingredient_id)} for item in report.exact_name],
                "ambiguous": [item.__dict__ | {"master_ingredient_id": str(item.master_ingredient_id)} for item in report.ambiguous],
                "unmapped": [item.__dict__ | {"master_ingredient_id": str(item.master_ingredient_id)} for item in report.unmapped],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    asyncio.run(build_report(parse_arguments()))
