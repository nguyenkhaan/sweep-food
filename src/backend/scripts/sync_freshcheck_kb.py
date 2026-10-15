"""Stage or activate one validated FreshCheck knowledge-base artifact."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db import build_async_database_url
from src.service.freshcheck_sync_service import (
    ArtifactValidationError,
    FreshCheckArtifact,
    FreshCheckSyncService,
    ReleaseConflictError,
    parse_freshcheck_artifact,
)


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    """Parse a single explicit FreshCheck synchronization operation."""
    parser = argparse.ArgumentParser(
        description="Stage or activate a versioned FreshCheck KB artifact."
    )
    parser.add_argument(
        "--artifact",
        required=True,
        type=Path,
        help="Path to the validated FreshCheck JSON artifact.",
    )
    parser.add_argument(
        "--database-url-env",
        default="DATABASE_URL",
        help="Name of the environment variable containing the target database URL.",
    )
    parser.add_argument(
        "--actor",
        default="freshcheck-sync",
        help="Audit actor recorded when the release is staged or activated.",
    )
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the artifact and print its sync plan without a database connection.",
    )
    operation.add_argument(
        "--stage",
        action="store_true",
        help="Stage the artifact in the Alembic-managed FreshCheck schema.",
    )
    operation.add_argument(
        "--activate",
        action="store_true",
        help="Activate an already staged artifact and retire the current active release.",
    )
    return parser.parse_args(arguments)


def load_artifact(artifact_path: Path) -> FreshCheckArtifact:
    """Load and validate one JSON artifact without exposing file contents on error."""
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactValidationError("Unable to read the FreshCheck artifact.") from error
    if not isinstance(payload, dict):
        raise ArtifactValidationError("FreshCheck artifact root must be a JSON object.")
    return parse_freshcheck_artifact(payload)


def print_sync_plan(artifact: FreshCheckArtifact) -> None:
    """Print release metadata that is safe to expose in local command output."""
    print(f"FreshCheck KB {artifact.kb_version}")
    print(f"checksum: {artifact.checksum}")
    print(f"source commit: {artifact.source_commit}")
    for record_type, count in artifact.record_counts.items():
        print(f"{record_type}: {count}")


async def synchronize(arguments: argparse.Namespace) -> str:
    """Run the selected operation and return its auditable outcome."""
    artifact = load_artifact(arguments.artifact)
    print_sync_plan(artifact)
    if arguments.dry_run:
        return "dry_run"

    database_url = os.getenv(arguments.database_url_env)
    if not database_url:
        raise ArtifactValidationError(
            f"Environment variable {arguments.database_url_env} is required."
        )
    engine = create_async_engine(
        build_async_database_url(database_url),
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            async with session.begin():
                service = FreshCheckSyncService(session)
                result = (
                    await service.stage(artifact, arguments.actor)
                    if arguments.stage
                    else await service.activate(artifact, arguments.actor)
                )
    finally:
        await engine.dispose()
    return result.action


def main(arguments: list[str] | None = None) -> int:
    """Execute the CLI without printing database credentials in error paths."""
    try:
        operation = asyncio.run(synchronize(parse_arguments(arguments)))
    except (ArtifactValidationError, ReleaseConflictError, ValueError) as error:
        print(f"FreshCheck sync failed: {error}", file=sys.stderr)
        return 2
    except Exception:
        print("FreshCheck sync failed before completing its transaction.", file=sys.stderr)
        return 1
    print(f"FreshCheck sync result: {operation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
