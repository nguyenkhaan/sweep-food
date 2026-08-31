"""Deprecated compatibility command for the canonical catalog seed script.

Run ``uv run python scripts/seed.py [--dry-run]`` instead.
"""

from scripts.seed import main as canonical_main


def main() -> None:
    """Delegate the legacy module command to the canonical seed entry point."""
    print(
        "Deprecated: use `uv run python scripts/seed.py [--dry-run]` instead.",
    )
    canonical_main()


if __name__ == "__main__":
    main()
