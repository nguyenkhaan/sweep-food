# Sweep Food Backend MVP — Execution Checklist

**Use this file after review of `tasks/plan.md`.** Tasks are ordered by dependency and intentionally small enough to implement and verify in a focused session. No task is complete without its verification evidence.

## Phase 0 — Database Redesign

### Task 0.1: Replace the conceptual database schema

**Description:** Rewrite `src/backend/docs/DATABASE.txt` as the canonical MVP data model from the PRD. Correct the existing spelling/enum issues and define all tables, fields, relationships, nullability, constraints, and indexes.

**Acceptance criteria:**

- [x] Documents users, sessions, catalog, recipes, inventory batches/ledger, recommendations, meal plans, cooking, shopping, devices, and notifications.
- [x] Replaces `user_ingredient` with batch-level inventory and an immutable quantity ledger.
- [x] Defines enum values and all primary/foreign/unique keys required by the PRD.

**Verification:**

- [x] Trace every PRD data entity to a table or explicitly documented Redis-only structure.
- [x] Review FEFO, OTP/session, cooking, and notification scenarios against the schema.

**Dependencies:** None.  
**Files likely touched:** `src/backend/docs/DATABASE.txt`  
**Estimated scope:** M

### Task 0.2: Add schema migration mapping and invariants

**Description:** Add the migration/reference section to `DATABASE_NOTES.md`, mapping each old conceptual table to its MVP successor and stating non-negotiable data invariants.

**Acceptance criteria:**

- [x] Old tables are marked retained, renamed, split, or removed with reason.
- [x] Invariants include ownership, non-negative batch quantity, manufacturer-expiry precedence, and ledger immutability.
- [x] Indexes required by user/batch/expiry and FEFO queries are listed.

**Verification:**

- [x] Reviewer can determine a migration order without guessing.
- [x] No existing ambiguous field name remains in the canonical schema.

**Dependencies:** Task 0.1.  
**Files likely touched:** `src/backend/docs/DATABASE_NOTES.md`
**Estimated scope:** S

### Checkpoint: Phase 0

- [x] `DATABASE.txt` has human approval.
- [x] All PRD data needs map to documented storage.
- [x] No application code or Alembic migration has been started against an unapproved schema.

## Phase 1 — Runtime Foundation

### Task 1.1: Establish backend package structure and typed configuration

**Description:** Replace the minimal application layout with versioned API modules, configuration, dependency wiring, and a shared error envelope while preserving the ability to run the server.

**Acceptance criteria:**

- [ ] API base path is `/api`; health endpoints follow the approved `/health` module contract.
- [ ] Environment variables load through the shared `core/setting.py` helper.
- [ ] Error responses contain `status_code`, `detail`, and `path`.

**Verification:**

- [ ] API starts with local configuration and OpenAPI loads.
- [ ] Ruff, mypy strict, and pylint pass for new Python modules.

**Dependencies:** Phase 0 checkpoint.  
**Files likely touched:** `src/backend/src/app.py`, `src/backend/src/core/*`, `src/backend/pyproject.toml`, tests  
**Estimated scope:** M

### Task 1.2: Add persistent service dependencies and local Docker environment

**Description:** Define Docker Compose services and environment examples for Redis, API, and WireMock; document Neon connection configuration and a safe disposable Neon development/test-branch workflow.

**Acceptance criteria:**

- [x] Redis and WireMock have health checks and isolated named volumes/networks; Neon is reached only through an environment-provided connection string.
- [x] No secret is committed; `.env.example` contains only safe placeholders.
- [x] API configuration can address services by Compose DNS name.

**Verification:**

- [ ] User manual test: `docker compose up` reaches healthy local dependency states without creating a local PostgreSQL database.
- [x] `docker compose config --quiet` validates the Compose syntax without starting containers.

**Dependencies:** Task 1.1.  
**Files likely touched:** `src/backend/Dockerfile`, `src/backend/docker-compose.yaml`, `src/backend/.dockerignore`, `src/backend/.env.example`, `src/backend/docs/*`
**Estimated scope:** M

### Task 1.3: Bootstrap SQLAlchemy, Alembic, and database conventions

**Description:** Add database engine/session lifecycle, base model conventions, migration tooling, and the first empty/revision-controlled migration workflow.

**Acceptance criteria:**

- [ ] Database URLs/configuration support local, test, and deployment environments.
- [ ] Alembic upgrade/downgrade works against a disposable Neon development/test branch.
- [ ] All future model timestamps/UUID conventions are centrally defined.

