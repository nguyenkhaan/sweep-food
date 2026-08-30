# Sweep Food Backend MVP — Execution Tracker

**Status:** Active  
**Started:** 2026-08-29  
**Source plan:** [`plan.md`](plan.md)  
**Task checklist:** [`todo.md`](todo.md)  
**Product requirements:** [`../src/backend/docs/prd.md`](../src/backend/docs/prd.md)  
**Database contract:** [`../src/backend/docs/DATABASE.txt`](../src/backend/docs/DATABASE.txt)

## Tracking Rules

- Update this tracker at the start and completion of every task in `todo.md`.
- A task can be marked `Done` only when every acceptance criterion and verification item has evidence recorded below.
- Do not begin a dependent task until its dependency and the required phase checkpoint are complete.
- Record a blocker immediately; do not work around a missing decision, failed verification, or unsafe database target.
- Keep secrets, Neon connection strings, OTPs, tokens, user identifiers, and raw provider payloads out of this file.
- Update both the task checkbox below and its status/evidence whenever a task changes state.
- Retry one failed command or task at most three times. After the third failed retry, stop that work, record concise error evidence, and ask the user for help; do not make a fourth retry without direction.

### Status Legend

| Status | Meaning |
|---|---|
| `Not started` | No implementation work has begun |
| `Ready` | Dependencies are satisfied; task may begin |
| `In progress` | Implementation or verification is actively underway |
| `Blocked` | Cannot safely continue; blocker and owner are recorded |
| `Review` | Implementation is complete; awaiting required human/phase review |
| `Done` | Acceptance criteria and verification evidence are complete |
| `Deferred` | Explicitly moved out of MVP by product approval |

## Current Focus

| Field | Value |
|---|---|
| Active phase | Phase 2 — Identity, Authentication, and User Preferences |
| Active task | Task 2.5 — Add profile, verified-email, and authorization policies (`Ready`) |
| Next task | Task 2.5 — Add profile, verified-email, and authorization policies |
| Next required action | Review and confirm the Task 2.5 API contract before implementation |
| Database target | Neon PostgreSQL; `alembic upgrade head` is user-verified; all future migration tests use a disposable branch/database |
| Current blocker | None |

## Phase Dashboard

| Phase | Objective | Status | Entry condition | Exit evidence |
|---|---|---|---|---|
| 0 | Data Contract and Database Redesign | `Done` | PRD approved | User approved `DATABASE.txt`; data model maps all MVP data/invariants |
| 1 | Runtime Foundation and Development Environment | `Done` | Phase 0 checkpoint complete | User-confirmed checkpoint: API, Alembic path, Redis/WireMock, test harness, and Phase 1 quality evidence are available |
| 2 | Identity, Authentication, and User Preferences | `In progress` | Phase 1 checkpoint complete | Phone/password sign-in; OTP-gated registration, recovery, sensitive changes; sessions, roles, and ownership checks pass |
| 3 | Catalog, Seed Pipeline, and Recipe Read APIs | `Not started` | Phase 0 and 1 checkpoints complete | Disposable Neon branch migrates/seeds repeatedly; read APIs work |
| 4 | Inventory, Shelf Life, and FEFO | `Not started` | Phase 3 checkpoint complete | Manual batches, ledger, expiry logic, and concurrency-safe FEFO work |
| 5 | Recommendations, Meal Selection, and Shopping Lists | `Not started` | Phases 3 and 4 checkpoints complete | Explainable inventory-sensitive recommendations and shopping list work |
| 6 | Cooking, Consumption, and Leftovers | `Not started` | Phases 4 and 5 checkpoints complete | Atomic/idempotent cooking and leftovers work |
| 7 | Notifications and Background Processing | `Not started` | Phase 2 and inventory prerequisites complete | Deduplicated expiry notification workflow works |
| 8 | Experimental OCR, ASR, and Barcode | `Not started` | Phase 1 checkpoint complete | Non-persisting extraction contracts pass WireMock tests |
| 9 | Hardening, Documentation, and Release Verification | `Not started` | Selected MVP phases complete | PRD acceptance, security, observability, and release checks pass |

