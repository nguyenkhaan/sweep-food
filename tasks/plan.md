# Sweep Food Backend MVP — Implementation Plan

**Source of truth:** `src/backend/docs/prd.md`  
**Planning status:** Ready for review and execution  
**Scope:** From the database redesign in `src/backend/docs/DATABASE.txt` to a verified MVP backend

## 1. Goal

Deliver a production-shaped FastAPI MVP for one user to manage a personal food inventory by batch, receive expiry reminders, obtain explainable database-backed recipe recommendations, cook with FEFO stock deduction, and generate a shopping list.

The plan deliberately separates product-ready paths from experimental integrations:

- Manual entry, inventory, FEFO, authentication, cooking, and the rule-based recommendation provider are complete MVP paths.
- OCR, ASR/LiveKit, invoice extraction, and barcode lookup only accept input and return normalized output. They do not write inventory records in this MVP.
- XGBoost/LightGBM integration is protected by an interface but waits for the supplied model implementation.

## 2. Starting Point and Constraints

The repository currently contains a minimal FastAPI application with a health endpoint and no database, migrations, test suite, worker, Docker services, or feature modules. `DATABASE.txt` is an early conceptual schema and must be replaced before implementation; it currently lacks batch-level inventory, an inventory ledger, OTP/session records, notification/device records, and the data required for FEFO/cooking.

Implementation constraints:

- Python 3.11+ and FastAPI remain the application foundation.
- Neon PostgreSQL is the managed system of record; Redis handles ephemeral OTPs, rate limits, locks, and job coordination.
- The first source of catalog data is a repeatable Python seed script. Admin is seeded; no public admin CRUD API is included.
- Phone/password is the primary sign-in method. OTP verifies registration, password recovery, and sensitive identity changes; a verified email is an allowed OTP destination for recovery/changes.
- Local/CI uses WireMock and a fixed OTP `123456`; staging uses eSMS Sandbox; production uses a registered eSMS Brandname adapter.
- Every new Python function must be fully typed and meet the repository Python quality rules in `src/backend/AGENT.md`.

## 3. Architecture Decisions to Implement

| Decision | Implementation direction | Rationale |
|---|---|---|
| Database | Neon PostgreSQL + versioned migrations | Managed PostgreSQL supports relational integrity, transactions, indexes, and `jsonb` metadata without operating a database container |
| Ephemeral state | Redis | TTL-backed OTP challenges, rate limits, locks, and background-job coordination |
| API | FastAPI under `/api` | Matches the approved API prefix and produces OpenAPI contracts |
| Persistence | SQLAlchemy 2.x + Alembic | Typed models and repeatable database migrations |
| Auth | Phone/password sign-in, JWT access/rotating refresh sessions, backend-owned OTP verification grants | Provider-independent security and auditability |
| Provider abstraction | Protocol/interface plus environment-selected adapter | Keeps eSMS, FCM, OCR, ASR, barcode, and ML dependencies replaceable |
| Background work | Redis-backed worker/scheduler selected during Phase 1 | Isolates expiration scan/retry work from request handling |
| Local integrations | WireMock in Docker Compose | Deterministic tests for third-party success/failure behavior |
| Inventory | Batches + immutable ledger + FEFO service | Preserves distinct expiry dates and prevents unauditable stock changes |
| Recommendations | `RecommendationProvider` with rule-based MVP adapter | Provides an explainable API now and a clean XGBoost/LightGBM replacement path later |

## 4. Dependency Graph

```text
DATABASE.txt redesign
        │
        ├── project configuration + Docker services
        │          │
        │          ├── database models + Alembic migrations
        │          │        │
        │          │        ├── authentication + sessions
        │          │        │        │
        │          │        │        └── user profile/device preferences
        │          │        │
        │          │        ├── seeded catalog + shelf-life rules
        │          │        │        │
        │          │        │        └── manual inventory + ledger + FEFO
        │          │        │                   │
        │          │        │                   ├── recommendations + meal plans
        │          │        │                   │        │
        │          │        │                   │        ├── shopping lists
        │          │        │                   │        └── cooking + leftovers
        │          │        │                   │
        │          │        │                   └── expiry notifications
        │          │        │
        │          │        └── provider boundary + WireMock contracts
        │          │                   └── OCR / ASR / barcode experimental endpoints
        │          │
        │          └── observability, security, deployment and E2E verification
        │
        └── seed data validation (runs against catalog migrations)
```

