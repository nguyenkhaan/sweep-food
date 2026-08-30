# Changelog

All notable backend changes are recorded in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Backend Product Requirements Document defining the approved Sweep Food MVP scope.
- Phase-based implementation plan and task checklist for the backend MVP.
- Neon PostgreSQL as the managed system of record for the backend.
- ADR-001 documenting the Neon PostgreSQL decision and safe migration/test workflow.
- Agent-facing context and operating guidance in `COOKBOOK.md`.
- Async SQLAlchemy database-session lifecycle and Alembic bootstrap revision for Neon PostgreSQL migrations.
- Pytest smoke-test harness under `src/test` and a deterministic WireMock provider fixture.

### Changed

- Backend database planning now targets Neon PostgreSQL instead of a local PostgreSQL container.
- Replaced the early conceptual database notes with the canonical MVP schema contract covering identity, catalog, batch inventory, FEFO audit data, recommendations, planning, cooking, shopping, and notifications.
- Split database documentation into table syntax (`DATABASE.txt`) and operational/design notes (`DATABASE_NOTES.md`) for faster schema review.
- Restored complete PRD data coverage after clarifying that the smaller user-provided schema was a reference, not a request to remove persistent MVP flows.
- Simplified the database contract from the user-approved `DATABASE.txt`: removed per-user timezone and redundant dimension/seed/version metadata, removed recommendation-event persistence, and aligned all documents to the remaining schema.

### Security

- Database credentials are supplied only through the ignored `.env` file; connection strings must never be committed or copied into logs, tests, fixtures, or documentation.

## [0.1.0] - 2026-08-29

### Added

- Initial FastAPI backend scaffold with a basic health endpoint.
- Initial backend Python project configuration.
- Early product requirements and conceptual database notes.

## Changelog Rules

- Add user-visible, API-contract, schema, security, operational, or dependency changes under `Unreleased` in the same change set.
- Move `Unreleased` entries into a dated semantic version only when that version is released.
- Write entries in terms of observable behavior and migration impact, not internal implementation trivia.
- Call out breaking API, database, authentication, or environment changes explicitly under `Changed`, `Removed`, or `Security`.
- Never include credentials, phone numbers, email addresses, OTPs, tokens, or private provider configuration.