## Task Checklist

### Phase 0 — Data Contract and Database Redesign

- [x] 0.1 Replace the conceptual database schema
- [x] 0.2 Add schema migration mapping and invariants
- [x] 0.3 Review data model against MVP flows
- [x] Phase 0 checkpoint

### Phase 1 — Runtime Foundation

- [x] 1.1 Establish backend package structure and typed configuration
- [x] 1.2 Add persistent service dependencies and local Docker environment
- [x] 1.3 Bootstrap SQLAlchemy, Alembic, and database conventions
- [x] 1.4 Establish quality, test, and WireMock fixture harness
- [x] Phase 1 checkpoint — user confirmed

### Phase 2 — Authentication and User Foundation

- [x] 2.1 Add user and session schema
- [x] 2.2 Implement OTP challenge, hashing, and rate-limit services (`In progress`)
- [x] 2.3 Add SMS/email delivery adapters and WireMock contracts
- [x] 2.4 Deliver registration, phone/password sign-in, and session APIs
- [ ] 2.5 Add profile, verified-email, and authorization policies
- [ ] Phase 2 checkpoint

### Phase 3 — Catalog and Seed Data

- [ ] 3.1 Add catalog and recipe migrations/models
- [ ] 3.2 Build the single idempotent seed entry point
- [ ] 3.3 Implement catalog and recipe read APIs
- [ ] 3.4 Curate and validate the initial seed dataset
- [ ] Phase 3 checkpoint

### Phase 4 — Inventory and FEFO

- [ ] 4.1 Add inventory batch and ledger persistence
- [ ] 4.2 Implement unit conversion and shelf-life/freshness services
- [ ] 4.3 Deliver manual batch CRUD APIs
- [ ] 4.4 Add inventory summaries and manual adjustments
- [ ] 4.5 Implement FEFO allocation and concurrency control
- [ ] Phase 4 checkpoint

### Phase 5 — Recommendations, Meal Plans, and Shopping

- [ ] 5.1 Add planning and recommendation persistence
- [ ] 5.2 Implement the rule-based recommendation provider
- [ ] 5.3 Expose and persist recommendations
- [ ] 5.4 Add meal-plan and favorites APIs
- [ ] 5.5 Implement shopping-list generation and editing
- [ ] Phase 5 checkpoint

### Phase 6 — Cooking and Leftovers

- [ ] 6.1 Add cooking persistence schema
- [ ] 6.2 Implement cooking preview
- [ ] 6.3 Implement atomic cooking completion
- [ ] 6.4 Add leftovers and cooking-history APIs
- [ ] Phase 6 checkpoint

### Phase 7 — Notifications and Background Jobs

- [ ] 7.1 Add device and notification persistence/API
- [ ] 7.2 Bootstrap worker/scheduler and FCM adapter
- [ ] 7.3 Implement expiry scan and deduplicated delivery workflow
- [ ] Phase 7 checkpoint

### Phase 8 — Experimental OCR, ASR, and Barcode

- [ ] 8.1 Create common extraction contract and media safety layer
- [ ] 8.2 Implement OCR label and invoice endpoints
- [ ] 8.3 Implement ASR/LiveKit endpoint
- [ ] 8.4 Implement barcode lookup endpoint
- [ ] Phase 8 checkpoint

### Phase 9 — Hardening and Release

- [ ] 9.1 Add observability and production-safe logging
- [ ] 9.2 Complete security and resilience review
- [ ] 9.3 Finalize OpenAPI and operations documentation
- [ ] 9.4 Run MVP acceptance and release gate
- [ ] Phase 9 checkpoint

## Task Status Summary

### Phase 0