**Verification:**

- [ ] Migration command succeeds from a clean database.
- [ ] Test fixture creates and rolls back an isolated database transaction.

**Dependencies:** Tasks 1.1–1.2.  
**Files likely touched:** `src/backend/alembic/*`, `src/backend/src/core/database.py`, `src/backend/pyproject.toml`, tests  
**Estimated scope:** M

### Task 1.4: Establish quality, test, and WireMock fixture harness

**Description:** Add pytest configuration, reusable API/database/Redis fixtures, and the WireMock mapping structure used by all provider contract tests.

**Acceptance criteria:**

- [ ] One command runs unit/integration tests locally.
- [ ] WireMock mappings can be loaded through Docker Compose.
- [ ] CI-friendly quality commands match `src/backend/AGENT.md` requirements.

**Verification:**

- [ ] Smoke tests cover `/api/health/liveness`, `/api/health/error`, and `/api/health/text`.
- [ ] A fixture produces a deterministic provider response through WireMock.

**Dependencies:** Tasks 1.2–1.3.  
**Files likely touched:** `src/backend/tests/*`, `src/backend/wiremock/*`, `src/backend/pyproject.toml`  
**Estimated scope:** M

### Checkpoint: Phase 1

- [ ] Dependencies start from a clean clone.
- [ ] The API, migration command, type checks, lint checks, and smoke tests pass.
- [ ] WireMock can simulate one external provider call.

## Phase 2 — Authentication and User Foundation

### Task 2.1: Add user and session schema

**Description:** Implement migrations/models for users, password credentials, account status/roles, profile preferences, and refresh-token sessions exactly as approved in `DATABASE.txt`.

**Acceptance criteria:**

- [ ] Phone is unique and normalized as E.164; email is nullable and unique when present.
- [ ] Every user has an Argon2id `password_hash`; no plaintext password is persisted, logged, or returned.
- [ ] User role/status and verified-at fields are represented.
- [ ] Refresh tokens are stored as hashes, not clear values.

**Verification:**

- [ ] Migration upgrade/downgrade test passes.
- [ ] Constraint tests reject duplicate phone/email, absent password hashes, and invalid status combinations.

**Dependencies:** Phase 1 checkpoint.  
**Files likely touched:** migrations, `src/backend/src/model/*`, `src/backend/src/module/auth/*`, tests  
**Estimated scope:** M

### Task 2.2: Implement OTP challenge, hashing, and rate-limit services

**Description:** Build the backend-owned OTP domain service using Redis TTL state, purpose separation, secure generation, hash verification, short-lived single-use verification grants, attempt limits, and configurable resend limits.

**Acceptance criteria:**

- [ ] OTP is six numeric digits in non-test environments and is never persisted/logged in clear text.
- [ ] Challenges expire, are single-use, and are scoped to destination plus purpose.
- [ ] A successful verification returns only a short-lived grant bound to the matching purpose/destination; it does not create a session.
- [ ] Request/attempt rate limits return stable domain errors.

**Verification:**

- [ ] Tests cover expiry, replacement, invalid code, purpose mismatch, and cooldown behavior.
- [ ] Constant fixed OTP behavior is enabled only in the local/CI adapter/configuration.

**Dependencies:** Task 2.1.  
**Files likely touched:** `src/backend/src/module/auth/*`, `src/backend/src/service/*`, tests  
**Estimated scope:** M

### Task 2.3: Add SMS/email delivery adapters and WireMock contracts

**Description:** Create provider interfaces and adapters for mock SMS, eSMS sandbox/production configuration, and a non-delivering local email adapter. Do not bind OTP validation to a provider.

**Acceptance criteria:**

- [ ] The same internal send contract works for phone and email channels.
- [ ] WireMock covers accepted, rejected, timeout, and malformed provider responses.
- [ ] Provider secrets/template IDs come only from settings.

**Verification:**

- [ ] Contract tests run entirely against WireMock.
- [ ] Provider failure does not consume or verify an OTP challenge.

**Dependencies:** Task 2.2, Task 1.4.  
**Files likely touched:** `src/backend/src/service/*`, `src/backend/src/module/auth/*`, `src/backend/wiremock/*`, tests  
**Estimated scope:** M

### Task 2.4: Deliver registration, phone/password sign-in, and session APIs

