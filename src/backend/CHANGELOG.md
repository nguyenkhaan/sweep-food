# Changelog

All notable backend changes are recorded in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Extraction response `fields` (`POST /api/extractions/ocr/label`, `ocr/invoice`, `asr`, `text`) and invoice `line_items[]` now include `category: string | null` containing the Vietnamese category name from `ingredient_categories.name` when matched to a catalog master ingredient, and `null` otherwise (partially reversing the earlier removal of category from extraction responses to enable app auto-fill).
- FreshCheck previews and assessments accept `other_answers` for free-text sensory
  observations. A single bounded call through the shared OpenAI client checks
  relevance and estimates each requested axis against that axis's server-owned
  scored anchors; standard selectable answers do not call the LLM.
- FreshCheck results expose `other_answer_scores`. Unrelated or unclear text returns
  HTTP 422 with a stable code and actionable per-axis feedback; invalid provider
  output fails closed. Assessments retain descriptions, inferred scores and the
  configured model in their immutable outcome, and idempotent replay skips inference.
- Recipe media and cooking steps backfill for the catalog importer, populating 100% validated media URLs and structured instruction steps via relaxed JSON-LD scraping, thumbnail-filtering heuristics, curated step overrides, and sweep-food-AI dataset commits.
- Catalog and recipe schema hardening migration with lossless Numeric conversions,
  case-insensitive catalog uniqueness, lookup indexes, and shelf-life validation.
- Backend Product Requirements Document defining the approved Sweep Food MVP scope.
- Phase-based implementation plan and task checklist for the backend MVP.
- Neon PostgreSQL as the managed system of record for the backend.
- ADR-001 documenting the Neon PostgreSQL decision and safe migration/test workflow.
- Agent-facing context and operating guidance in `COOKBOOK.md`.
- Async SQLAlchemy database-session lifecycle and Alembic bootstrap revision for Neon PostgreSQL migrations.
- Pytest smoke-test harness under `src/test` and a deterministic WireMock provider fixture.
- SQLAlchemy database models for every approved MVP table, with a common enum module and time-ordered UUIDv7 primary-key generation.
- Custom JWT service plus authentication and role-authorization dependencies with OpenAPI Bearer-token support and injected access-token secret keys.
- Redis lifecycle management plus backend-owned OTP challenge, verification-grant, rate-limit, and Argon2id helper services.
- Provider-neutral OTP delivery contract, deterministic WireMock SMS adapter, and non-delivering local email adapter.
- Backend-hosted AI under `AI/`: LightGBM recommendation engine over a catalog rebuilt in Postgres from the bundled data (`python -m AI.catalog.importer`), OpenAI-based OCR and LLM text parsing, Groq Whisper ASR, and a four-tier pantry parser. Adds `recipes.ai_features`, `recipe_ingredients.ai_attributes`, and `master_ingredients.source_code` (migration `e2b4f68a10cd`).
- `GET /api/health/ai` now reports the in-process catalog revision, ranker, and provider configuration.
- Pre-OCR image guard (`OPENAI_OCR_GUARD_MODEL`, default `gpt-4o-mini`): images that are neither a food label/packaging nor an invoice are rejected with HTTP 422 before the OCR model is called.

### Fixed

- FreshCheck hard-stop spoilage signals now block estimates even when a printed
  manufacturer expiry exists; the printed date and batch quantity remain unchanged.
  The inference rule version is now `freshcheck-infer-v1.1`.
- Alembic revision template now includes dialect-specific imports emitted during autogeneration, allowing PostgreSQL `JSONB` migrations to run.
- Pantry matcher no longer maps labels onto the wrong ingredient: aliases and the query are scored together (IDF-weighted token F1 over ordered tokens, graded tone / d-đ agreement, head-noun position, recipe popularity as the tie-break) instead of sequential tiers, brand and preparation noise (`C.P`, `làm sạch`, `nguyên con`) is stripped, regional synonyms no longer override real catalog names, and ambiguous or unknown labels return no match with a `match_confidence`.
- OpenAI OCR/guard HTTP client is no longer closed after every call, which broke concurrent extraction requests on the shared service.
- `PATCH /api/inventory/batches/{id}`, `POST /api/inventory/batches/{id}/move` and `PATCH /api/favorite-menus/{id}` no longer return 500: server-side `updated_at` is now fetched eagerly (`eager_defaults`) instead of lazily loaded outside the async context.
- `DELETE /api/shopping-lists/{id}/items/{item_id}` no longer always returns 409: an empty receipt body is stored as SQL `NULL` (`JSONB(none_as_null=True)`) so it satisfies the 204-with-no-body check constraint.