| Task | Status | Dependencies | Evidence / next action |
|---|---|---|---|
| 0.1 Replace conceptual database schema | `Done` | None | User-approved schema has 22 enums and 24 tables, including password credentials and purpose-scoped OTP contracts; notes and delivery documents are synchronized |
| 0.2 Add schema migration mapping and invariants | `Done` | 0.1 | Mapping, migration order, invariants, and indexes are documented in `DATABASE_NOTES.md` |
| 0.3 Review data model against MVP flows | `Done` | 0.1, 0.2 | Every persisted and non-persisting PRD flow maps to the user-approved schema or Redis/transient processing |
| Phase 0 checkpoint | `Done` | 0.1–0.3 | User approved the database contract by authorizing Task 1.1 |

### Phase 1 Completed Work

| Task | Status | Dependencies | Evidence / next action |
|---|---|---|---|
| 1.1 Establish backend package structure and configuration | `Done` | Phase 0 checkpoint | `/api` application layout, environment helper, error envelope, and health module are implemented; Phase 1 checkpoint is user-confirmed. |
| 1.2 Add persistent service dependencies and local Docker environment | `Done` | 1.1 | Docker Compose defines API, Redis, and WireMock without local PostgreSQL; Compose syntax and WireMock startup were verified. |
| 1.3 Bootstrap SQLAlchemy, Alembic, and database conventions | `Done` | 1.1–1.2 | Async SQLAlchemy session manager, lifespan lifecycle, UUID/timestamp ORM base, Alembic environment, and bootstrap revision are implemented; user verified `alembic upgrade head`. |
| 1.4 Establish quality, test, and WireMock fixture harness | `Done` | 1.2–1.3 | `src/test` harness, health smoke tests, deterministic `/mock/sms` mapping, and test-folder quality checks passed. |

### Phase 2 Ready Work

| Task | Status | Dependencies | Evidence / next action |
|---|---|---|---|
| 2.1 Add user and session schema | `Done` | Phase 1 checkpoint | User-confirmed migration creates user/session tables and constraints; JWT access authentication and role demonstration endpoints are verified. |
| 2.2 Implement OTP challenge, hashing, and rate-limit services | `In progress` | Task 2.1 | Redis-backed OTP service, password/OTP helpers, configurable limits, and unit tests are implemented; Redis lifecycle requires user confirmation. |
| 2.3 Add SMS/email delivery adapters and WireMock contracts | `Done` | Task 2.2 | WireMock SMS and Mailpit-backed, template-based email delivery are verified locally; delivery remains provider-adapter based. |
| 2.4 Deliver registration, phone/password sign-in, and session APIs | `Done` | Tasks 2.1–2.3 | Database is at `20260830_0003 (head)`; auth/OTP/JWT/session tests pass, WireMock contract is verified against the healthy container, and logout revocation blocks refresh-token reuse. |

## Decision Baseline

| Decision | Status | Source |
|---|---|---|
| Single-user personal inventory | Accepted | PRD §2–3 |
| Batch-level stock and FEFO deduction | Accepted | PRD §4.2–4.3 |
| Neon PostgreSQL system of record | Accepted | [ADR-001](../src/backend/docs/decisions/ADR-001-neon-postgresql.md) |
| Redis for ephemeral OTP/rate-limit/lock/job state | Accepted | PRD §9, ADR-001 |
| Phone/password primary sign-in; OTP for registration, recovery, sensitive changes, and step-up authentication | Accepted | PRD §6; user-approved auth-contract update |
| Seed-only admin/catalog management | Accepted | PRD §3, §10 |
| Rule-based recommendation provider before XGBoost/LightGBM | Accepted | PRD §7.7 |
| OCR/ASR/barcode extraction does not persist in MVP | Accepted | PRD §7.14 |

## Execution Log

