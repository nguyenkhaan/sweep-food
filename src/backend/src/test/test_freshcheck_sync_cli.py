"""Unit tests for the FreshCheck sync command interface."""

import asyncio
from unittest.mock import Mock

import pytest

from scripts import sync_freshcheck_kb
from scripts.sync_freshcheck_kb import parse_arguments
from src.service.freshcheck_sync_service import FreshCheckArtifact


@pytest.mark.parametrize(
    "operation",
    ("--dry-run", "--stage", "--activate", "--rollback"),
)
def test_sync_cli_requires_one_explicit_operation(operation: str) -> None:
    """Each supported CLI operation is explicit and mutually exclusive."""
    arguments = parse_arguments(["--artifact", "artifact.json", operation])

    assert arguments.artifact.name == "artifact.json"
    assert getattr(arguments, operation.removeprefix("--").replace("-", "_")) is True


def test_sync_cli_rejects_multiple_operations() -> None:
    """A release cannot be staged and activated by one ambiguous command."""
    with pytest.raises(SystemExit):
        parse_arguments(["--artifact", "artifact.json", "--stage", "--activate"])


def test_dry_run_does_not_create_a_database_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Artifact validation is safe even when no database URL is configured."""
    artifact = FreshCheckArtifact(
        raw={},
        kb_version="1.2.3",
        checksum=f"sha256:{'a' * 64}",
        source_commit="a" * 40,
        stats={},
        sources=(),
        claims=(),
        archetypes={},
        ingredients={},
    )
    load_artifact = Mock(return_value=artifact)
    create_engine = Mock()
    monkeypatch.setattr(sync_freshcheck_kb, "load_artifact", load_artifact)
    monkeypatch.setattr(sync_freshcheck_kb, "create_async_engine", create_engine)

    result = asyncio.run(
        sync_freshcheck_kb.synchronize(
            parse_arguments(["--artifact", "artifact.json", "--dry-run"])
        )
    )

    assert result == "dry_run"
    load_artifact.assert_called_once()
    create_engine.assert_not_called()