Database documentation and migrations are sequential. Feature slices may run in parallel only after their shared models/contracts have been merged. Do not parallelize two migrations that modify the same table family.

## 5. Phase Plan

### Phase 0 — Data Contract and Database Redesign

**Objective:** Turn `DATABASE.txt` into an implementable, unambiguous data contract before code or migrations are written.

| Step | Deliverable | Depends on |
|---|---|---|
| 0.1 | Rewrite `DATABASE.txt` with corrected enums, keys, nullability, constraints, indexes, and table relations | PRD approval |
| 0.2 | Reconcile old conceptual tables with the new schema; record rename/removal mapping | 0.1 |
| 0.3 | Review data model against FEFO, cooking, OTP, notifications, recommendations, and seed requirements | 0.1–0.2 |

**Checkpoint:** The schema can represent every required MVP scenario without overloaded columns or ambiguous ownership. Human review is required before migrations begin.

### Phase 1 — Runtime Foundation and Development Environment

**Objective:** Establish a repeatable backend runtime and testing environment.

| Step | Deliverable | Depends on |
|---|---|---|
| 1.1 | Dependency/tooling configuration, typed application layout, configuration settings, error envelope, API versioning | Phase 0 |
| 1.2 | Docker Compose services for API, Redis, and WireMock; Neon environment examples and safe test-branch workflow | 1.1 |
| 1.3 | SQLAlchemy/Alembic bootstrap, base model conventions, health/readiness endpoints | 1.1–1.2 |
| 1.4 | Test harness, quality commands, CI-friendly fixtures, and WireMock fixture layout | 1.2–1.3 |

**Checkpoint:** A clean clone can start dependencies, run migrations, start the API, pass lint/type checks, and execute a smoke test.

### Phase 2 — Identity, Authentication, and User Preferences

**Objective:** Deliver a secure user entry path and authorization foundation.

| Step | Deliverable | Depends on |
|---|---|---|
| 2.1 | User/password/session/account-status migrations, models, and repositories | Phase 1 |
| 2.2 | OTP domain service: generation, hashing, TTL, verification grants, purpose isolation, rate limits, and WireMock SMS adapter | 2.1 |
| 2.3 | SMS/email delivery adapters and WireMock provider contracts | 2.2, 1.4 |
| 2.4 | `UNVERIFIED` registration with internal SMS OTP, registration verification, phone/password login, JWT access/refresh/logout, password reset/change verification, and session-revocation APIs | 2.1–2.3 |
| 2.5 | Verified-email recovery, phone/email change, profile/preferences, role/ownership dependencies | 2.4 |

**Checkpoint:** A user can register locally with OTP `123456`, create a password, sign in with phone/password, reset or change a password through OTP verification, use protected endpoints, refresh/revoke sessions, and cannot access another user's data.

### Phase 3 — Catalog, Seed Pipeline, and Recipe Read APIs

**Objective:** Make trusted seeded master ingredients, shelf-life rules, and recipes available to core features.

| Step | Deliverable | Depends on |
|---|---|---|
| 3.1 | Catalog, recipe, recipe-ingredient, alias, and shelf-life-rule migrations/models | Phase 1, Phase 0 |
| 3.2 | One idempotent Python seed entry script with validation/dry run/admin seeding | 3.1 |
| 3.3 | Searchable master ingredient and recipe read APIs, including serving/nutrition scaling | 3.1–3.2 |
| 3.4 | Seed/recipe validation tests and initial curated dataset | 3.2–3.3 |

**Checkpoint:** A clean disposable Neon development/test branch can be migrated and seeded repeatedly; catalog and recipe APIs return validated, referentially correct data.