| Date | Phase / task | Status change | Evidence / note |
|---|---|---|---|
| 2026-08-29 | Project execution | `Not started` → `Active` | Tracker created. No schema, migration, or application-code implementation has been performed in this execution session. |
| 2026-08-29 | Phase 0 | `Not started` → `In progress` | Task 0.1 is ready; database schema redesign is the next planned work. |
| 2026-08-29 | Task 0.1 | `Ready` → `In progress` | Canonical MVP schema rewrite started from PRD §9. |
| 2026-08-29 | Task 0.1 | `In progress` → `Done` | Canonical schema now contains 25 required tables, 22 enums, explicit keys/checks/indexes, and Redis-only OTP/rate-limit/lock/job structures. |
| 2026-08-29 | Task 0.1 revision | `Done` → `In progress` | User requested `DATABASE.txt` contain enum/table syntax only; notes are being moved to a separate file. |
| 2026-08-29 | Task 0.1 revision | `In progress` → `Done` | `DATABASE.txt` now contains only enum/table syntax. Constraints, indexes, Redis state, relationships, and data rules moved to `DATABASE_NOTES.md`. |
| 2026-08-29 | Task 0.1 revision | `Done` → `In progress` | Product owner requested a substantially smaller MVP schema; nonessential tables and fields were being removed. |
| 2026-08-30 | Task 0.1 revision | `In progress` → `In progress` | Product owner clarified that the smaller schema was reference material only. Full PRD entity coverage is being restored. |
| 2026-08-30 | Task 0.1 revision | `In progress` → `Done` | Restored 22 enums and 25 tables for all persistent PRD flows; confirmed table-only syntax, notes coverage, and clean whitespace validation. |
| 2026-08-30 | Task 0.1 revision | `Done` → `In progress` | User edited `DATABASE.txt` directly and designated it as the source of truth. Documentation and dangling definitions are being reconciled. |
| 2026-08-30 | Task 0.1 revision | `In progress` → `Done` | Removed the orphaned recommendation-event enum, synchronized documentation, and confirmed all documented table references resolve. |
| 2026-08-30 | Tasks 0.2–0.3 | `In progress` → `Done` | Completed migration mapping/invariant review and verified every PRD flow against the approved schema. |
| 2026-08-30 | Phase 0 checkpoint | `Review` → `Done` | User authorized Task 1.1 after reviewing the data contract. |
| 2026-08-30 | Task 1.1 | `Ready` → `In progress` | Replacing the FastAPI stub with the approved `/api` module architecture, typed settings, global exception handler, and health endpoints. |
| 2026-08-30 | Task 1.1 | `In progress` | User replaced typed Pydantic settings with `python-dotenv` and `core/setting.py`; `main.py` remains the entry point. Health smoke validation remains paused under the retry-limit rule. |
| 2026-08-30 | Task 1.2 | `Ready` → `Review` | Created backend-local Dockerfile/Compose assets; YAML and `docker compose config --quiet` passed without starting containers. |
| 2026-08-30 | Tasks 1.3–1.4 | `In progress` → `Done` | Added async SQLAlchemy/Alembic bootstrap, `src/test` pytest harness, and deterministic WireMock `/mock/sms` contract. User verified `alembic upgrade head`; test harness passed 4/4 tests. |
| 2026-08-30 | Phase 1 checkpoint | `In progress` → `Done` | User confirmed the Phase 1 checkpoint after runtime, migration, Docker/WireMock, and test-harness work. |
| 2026-08-30 | Authentication contract | `Accepted` | User approved phone/password sign-in. OTP now verifies registration, password recovery/change, phone/email changes, and optional step-up authentication; PRD/schema/plan/checklist were updated. |
| 2026-08-30 | Task 2.1 | `Ready` → `In progress` | Declared 24 table models in individual `*_model.py` files, registered shared enums in `enum_model.py`, and verified model metadata/foreign keys without circular imports. |
| 2026-08-30 | Task 2.1 | `In progress` → `Done` | User confirmed `alembic upgrade head` succeeds for the focused user/session migration; JWT service, authentication/role dependencies, and protected demonstration endpoints passed verification. |
| 2026-08-30 | Task 2.2 | `Ready` → `In progress` | Implemented Redis lifecycle, Argon2id/OTP helpers, and Redis-backed OTP challenge/grant/rate-limit service with isolated unit tests. |
| 2026-08-30 | Task 2.3 | `Ready` → `In progress` | Added provider-neutral OTP delivery contract, WireMock SMS adapter/fixtures, and non-delivering local email adapter; WireMock accepted contract passed with `DEFAULT_OTP`. |
| 2026-08-30 | Task 2.3 | `In progress` → `Done` | User accepted Task 2.3 with the local/mock provider scope and fixed `DEFAULT_OTP`; eSMS live integration remains a future provider configuration task. |
| 2026-08-30 | Task 2.3 extension | `Done` → `Done` | Replaced the non-delivering email adapter with Mailpit SMTP delivery, five purpose-specific HTML templates, Docker networking, and local SMTP verification. |
| 2026-08-30 | Task 2.3 extension | `Done` → `Done` | Converted all email templates to English, renamed the shared layout to `base_email.html`, and added the Mailpit test-email endpoint. |
| 2026-08-30 | Task 2.4 | `Ready` → `In progress` | Implemented the approved internal-OTP auth contract: unverified registration, registration verification, password OTP flows, sessions, and database account-status checks. |
| 2026-08-30 | Task 2.4 revision | `In progress` → `In progress` | Removed client IP propagation from AuthService and added unverified-registration OTP resend; replacing a challenge invalidates its previous Redis key. |
| 2026-08-30 | Task 2.4 migration fix | `In progress` → `In progress` | Corrected the `UNVERIFIED` PostgreSQL enum label to match SQLAlchemy's persisted enum-name convention; a follow-up migration is required for databases already upgraded. |
| 2026-08-30 | Task 2.4 OTP contract correction | `In progress` → `In progress` | Removed public/internal challenge IDs from auth OTP flows. Issue/resend responses now return the generated OTP; Redis stores one hashed OTP per channel/purpose/destination scope, resend overwrites the old code, and local/test verification additionally accepts `123456`. |
| 2026-08-30 | Task 2.4 JWT contract revision | `In progress` → `In progress` | Registration verification now returns plain text only. Login issues access/refresh JWTs, purpose claims and separate secrets are enforced, refresh can issue a new access JWT, and `device_label` was removed from login. |
| 2026-08-30 | Task 2.4 OpenAPI security revision | `In progress` → `In progress` | Bearer security is now inferred recursively from `require_authentication` and `require_role(...)` dependencies, so protected routes receive Swagger lock icons without per-route `openapi_extra` declarations. |
| 2026-08-30 | Task 2.4 token route revision | `In progress` → `In progress` | Removed the access-token-to-refresh-token route by user decision; login remains the refresh-token issuer and `/auth/token/refresh` exchanges a valid refresh JWT for a new access JWT. |
| 2026-08-30 | Task 2.4 | `In progress` → `Done` | Removed obsolete refresh-issuance service/test code, confirmed database revision `20260830_0003 (head)`, passed the live WireMock contract, and verified logout revokes the matching session and blocks refresh reuse. |

