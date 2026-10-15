"""Unit tests for the FreshCheck sync command interface."""

import pytest

from scripts.sync_freshcheck_kb import parse_arguments


@pytest.mark.parametrize("operation", ("--dry-run", "--stage", "--activate"))
def test_sync_cli_requires_one_explicit_operation(operation: str) -> None:
    """Each supported CLI operation is explicit and mutually exclusive."""
    arguments = parse_arguments(["--artifact", "artifact.json", operation])

    assert arguments.artifact.name == "artifact.json"
    assert getattr(arguments, operation.removeprefix("--").replace("-", "_")) is True


def test_sync_cli_rejects_multiple_operations() -> None:
    """A release cannot be staged and activated by one ambiguous command."""
    with pytest.raises(SystemExit):
        parse_arguments(
            ["--artifact", "artifact.json", "--stage", "--activate"]
        )