**Description:** Implement `UNVERIFIED` registration with internally issued SMS OTP, registration verification, phone/password login, internally issued password OTPs, password verification/change, access/refresh token, logout, and session management endpoints with consistent responses and ownership middleware. Generic OTP request/verify endpoints are not exposed.

**Acceptance criteria:**

- [ ] A verified registration grant plus valid password creates/activates a user; OTP verification alone never creates a session.
- [ ] Phone/password login returns access/refresh session data without disclosing whether an account existed or password verification failed.
- [ ] Password reset/change consumes a matching OTP grant and revokes affected refresh-token sessions.
- [ ] Refresh rotation and revocation invalidate the correct session family.

**Verification:**

- [ ] API tests register locally with `123456`, sign in with phone/password, reset/change password through OTP verification, refresh, logout, and fail after revocation.
- [ ] A banned account cannot use protected endpoints.

**Dependencies:** Tasks 2.1–2.3.  
**Files likely touched:** `src/backend/src/module/auth/*`, `src/backend/src/middleware/*`, tests  
**Estimated scope:** M

### Task 2.5: Add profile, verified-email, and authorization policies

**Description:** Implement profile/preferences APIs, verified-email recovery, verified phone/email change, and reusable user ownership/admin role policy dependencies.

**Acceptance criteria:**

- [ ] An unverified email cannot be used for password recovery or sensitive identity changes.
- [ ] Email verification requires an OTP with the correct purpose.
- [ ] Protected resource queries enforce current user ownership.

**Verification:**

- [ ] Cross-user access tests return a non-disclosing error.
- [ ] Profile/session/email API tests pass with both SMS and verified-email OTP channels.

**Dependencies:** Task 2.4.  
**Files likely touched:** `src/backend/src/module/users/*`, `src/backend/src/module/auth/*`, tests  
**Estimated scope:** M

### Checkpoint: Phase 2

- [ ] OTP-gated registration, phone/password sign-in, password recovery, and verified phone/email change flows work end-to-end locally.
- [ ] Session rotation/revocation, rate limits, account status, and ownership checks pass tests.
- [ ] No OTP, token, or provider secret appears in captured logs.

## Phase 3 — Catalog and Seed Data

### Task 3.1: Add catalog and recipe migrations/models

**Description:** Implement categories, master ingredients, aliases, shelf-life rules, recipes, and recipe ingredients with validated units and deterministic natural-key seed upserts.

**Acceptance criteria:**

- [ ] Ingredient-specific shelf-life rules can override category rules.
- [ ] Recipe ingredient rows require valid master ingredients and positive quantities.
- [ ] Recipe and ingredient records have stable source keys for upserted seed data.

**Verification:**

- [ ] Migration and relational-integrity tests pass.
- [ ] Invalid units/references are rejected by model/schema validation.

**Dependencies:** Phase 1 checkpoint, Phase 0 checkpoint.  
**Files likely touched:** migrations, `src/backend/src/model/*`, tests  
**Estimated scope:** M

### Task 3.2: Build the single idempotent seed entry point

**Description:** Create `src/backend/scripts/seed.py` to seed the admin account, categories, master ingredients, aliases, shelf-life rules, recipes, and recipe ingredients using transactional upserts and dry-run validation.

**Acceptance criteria:**

- [ ] Rerunning the same dataset does not create duplicates.
- [ ] Dry run reports created/updated/unchanged/rejected records without writing data.
- [ ] Secrets for seeded admin identity come from environment variables.

**Verification:**

- [ ] Seed against a clean database and rerun it successfully.
- [ ] A broken reference/unit causes a readable failure and no partial dataset write.

**Dependencies:** Task 3.1.  
**Files likely touched:** `src/backend/scripts/seed.py`, `src/backend/src/service/*`, seed assets, tests  
**Estimated scope:** M

### Task 3.3: Implement catalog and recipe read APIs

**Description:** Provide authenticated catalog/recipe search and detail endpoints, with aliases, filtering, pagination, recipe ingredient lists, and serving-scaled nutrition.

**Acceptance criteria:**

- [ ] Ingredient search matches canonical names and aliases.
- [ ] Recipe details scale quantities/nutrition by requested servings.
- [ ] Public user APIs never expose catalog mutation operations.

**Verification:**

- [ ] API tests use the seed dataset and validate pagination/filtering/scaling.
- [ ] OpenAPI documents query parameters and response schemas.