### Changed
- `POST /api/inventory/batches` called with `custom_name` now resolves the name through the deterministic smart parser. If recognized, the batch is stored under the resolved master ingredient (`master_ingredient_id` set, `custom_name = null`); if unrecognized, the request is rejected with HTTP 422 and detail `INGREDIENT_NOT_SUPPORTED`. Requests with `master_ingredient_id` and internal batch staging via `stage_batch` remain unaffected.

- **Breaking authentication change:** registration now requires phone OTP verification followed by password creation; sign-in now uses phone number and password. OTP is reserved for registration, password recovery/change, identity changes, and step-up authentication.
- **Breaking extraction contract change:** `POST /api/extractions/ocr/label|ocr/invoice|asr` now return only `ingredient_name`, `raw_name`, `master_ingredient_id`, `quantity`, `unit`, `packaged_at` and `expires_at` (invoice lines: `name`, `raw_name`, `master_ingredient_id`, `quantity`, `unit`, `unit_price`, `total_price`). `nutrition`, `freshness_guide`, `is_staple`, `category`, `master_ingredient_code`, `quantity_source`, `price`, `currency` and `barcode` were removed. `master_ingredient_id` is resolved from the AI catalog code through `master_ingredients.source_code` and is `null` when no master ingredient matches.
- **Inventory batches are no longer estimated at creation:** `POST /api/inventory/batches` without `expires_at` now stores `expires_at = null` and `expiration_source = UNKNOWN` instead of applying a seeded shelf-life rule. A printed `expires_at` is still stored as `MANUFACTURER`; FreshCheck assessments record `ESTIMATED` expiries. Moving a batch between storage modes still recalculates `ESTIMATED`/`UNKNOWN` expiries from shelf-life rules.
- `POST /api/extractions/text` runs typed ingredient text through the smart parser (dictionary and regex tiers) and returns the same envelope as label/ASR extraction. The smart parser's text fallback now propagates `quantity_source`, so a quantity stated in the text is reported as extracted.
- `POST /api/freshness/previews` estimates an expiry for an unsaved ingredient from sensory answers without persisting anything.
- Backend database planning now targets Neon PostgreSQL instead of a local PostgreSQL container.
- Replaced the early conceptual database notes with the canonical MVP schema contract covering identity, catalog, batch inventory, FEFO audit data, recommendations, planning, cooking, shopping, and notifications.
- Split database documentation into table syntax (`DATABASE.txt`) and operational/design notes (`DATABASE_NOTES.md`) for faster schema review.
- Restored complete PRD data coverage after clarifying that the smaller user-provided schema was a reference, not a request to remove persistent MVP flows.
- Simplified the database contract from the user-approved `DATABASE.txt`: removed per-user timezone and redundant dimension/seed/version metadata, removed recommendation-event persistence, and aligned all documents to the remaining schema.
- **Breaking:** `POST /api/recommendations` no longer accepts `max_cooking_time_min`. AI endpoints return HTTP 503 until the catalog has been imported.
- The backend no longer proxies to a separate SweepFood AI service; `AI_BASE_URL` and `AI_*_TIMEOUT_SECONDS` are removed. OCR now uses OpenAI instead of Groq Vision.

### Removed

- Obsolete scaffold/phase prerequisites, speculative environment/provider setup,
  and mock recommendation guidance from backend operating documentation.
- Superseded Phase 5 implementation checklist, conceptual database migration
  mapping, and unrelated PyTorch/GPU instructions from the backend protocol.

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