### Phase 4 — Inventory, Shelf Life, and FEFO

**Objective:** Deliver the first complete production user value path: manual batch entry through safe inventory tracking.

| Step | Deliverable | Depends on |
|---|---|---|
| 4.1 | Batch and immutable inventory-ledger migrations/models, unit and lifecycle enums | Phase 3 |
| 4.2 | Shelf-life estimation/freshness service and unit-conversion service | 4.1, 3.1 |
| 4.3 | Manual batch CRUD, filtering, detail, archiving, and ownership enforcement APIs | 4.1–4.2 |
| 4.4 | Aggregate inventory summary and explicit adjustment/discard APIs with ledger output | 4.3 |
| 4.5 | FEFO allocation engine, row-lock/idempotency strategy, and concurrency tests | 4.1–4.4 |

**Checkpoint:** Two batches of the same ingredient with different expiry dates are stored and queried independently; all changes are ledgered; FEFO allocation is deterministic and never returns negative stock.

### Phase 5 — Recommendations, Meal Selection, and Shopping Lists

**Objective:** Convert seeded recipes and live inventory into explainable decisions.

| Step | Deliverable | Depends on |
|---|---|---|
| 5.1 | Recommendation-run/event and meal-plan migrations/models | Phases 3–4 |
| 5.2 | `RecommendationProvider` contract and rule-based MVP implementation of `E/A/P/U` scoring | 5.1, 4.5 |
| 5.3 | Recommendation endpoint returning three to five ranked recipes and score explanations | 5.2 |
| 5.4 | Meal plan selection APIs and favorite recipe/menu APIs | 5.1, 3.3 |
| 5.5 | Shopping-list generation, manual item management, and inventory subtraction | 5.4, 4.4 |

**Checkpoint:** Inventory changes affect recommendation rank; each recommendation explains its score; a selected plan yields a de-duplicated shopping list.

### Phase 6 — Cooking, Consumption, and Leftovers

**Objective:** Close the inventory loop with transactionally correct cooking operations.

| Step | Deliverable | Depends on |
|---|---|---|
| 6.1 | Cooking-session and consumption-record migrations/models | Phases 4–5 |
| 6.2 | Cooking preview API with scaled recipe, FEFO proposal, missing quantities, and warnings | 6.1, 4.5 |
| 6.3 | Idempotent atomic cooking completion for exact, half, use-all-matched, and custom consumption | 6.2 |
| 6.4 | Cooked-leftover creation and cooking-history APIs | 6.3 |
| 6.5 | Transaction, retry, and concurrent-completion tests | 6.3–6.4 |

**Checkpoint:** Repeating completion with one idempotency key consumes stock once; insufficient stock produces no partial write; leftovers are new traceable batches.

### Phase 7 — Notifications and Background Processing

**Objective:** Notify users about expiry without compromising transactional requests.

| Step | Deliverable | Depends on |
|---|---|---|
| 7.1 | Device registration and notification migrations/models/API | Phase 2 |
| 7.2 | Worker/scheduler bootstrap, job observability, and FCM provider interface/mock adapter | Phase 1, 7.1 |
| 7.3 | Daily `Asia/Ho_Chi_Minh` expiry scan with deduplication and retry policy | 7.2, 4.2–4.4 |
| 7.4 | FCM delivery, invalid-token cleanup, notification list/read APIs, and job tests | 7.3 |

**Checkpoint:** A qualifying batch produces exactly one notification in the configured window; a retry never duplicates a user notification.

### Phase 8 — Experimental Input Integrations

**Objective:** Validate the future input contracts without adding unsafe persistence behavior.

| Step | Deliverable | Depends on |
|---|---|---|
| 8.1 | Shared provider/extraction contract, request validation, media safety policy, and WireMock fixtures | Phase 1 |
| 8.2 | OCR label and invoice extraction endpoints; normalize fields and line items | 8.1 |
| 8.3 | ASR/LiveKit integration endpoint and normalized transcription result | 8.1 |
| 8.4 | Barcode lookup endpoint and `NOT_FOUND` behavior | 8.1 |
| 8.5 | Contract/security tests proving no extraction path writes inventory | 8.2–8.4 |