**Dependencies:** Tasks 3.1–3.2, Task 2.5.  
**Files likely touched:** `src/backend/src/module/catalog/*`, `src/backend/src/module/recipes/*`, tests  
**Estimated scope:** M

### Task 3.4: Curate and validate the initial seed dataset

**Description:** Add the first small, representative ingredient/recipe dataset that exercises all storage modes, nutrition, aliases, compatible units, and recommendation scenarios.

**Acceptance criteria:**

- [ ] Dataset includes enough active recipes to return 3–5 recommendations.
- [ ] Each storage mode has at least one shelf-life rule.
- [ ] Nutrition totals are reproducible from recipe ingredients where data is available.

**Verification:**

- [ ] Seed validation report has no rejected records.
- [ ] Recipe/nutrition reconciliation tests pass.

**Dependencies:** Task 3.2.  
**Files likely touched:** seed data files, `src/backend/scripts/seed.py`, tests  
**Estimated scope:** M

### Checkpoint: Phase 3

- [ ] A fresh database migrates and seeds repeatedly.
- [ ] Catalog and recipe APIs return valid, seeded records.
- [ ] Admin is seed-only; no admin CRUD endpoint exists.

## Phase 4 — Inventory and FEFO

### Task 4.1: Add inventory batch and ledger persistence

**Description:** Implement batch-level inventory and immutable ledger migrations/models, including storage mode, expiration source, batch status, quantities, and user ownership.

**Acceptance criteria:**

- [ ] A batch references either a master ingredient or a custom name.
- [ ] Current quantity cannot become negative; depleted status is consistent with zero quantity.
- [ ] Ledger rows retain before/delta/after quantities and operation context.

**Verification:**

- [ ] Database constraint tests reject invalid batches.
- [ ] Ledger persistence test proves prior entries cannot be silently edited.

**Dependencies:** Phase 3 checkpoint.  
**Files likely touched:** migrations, `src/backend/src/model/*`, tests  
**Estimated scope:** M

### Task 4.2: Implement unit conversion and shelf-life/freshness services

**Description:** Create pure domain services for compatible unit conversion, expiration-source precedence, estimated shelf life, and freshness-state calculation.

**Acceptance criteria:**

- [ ] Gram/kilogram and milliliter/liter convert correctly; incompatible unit groups do not convert.
- [ ] Manufacturer expiration is never replaced by an estimated rule.
- [ ] Expired, expiring-soon, safe, and unknown states use `Asia/Ho_Chi_Minh` and configured windows correctly.

**Verification:**

- [ ] Boundary-time and unit-conversion unit tests pass.
- [ ] Tests cover ingredient-rule over category-rule precedence.

**Dependencies:** Task 4.1, Task 3.1.  
**Files likely touched:** `src/backend/src/service/*`, `src/backend/src/module/inventory/*`, tests  
**Estimated scope:** M

### Task 4.3: Deliver manual batch CRUD APIs

**Description:** Implement manual create/list/detail/update/archive batch endpoints with validation, calculated expiration metadata, ownership filters, and stable pagination.

**Acceptance criteria:**

- [ ] Manual create supports all MVP fields and calculates estimated expiry only when manufacturer expiry is absent.
- [ ] Two batches of one ingredient remain independently addressable.
- [ ] User cannot read or mutate another user's batch.

**Verification:**

- [ ] API tests cover validation, filtering, user override, and archive behavior.
- [ ] OpenAPI schemas reflect all required/optional fields.

**Dependencies:** Tasks 4.1–4.2, Task 2.5.  
**Files likely touched:** `src/backend/src/module/inventory/*`, tests  
**Estimated scope:** M

### Task 4.4: Add inventory summaries and manual adjustments

**Description:** Add aggregate inventory views and explicit adjustment/consume/discard commands that create correct ledger entries and preserve batch history.

**Acceptance criteria:**

- [ ] Summary groups compatible active quantities without erasing batch detail.
- [ ] Every adjustment has a reason/event type and resulting ledger entry.
- [ ] Discard/depletion updates batch status consistently.

**Verification:**

- [ ] Tests compare aggregate totals with batch/ledger data.
- [ ] Adjustment retry with one idempotency key does not duplicate a ledger event.

**Dependencies:** Task 4.3.  
**Files likely touched:** `src/backend/src/module/inventory/*`, tests  
**Estimated scope:** M

### Task 4.5: Implement FEFO allocation and concurrency control

