# FreshCheck knowledge base

This directory contains the reviewed FreshCheck source data and the tooling that produces its PostgreSQL-ready release artifact.

## Development setup

Use `uv` to create and synchronize the isolated environment:

```bash
uv sync --all-groups
```

## Build and validate a release

Commit the reviewed source data before building a release. The builder records the current Git commit as `source_commit` in the artifact.

```bash
uv run python scripts/build_kb.py
uv run pytest -q tests
uv run ruff check scripts/build_kb.py tests/test_kb_invariants.py
uv run ruff format --check scripts/build_kb.py tests/test_kb_invariants.py
uv run mypy --strict scripts/build_kb.py
```

The build creates `build/freshcheck_kb.json`. This file is a release artifact rather than a runtime dependency of the backend; Task 3 syncs it into PostgreSQL.

## Release metadata

Record the following values printed by the builder in the release note before syncing:

- `kb_version`
- `source_commit`
- `checksum`
- counts of archetypes, ingredients, claims, and sources

`checksum` is a SHA-256 digest of canonical KB content. It deliberately excludes `generated_at` and `checksum`, so rebuilding identical reviewed data produces the same integrity value.

Do not edit `build/freshcheck_kb.json` by hand. Update reviewed YAML source data, build a new artifact, and validate it again.