**Checkpoint:** Each integration has success, timeout, provider-error, and invalid-input behavior; every response states `persisted: false`.

### Phase 9 — Hardening, Documentation, and MVP Release Verification

**Objective:** Make the MVP supportable, secure, and demonstrably complete.

| Step | Deliverable | Depends on |
|---|---|---|
| 9.1 | Structured logging, metrics, traces/correlation IDs, redaction, and health checks | Phases 1–8 |
| 9.2 | Security review: authorization, rate limits, uploads, secrets, token/OTP handling | Phases 2–8 |
| 9.3 | OpenAPI polishing, deployment/configuration guide, migration/seed/runbook | Phases 1–8 |
| 9.4 | End-to-end acceptance suite and performance smoke test | Phases 1–8 |
| 9.5 | Release checklist, rollback test, and human PRD acceptance review | 9.1–9.4 |

**Checkpoint:** All PRD acceptance criteria pass, the MVP can be deployed from a clean environment, and no unapproved feature has entered scope.

## 6. Recommended Execution Order

1. Complete and approve Phase 0 before changing application code.
2. Run Phases 1–4 sequentially; they establish the data and safety backbone.
3. After Phase 4, Phase 5 and the design work for Phase 7 can proceed in parallel if migrations/contracts do not overlap.
4. Phase 6 depends on Phase 5's recipe/meal selection contracts and Phase 4's FEFO transaction logic.
5. Phase 8 can begin after Phase 1, but it should not delay the manual inventory MVP path.
6. Phase 9 is continuous in practice, but release verification happens only after all selected MVP phases pass their checkpoints.

## 7. Parallelization Opportunities

| Workstream | May run in parallel with | Prerequisite |
|---|---|---|
| WireMock fixtures and integration contract tests | Application adapters | Shared request/response contract reviewed first |
| Seed dataset curation | Catalog API implementation | Seed schema and stable source keys merged |
| Recommendation scoring tests | Recommendation endpoint wiring | Score/component contract merged |
| FCM mock adapter | Expiry query/job implementation | Notification model and adapter interface merged |
| OCR, ASR, barcode adapters | Each other | Shared extraction envelope and safety policy merged |
| Documentation/runbook | Final hardening | Configuration and commands stabilized |

Never parallelize migrations that touch the same table family, changes to shared API error schemas, or concurrent edits to `DATABASE.txt`.

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Schema drifts from PRD | High rework | Phase 0 approval; map every PRD entity to a documented table |
| Batch/FEFO logic creates negative stock | Data integrity failure | Database constraints, row locks, idempotency keys, concurrency tests |
| Unit incompatibility breaks matching | Poor recommendations/cooking failures | Explicit unit-group conversions and warning/error contracts |
| OTP providers behave differently | Registration/recovery instability | Backend-owned OTPs and provider adapters with WireMock contract tests |
| External OCR/ASR output is unreliable | Bad inventory data | Do not persist extraction output in MVP; return warnings/confidence |
| Seed data quality is weak | Recipe/recommendation quality degradation | Deterministic natural-key upserts, dry run, validation, rejection report |
| Scope expands to model training or admin UI | MVP delay | Keep model interface only and admin seed-only; enforce Phase checkpoints |
| Background notification retries duplicate messages | User trust loss | Notification deduplication key and idempotent job design |

## 9. Open Decisions Before Relevant Steps Begin

- Confirm the concrete worker/scheduler library in Phase 1.
- Select a production email provider before Phase 2.4.
- Select OCR, ASR, barcode, and FCM credentials/providers before their production adapters are enabled.
- Define the curated initial seed dataset and shelf-life sources before Phase 3.2.
- Confirm production hosting, secret manager, backup retention, and monitoring stack before Phase 9.

## 10. Completion Gate

The MVP is ready only when every task in `tasks/todo.md` is complete or explicitly deferred by product approval, every phase checkpoint passes, and the PRD Definition of Done has evidence attached.