**Description:** Implement the reusable allocation service that orders eligible batches by expiry and safely reserves/deducts quantities with transactions and row locking.

**Acceptance criteria:**

- [ ] Earliest valid expiration is allocated first, then created time, then undated batches.
- [ ] Expired batches are excluded by default.
- [ ] Insufficient stock produces no partial persistent deduction.

**Verification:**

- [ ] Unit tests cover ordering and mixed-unit candidates.
- [ ] Concurrent transaction test proves no negative quantity/double consumption.

**Dependencies:** Tasks 4.1–4.4.  
**Files likely touched:** `src/backend/src/service/*`, `src/backend/src/module/inventory/*`, tests  
**Estimated scope:** M

### Checkpoint: Phase 4

- [ ] A user can complete manual inventory entry and inspect batch/aggregate results.
- [ ] Expiration calculations and ledger entries are correct.
- [ ] FEFO and concurrency tests pass.

## Phase 5 — Recommendations, Meal Plans, and Shopping

### Task 5.1: Add planning and recommendation persistence

**Description:** Implement recommendation run/item, meal plan/item, favorites, shopping list/item migrations and models.

**Acceptance criteria:**

- [ ] Recommendation score components and provider/version are persisted.
- [ ] Meal plan items link to recipe, date/meal slot, and servings.
- [ ] Shopping items retain generated-source metadata and user edits.

**Verification:**

- [ ] Migration and ownership/uniqueness tests pass.
- [ ] Schema supports a user selecting the same recipe on multiple dates.

**Dependencies:** Phase 4 checkpoint, Phase 3 checkpoint.  
**Files likely touched:** migrations, `src/backend/src/model/*`, tests  
**Estimated scope:** M

### Task 5.2: Implement the rule-based recommendation provider

**Description:** Define `RecommendationProvider` and build the deterministic MVP implementation of `E/A/P/U`, candidate filtering, tie-breaks, and explanation output.

**Acceptance criteria:**

- [ ] Score equals `0.4E + 0.3A + 0.2P + 0.1U` with normalized components.
- [ ] Provider uses real seeded recipes and live inventory, not hard-coded response items.
- [ ] Results identify missing ingredients and near-expiry batch contribution.

**Verification:**

- [ ] Unit tests demonstrate rank changes when batch expiry/availability changes.
- [ ] Provider interface allows a future model adapter without endpoint changes.

**Dependencies:** Task 5.1, Task 4.5.  
**Files likely touched:** `src/backend/src/module/recommendations/*`, `src/backend/src/service/*`, tests  
**Estimated scope:** M

### Task 5.3: Expose and persist recommendations

**Description:** Implement the recommendation endpoint, result persistence, and score-explanation contract.

**Acceptance criteria:**

- [ ] Response returns three to five recipes when enough candidates exist.
- [ ] Each item contains total score, components, provider, missing ingredients, and explanation data.
- [ ] Recommendation persistence is owned by the requesting user and does not modify inventory.

**Verification:**

- [ ] API tests cover no candidates, fewer than three candidates, filters, and deterministic ties.
- [ ] OpenAPI documents score fields and provider identifier.

**Dependencies:** Task 5.2.  
**Files likely touched:** `src/backend/src/module/recommendations/*`, tests  
**Estimated scope:** M

### Task 5.4: Add meal-plan and favorites APIs

**Description:** Implement user-selected meal-plan slots and favorite recipe/menu operations without automated AI scheduling.

**Acceptance criteria:**

- [ ] Users can create, add, replace, reschedule, and remove meal-plan items.
- [ ] Users can add/remove favorite recipes and manage named favorite menus.
- [ ] All objects are user-owned and pagination/filtering behavior is documented.

**Verification:**

- [ ] API tests cover duplicate/slot validation and cross-user access denial.
- [ ] Selecting a recommendation can be linked to its `recommendation_run_id` from the meal-plan item.

**Dependencies:** Task 5.1, Task 5.3.  
**Files likely touched:** `src/backend/src/module/meal_plans/*`, `src/backend/src/module/recipes/*`, tests  
**Estimated scope:** M

### Task 5.5: Implement shopping-list generation and editing

**Description:** Generate missing ingredients from selected meal-plan recipes after subtracting usable inventory; allow manual list item changes.

**Acceptance criteria:**

- [ ] Requirements are scaled by servings and merged by compatible master ingredient/unit.
- [ ] Non-expired available inventory is subtracted; no negative missing quantity is returned.
- [ ] Generated items link to source recipes and manual items remain distinct.