## Verification Evidence

### Task 0.1 — Replace the conceptual database schema

- Completed: 2026-08-29
- Changed files: `src/backend/docs/DATABASE.txt`, `src/backend/docs/DATABASE_NOTES.md`, `src/backend/COOKBOOK.md`, `src/backend/CHANGELOG.md`, `tasks/todo.md`, `tasks/tracking.md`
- Acceptance evidence: all identity, catalog, recipe, batch inventory/ledger, recommendation, meal-plan, cooking, shopping, device, and notification entities are explicitly modeled. The legacy `user_ingredient` shape and misspelled enum/field names are absent.
- File layout evidence: `DATABASE.txt` contains only 22 enum blocks, 24 table blocks, fields, and relationship comments in the requested syntax. `DATABASE_NOTES.md` contains constraints, indexes, Redis-only state, relationships, and data rules.
- Storage coverage: OTP challenges and rate-limit/lock/job coordination are documented as Redis-only; OCR/ASR/barcode explicitly have no persistent MVP tables.
- Critical-flow review: FEFO, cooking/ledger, session hashing, and notification deduplication are retained as explicit notes outside the syntax-only schema file.
- Verification commands: required-table coverage script — 24/24 present; table-syntax-only scan — passed; trailing-whitespace scan — passed.
- Manual verification: traced every PRD §9 entity and the FEFO, OTP/session, cooking, notification, seed, and non-persisting extraction scenarios to documented storage.
- Follow-up: Task 0.2 must add the legacy schema mapping and consolidated cross-table invariant/index reference before Phase 0 review.
- Revision note: The user clarified that their smaller schema was illustrative only. The final contract retains auth sessions, catalog categories/aliases/shelf-life rules, batch ledger, recommendation history, normalized plan/cooking/shopping data, devices, and notifications.
- Final verification: `rg -c '^enum ' src/backend/docs/DATABASE.txt` — 22; `rg -c '^table ' src/backend/docs/DATABASE.txt` — 24; documented-reference scan — every referenced table exists; `git diff --check` — passed.
- Latest revision: `DATABASE.txt` was accepted as the source of truth. Per-user timezone, redundant dimension/seed/version metadata, and recommendation-event persistence are intentionally absent; PRD, plan, checklist, cookbook, and database notes match this contract.

