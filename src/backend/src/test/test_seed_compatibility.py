"""Unit coverage for the deprecated seed-module compatibility command."""

import pytest

from src import seed


def test_legacy_seed_module_delegates_to_canonical_entry_point(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Keep the legacy command path without creating another seed implementation."""
    calls: list[None] = []

    def _canonical_main() -> None:
        calls.append(None)

    monkeypatch.setattr(seed, "canonical_main", _canonical_main)

    seed.main()

    captured = capsys.readouterr()
    assert calls == [None]
    assert "uv run python scripts/seed.py [--dry-run]" in captured.out


def test_legacy_seed_module_propagates_canonical_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Avoid changing the canonical command's exit-code behavior."""

    def _canonical_main() -> None:
        raise RuntimeError("canonical seed failure")

    monkeypatch.setattr(seed, "canonical_main", _canonical_main)

    with pytest.raises(RuntimeError, match="canonical seed failure"):
        seed.main()