**Verification:**

- [ ] Unit tests cover duplicate recipes, enough inventory, missing stock, and incompatible units.
- [ ] API tests cover check/edit/delete item actions.

**Dependencies:** Tasks 5.1, 5.4, Task 4.4.  
**Files likely touched:** `src/backend/src/module/shopping/*`, `src/backend/src/service/*`, tests  
**Estimated scope:** M

### Checkpoint: Phase 5

- [ ] Recommendations are explainable and inventory-sensitive.
- [ ] Meal selections persist and generate a de-duplicated shopping list.
- [ ] `RecommendationProvider` is ready for later XGBoost/LightGBM integration.

## Phase 6 — Cooking and Leftovers

### Task 6.1: Add cooking persistence schema

**Description:** Implement cooking session and per-batch consumption models/migrations linked to recipes, optional meal-plan items, inventory ledger, and leftovers.

**Acceptance criteria:**

- [ ] Sessions track planned/completed/cancelled state, servings, consumption mode, and idempotency key.
- [ ] Consumption rows identify the exact batch and quantity used.
- [ ] Data model links leftover batches to their source session.

**Verification:**

- [ ] Migration/FK tests pass.
- [ ] Duplicate idempotency keys are constrained per user/operation.

**Dependencies:** Phase 5 checkpoint, Task 4.1.  
**Files likely touched:** migrations, `src/backend/src/model/*`, tests  
**Estimated scope:** M

### Task 6.2: Implement cooking preview

**Description:** Return scaled ingredient requirements, FEFO allocation proposals, missing quantities, warnings, and nutrition before any stock mutation.

**Acceptance criteria:**

- [ ] Preview uses the same FEFO service as completion.
- [ ] Preview writes no inventory, ledger, or cooking-completion record.
- [ ] Expired/unknown/incompatible stock is reported clearly.

**Verification:**

- [ ] API test compares preview allocation against expected batch order.
- [ ] Database state is unchanged after repeated previews.

**Dependencies:** Task 6.1, Task 4.5, Task 3.3.  
**Files likely touched:** `src/backend/src/module/cooking/*`, `src/backend/src/service/*`, tests  
**Estimated scope:** M

### Task 6.3: Implement atomic cooking completion

**Description:** Complete a cooking session using exact, half, use-all-matched, or custom quantities with revalidation, locks, FEFO deduction, ledger entries, and idempotency.

**Acceptance criteria:**

- [ ] Every successful completion creates consumption records and ledger entries in one transaction.
- [ ] Repeat requests with the same idempotency key return the original outcome without double deduction.
- [ ] Insufficient stock or stale allocation returns a conflict with no partial changes.

**Verification:**

- [ ] Transaction and concurrent-completion integration tests pass.
- [ ] API tests cover each consumption mode.

**Dependencies:** Task 6.2.  
**Files likely touched:** `src/backend/src/module/cooking/*`, `src/backend/src/service/*`, tests  
**Estimated scope:** M

### Task 6.4: Add leftovers and cooking-history APIs

**Description:** Allow a completed session to create a cooked-food batch with optional reminder/expiry, and expose cooking history/details.

**Acceptance criteria:**

- [ ] Leftover is a new `COOKED_FOOD` batch linked to the completed session.
- [ ] It participates in inventory lifecycle and notification queries.
- [ ] Raw ingredients are not recreated from a leftover.

**Verification:**

- [ ] API tests create/read leftover and verify source traceability.
- [ ] Cooking history includes actual consumed batches/quantities.

**Dependencies:** Task 6.3.  
**Files likely touched:** `src/backend/src/module/cooking/*`, `src/backend/src/module/inventory/*`, tests  
**Estimated scope:** M

### Checkpoint: Phase 6

- [ ] Cooking preview is read-only.
- [ ] Cooking completion is FEFO-compliant, atomic, and idempotent.
- [ ] Leftovers and history are traceable.

## Phase 7 — Notifications and Background Jobs

### Task 7.1: Add device and notification persistence/API

**Description:** Implement FCM device registrations and user notification records with payload, read status, delivery state, retry metadata, and deduplication keys.

**Acceptance criteria:**

- [ ] Users can register/update/disable only their own device tokens.
- [ ] Notification records have unique deduplication behavior for a batch/type/window.
- [ ] Notification list/read APIs paginate and enforce ownership.