### Task 0.2 — Add schema migration mapping and invariants

- Completed: 2026-08-30
- Changed files: `src/backend/docs/DATABASE_NOTES.md`, `tasks/todo.md`, `tasks/tracking.md`
- Acceptance evidence: the mapping names every original conceptual table and its approved destination; migration order resolves the nullable cooking-leftover circular reference; ownership, quantity, expiry, FEFO, ledger, idempotency, uniqueness, and index requirements are explicit.
- Verification commands: documented-reference scan — every `// table.id` reference resolves; `git diff --check` — passed.
- Manual verification: reviewed all 22 enums and 24 tables in `DATABASE.txt` as the source of truth.

### Task 0.3 — Review data model against MVP flows

- Completed: 2026-08-30
- Changed files: `src/backend/docs/DATABASE_NOTES.md`, `tasks/tracking.md`
- Acceptance evidence: the MVP flow review maps authentication, catalog, expiration, inventory/FEFO, recipes, recommendation, planning, shopping, cooking/leftovers, favorites, notifications, and non-persisting extraction to approved storage.
- Verification commands: obsolete-schema scan — no references to removed timezone, dimension, seed/version, or recommendation-event persistence; `git diff --check` — passed.
- Manual verification: verified that OCR/ASR/invoice/barcode have no persistence path and that all retained relationship comments reference existing tables.

### Task 1.3 — Bootstrap SQLAlchemy, Alembic, and database conventions

- Completed: 2026-08-30
- Changed files: `src/backend/src/db.py`, `src/backend/src/app.py`, `src/backend/src/core/setting.py`, `src/backend/src/model/base.py`, `src/backend/alembic/*`, `src/backend/alembic.ini`
- Acceptance evidence: async `db_session` initializes and disposes with FastAPI lifespan; `DATABASE_URL` is normalized for `asyncpg`; Alembic has an asynchronous environment and revision-controlled bootstrap migration.
- Verification commands: application compile/import, URL-normalization check, and `uv run alembic history` — passed; `uv run alembic upgrade head` — user verified.
- Manual verification: database URLs retain secrets outside source control; example configuration uses the `postgresql+asyncpg` scheme.

### Task 1.4 — Establish quality, test, and WireMock fixture harness