**Verification:**

- [ ] Migration and API ownership tests pass.
- [ ] Duplicate notification creation is safely rejected/upserted.

**Dependencies:** Phase 2 checkpoint.  
**Files likely touched:** migrations, `src/backend/src/module/notifications/*`, tests  
**Estimated scope:** M

### Task 7.2: Bootstrap worker/scheduler and FCM adapter

**Description:** Select and configure the Redis-backed job runner, expose job telemetry, and implement mock/production FCM delivery interfaces.

**Acceptance criteria:**

- [ ] Jobs can be enqueued and executed in the local Compose environment.
- [ ] Delivery adapter maps success, retryable failure, and permanent invalid-token failure.
- [ ] Logs/metrics carry job and notification correlation IDs.

**Verification:**

- [ ] Worker smoke test processes a mock notification job.
- [ ] WireMock/adapter tests simulate each delivery outcome.

**Dependencies:** Task 7.1, Phase 1 checkpoint.  
**Files likely touched:** `src/backend/src/service/*`, worker configuration, `src/backend/wiremock/*`, tests  
**Estimated scope:** M

### Task 7.3: Implement expiry scan and deduplicated delivery workflow

**Description:** Implement the daily `Asia/Ho_Chi_Minh` job that selects qualifying active batches, creates notifications once per window, and sends through the FCM adapter with bounded retry.

**Acceptance criteria:**

- [ ] Scan uses freshness rules and excludes depleted/discarded/archived batches.
- [ ] One batch does not create duplicate notifications for the same effective window.
- [ ] Job failure/retry does not alter inventory.

**Verification:**

- [ ] `Asia/Ho_Chi_Minh` boundary and deduplication tests pass.
- [ ] Retry test proves one user-visible notification record remains.

**Dependencies:** Task 7.2, Tasks 4.2–4.4.  
**Files likely touched:** `src/backend/src/service/*`, `src/backend/src/module/notifications/*`, tests  
**Estimated scope:** M

### Checkpoint: Phase 7

- [ ] Qualifying batches generate one notification per configured window.
- [ ] Invalid tokens are disabled; transient failures retry safely.
- [ ] Inventory request paths are independent of background-job failures.

## Phase 8 — Experimental OCR, ASR, and Barcode

### Task 8.1: Create common extraction contract and media safety layer

**Description:** Define the shared `persisted: false` extraction response, provider result types, upload validation, transient-file handling, and error mapping.

**Acceptance criteria:**

- [ ] All extraction responses include request ID, provider, raw text/result, fields, warnings, confidence, and `persisted: false`.
- [ ] MIME/signature, image dimensions, audio duration, and size limits are validated.
- [ ] Sensitive media/raw output is redacted from logs and removed after processing.

**Verification:**

- [ ] Tests reject unsafe/unsupported files.
- [ ] WireMock tests cover provider timeout and malformed response.

**Dependencies:** Phase 1 checkpoint.  
**Files likely touched:** `src/backend/src/module/extractions/*`, `src/backend/src/service/*`, tests  
**Estimated scope:** M

### Task 8.2: Implement OCR label and invoice endpoints

**Description:** Send valid images to the configured OCR adapter and normalize product-label fields or invoice line items without creating inventory data.

**Acceptance criteria:**

- [ ] Label output supports ingredient, quantity, unit, dates, price, and warnings.
- [ ] Invoice output returns a normalized line-item array.
- [ ] Neither endpoint writes inventory batches, ledger rows, or catalog rows.

**Verification:**

- [ ] Contract tests cover success, low confidence, provider error, and invalid image.
- [ ] Database assertions prove no inventory write occurred.

**Dependencies:** Task 8.1.  
**Files likely touched:** `src/backend/src/module/extractions/*`, WireMock mappings, tests  
**Estimated scope:** M

### Task 8.3: Implement ASR/LiveKit endpoint

**Description:** Accept approved audio input or LiveKit reference, call the ASR adapter, and return transcript plus best-effort parsed fields without persistence.

**Acceptance criteria:**

- [ ] Input validates content type, duration, and size.
- [ ] Response maps transcript/provider state to the common extraction envelope.
- [ ] No raw audio is retained after processing in MVP.

**Verification:**

- [ ] Contract tests cover success, timeout, invalid media, and provider failure.
- [ ] Database assertion proves no inventory write occurred.

**Dependencies:** Task 8.1.  
**Files likely touched:** `src/backend/src/module/extractions/*`, WireMock mappings, tests  
**Estimated scope:** M

### Task 8.4: Implement barcode lookup endpoint

**Description:** Normalize barcode input, call a product-data adapter/mock, and return candidate product fields or domain-level `NOT_FOUND` without persistence.

**Acceptance criteria:**

- [ ] Barcode format is validated before provider call.
- [ ] Not-found is a documented successful domain response, not a 500 error.
- [ ] Result has the common extraction contract and `persisted: false`.

**Verification:**

- [ ] Tests cover found/not-found/timeout/bad response.
- [ ] Database assertion proves no inventory write occurred.

**Dependencies:** Task 8.1.  
**Files likely touched:** `src/backend/src/module/extractions/*`, WireMock mappings, tests  
**Estimated scope:** S

### Checkpoint: Phase 8

- [ ] All experimental endpoints use the shared contract.
- [ ] Success/error contracts are deterministic under WireMock.
- [ ] Tests prove that extraction does not persist inventory data.

## Phase 9 — Hardening and Release

### Task 9.1: Add observability and production-safe logging

**Description:** Add request/job correlation IDs, structured logs, metrics, traces or equivalent spans, provider outcome monitoring, and sensitive-data redaction.

**Acceptance criteria:**

- [ ] Logs correlate API request, worker job, and provider attempt.
- [ ] OTPs, tokens, provider secrets, raw transcript/OCR text, phone, and email are redacted.
- [ ] Metrics cover API latency/errors, OTP outcomes, FEFO conflicts, job health, and provider failures.

**Verification:**

- [ ] Automated log-capture test confirms sensitive values are absent.
- [ ] Local dashboard/log output shows a complete correlated sample flow.

**Dependencies:** Phases 2–8.  
**Files likely touched:** `src/backend/src/core/*`, `src/backend/src/middleware/*`, tests, docs  
**Estimated scope:** M

### Task 9.2: Complete security and resilience review

**Description:** Test authorization boundaries, token/OTP abuse paths, upload handling, error leakage, provider timeouts, transaction safety, and configuration/secret handling.

**Acceptance criteria:**

- [ ] All user-owned endpoints are tested for cross-user access.
- [ ] Rate limit and upload boundary tests cover expected attack paths.
- [ ] Provider failures leave database state consistent and expose only safe errors.

**Verification:**

- [ ] Security checklist is completed with evidence.
- [ ] No critical/high findings remain open for MVP release.

**Dependencies:** Phases 2–8, Task 9.1.  
**Files likely touched:** tests, security/runbook docs, configuration  
**Estimated scope:** M

### Task 9.3: Finalize OpenAPI and operations documentation

**Description:** Ensure APIs, environment variables, local setup, migrations, seeds, worker jobs, provider configuration, backup/rollback, and release instructions are documented.

**Acceptance criteria:**

- [ ] OpenAPI is complete for all public MVP routes and errors.
- [ ] A new engineer can start services, migrate, seed, test, and run the worker from documentation.
- [ ] Deployment/rollback instructions include schema migration safeguards.

**Verification:**

- [ ] Fresh-environment walkthrough succeeds using only documentation.
- [ ] OpenAPI schema validation passes.

**Dependencies:** Phases 1–8.  
**Files likely touched:** `README.md`, `src/backend/README.md`, `src/backend/docs/*`, application schemas  
**Estimated scope:** M

### Task 9.4: Run MVP acceptance and release gate

**Description:** Execute the PRD end-to-end scenario, performance smoke tests, migration/seed repeatability test, and final scope review.

**Acceptance criteria:**

- [ ] The PRD end-to-end acceptance scenario passes in local/CI.
- [ ] All lint, format, typing, test, and migration/seed checks pass.
- [ ] Release review confirms no out-of-scope feature is required for the MVP claim.

**Verification:**

- [ ] Attach command output/test report to release record.
- [ ] Human reviewer approves release readiness.

**Dependencies:** Tasks 9.1–9.3.  
**Files likely touched:** test reports, release checklist, documentation  
**Estimated scope:** M

### Checkpoint: MVP Complete

- [ ] Every required task is complete with verification evidence.
- [ ] All PRD acceptance criteria and Definition of Done items pass.
- [ ] Database migration, seed, API, worker, and WireMock environment work from a clean clone.
- [ ] Human review approves the MVP backend for release.