- Completed: 2026-08-30
- Changed files: `src/backend/src/test/*`, `src/backend/pyproject.toml`, `src/backend/wiremock/mappings/mock-sms.json`
- Acceptance evidence: pytest discovers `src/test`; reusable API, safe test-database, Redis, and WireMock fixtures exist; health liveness/error/text smoke tests and deterministic `/mock/sms` contract test exist.
- Verification commands: `uv run pytest` — 4 passed; `uv run ruff check src/test`, `uv run ruff format --check src/test`, `uv run mypy --strict src/test` — passed; `uv run pylint src/test` — 10.00/10.
- Manual verification: WireMock was started with Docker Compose and the `/mock/sms` contract test passed against the running container.

### Task 2.1 — Add user and session schema

- Completed: 2026-08-30
- Changed files: `src/backend/src/model/user_model.py`, `src/backend/src/model/auth_session_model.py`, `src/backend/alembic/versions/6470957327a3_create_mvp_models.py`, `src/backend/src/service/jwt_service.py`, `src/backend/src/middleware/*`, `src/backend/src/module/health/health_router.py`, `src/backend/src/test/test_auth_middleware.py`, `src/backend/src/test/test_health.py`
- Acceptance evidence: focused migration creates `users` and `auth_sessions`, `user_role`/`account_status` enums, verified-phone constraint, and refresh-session indexes. Custom JWT parsing exposes only `user_id` and `roles`; `require_authentication` and `require_role` guard the protected demonstration routes.
- Verification commands: ruff and mypy strict — passed; Pylint — 10.00/10; targeted JWT/health suite — 14 passed; Alembic offline upgrade/downgrade SQL generation — passed.
- Manual verification: user confirmed `uv run alembic upgrade head` succeeds. `/api/health/test-login` accepts a valid access JWT and `/api/health/test-role` rejects a non-admin JWT.
- Follow-up / known limitation: OTP, password hashing, registration, sign-in, refresh, and session-revocation APIs are intentionally deferred to Tasks 2.2–2.5.

### Task 2.3 — Add SMS/email delivery adapters and WireMock contracts

- Completed: 2026-08-30
- Changed files: `src/backend/src/service/otp_delivery_service.py`, `src/backend/src/service/sms_service.py`, `src/backend/src/service/email_service.py`, `src/backend/src/template/*.html`, `src/backend/src/core/setting.py`, `src/backend/.env.example`, `src/backend/docker-compose.yaml`, `src/backend/wiremock/mappings/mock-sms*.json`, `src/backend/src/test/test_otp_delivery_service.py`, `src/backend/src/test/test_email_service.py`, `src/backend/src/test/test_wiremock_contract.py`
- Acceptance evidence: one provider-neutral `send_otp` contract supports WireMock SMS and Mailpit email delivery. `EmailService.send_email` renders purpose-specific, autoescaped HTML templates for verified-email, email-change, password-reset, password-change, and step-up flows; WireMock maps accepted, rejected, timeout, and malformed SMS responses to stable domain errors.
- Verification commands: `docker compose config --quiet`; focused email and OTP-adapter tests — 13 passed; ruff and mypy — passed; Pylint — 10.00/10.
- Manual verification: restarted WireMock and verified its accepted SMS contract. Mailpit SMTP is healthy and accepted a rendered local verification email using the configured SMTP host and port.
- Latest extension: `POST /api/health/test-email` uses `HealthService` and `EmailService` to submit `base_email.html` to the Mailpit-only test inbox. English templates and the isolated endpoint test are verified.
- Follow-up / known limitation: eSMS implementation is intentionally deferred until its endpoint, request schema, template, and credential contract are supplied.

## Verification Evidence Template

Add one entry for each completed task:

```markdown
### Task X.Y — [name]

- Completed: YYYY-MM-DD
- Changed files: `path/to/file`
- Acceptance evidence: [concise evidence for every criterion]
- Verification commands: `command` — pass/fail result
- Manual verification: [scenario and result]
- Follow-up / known limitation: [none or explicit item]
```

## Blocker Log

No active blockers.

When blocked, add:

| Opened | Task | Blocker | Needed decision/action | Owner | Status |
|---|---|---|---|---|---|
| YYYY-MM-DD | X.Y | Description | Specific next action | User/engineering/provider | Open |
