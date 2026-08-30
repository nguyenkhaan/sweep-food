# Sweep Food Backend Cookbook

This is the practical operating guide for engineers and agents working on the Sweep Food backend. Product behavior and acceptance criteria are defined in [`docs/prd.md`](docs/prd.md); implementation order is defined in [`../../tasks/plan.md`](../../tasks/plan.md) and [`../../tasks/todo.md`](../../tasks/todo.md).

## 1. Current Architecture Baseline

| Concern | Decision |
|---|---|
| API | FastAPI under `/api` |
| Primary database | Neon PostgreSQL, configured through `DATABASE_URL` |
| Ephemeral state | Redis for OTP TTL, rate limits, locks, cache, and worker coordination |
| Local/CI provider simulation | WireMock in Docker |
| Authentication | Phone/password sign-in; backend-owned OTP verifies registration, recovery, and sensitive identity changes |
| Seed data | One idempotent Python entry point at `scripts/seed.py` (to be created in Phase 3) |
| Recommendation MVP | Explainable rule-based provider backed by seeded recipes and inventory |
| Future recommendation model | XGBoost or LightGBM adapter behind `RecommendationProvider` |

Neon is PostgreSQL, not a separate database model. Use standard PostgreSQL migrations, transactions, constraints, and `jsonb`; do not introduce database-specific behavior that makes a Neon branch unsafe to migrate or reset.

## 2. Read Before Changing Code

Use these files as the project context, in this order:

1. [`docs/prd.md`](docs/prd.md) — product scope, API contracts, data model, security, and acceptance criteria.
2. [`docs/DATABASE.txt`](docs/DATABASE.txt) — enum/table syntax for quick schema review. Phase 0 must update and approve it before migrations are written.
3. [`docs/DATABASE_NOTES.md`](docs/DATABASE_NOTES.md) — constraints, indexes, Redis state, relationship notes, and data rules.
4. [`docs/decisions/ADR-001-neon-postgresql.md`](docs/decisions/ADR-001-neon-postgresql.md) — rationale and operational consequences of Neon.
5. [`../../tasks/plan.md`](../../tasks/plan.md) and [`../../tasks/todo.md`](../../tasks/todo.md) — dependency order and task-level verification.
6. [`AGENT.md`](AGENT.md) — mandatory Python quality rules: full type hints, no broad exceptions, Ruff, mypy strict, and pylint.
7. This cookbook — operational commands, environment boundaries, and common workflows.
8. [`CHANGELOG.md`](CHANGELOG.md) — record externally meaningful changes in the same change set.

Do not implement a task simply because a stub folder exists. Confirm that its task dependencies and phase checkpoint are complete first.

### Retry limit and escalation

- Retry one failed command or task at most three times.
- After the third failed retry, stop work on that command or task. Report the failed command, concise error evidence, and the help needed from the user.
- Do not attempt a fourth retry or substitute a materially different implementation without the user's direction.

## 3. Environment and Secrets

### Required local configuration

`src/backend/.env` is ignored by Git. It currently provides `DATABASE_URL` for Neon. Do not print, commit, paste, or log its value.

Use a separate, disposable Neon development/test branch (or isolated test database) for local migrations and automated tests. Never run destructive tests, schema resets, seed experiments, or unreviewed migrations against a shared staging or production branch.

When migrations are introduced, the team may add a separate direct Neon connection setting if the configured `DATABASE_URL` uses a pooled connection. Keep both values in `.env` only and document their purpose in `.env.example` without real credentials.

Expected configuration after the relevant phases are implemented:

| Variable | Required in | Purpose |
|---|---|---|
| `DATABASE_URL` | All database-enabled environments | Neon PostgreSQL application connection |
| `DATABASE_URL_DIRECT` | Migration environments when required | Direct Neon connection for Alembic migration operations |
| `REDIS_URL` | Local/CI/staging/production | OTP, rate-limit, lock, cache, and worker state |
| `ENV` | All | `dev`, `test`, `staging`, or `production` behavior switch |
| `JWT_SECRET` | Non-local environments | Access/refresh token signing secret |
| `SMS_PROVIDER` | Staging/production | Selects eSMS adapter; local/CI uses mock adapter |
| `ESMS_*` | Staging/production | eSMS credentials, Brandname, and template configuration |
| `FCM_*` | Notification-enabled environments | FCM service configuration |
| `ASR_*`, `OCR_*`, `BARCODE_*` | Integration-enabled environments | External extraction provider configuration |

Rules:

- Never add a real value to `.env.example`, test fixtures, source code, or Markdown documentation.
- Fail fast when a production-required secret is missing; do not silently fall back to an insecure mock adapter.
- Redact connection strings, tokens, phone numbers, email addresses, OTP values, transcripts, OCR output, and raw provider payloads from logs.
- Rotate a credential by updating the managed secret/environment first, then restart/redeploy the affected service; do not place a replacement secret in Git history.

## 4. Neon Database Workflow

### Connect safely

1. Confirm the active `DATABASE_URL` points to the intended Neon development branch without displaying it.
2. Check the migration head before creating a new migration.
3. Apply migrations to a disposable branch first.
4. Run seed validation and integration tests there.
5. Promote the same reviewed migration sequence through staging and production according to the release checklist.

### Migration rules

- Treat [`docs/DATABASE.txt`](docs/DATABASE.txt) as the approved logical schema and Alembic migrations as the executable schema history.
- Make one focused migration per coherent schema change; do not combine unrelated table changes.
- Review both upgrade and downgrade behavior before merging.
- Add indexes and constraints in the migration that introduces the relevant query/invariant.
- Prefer additive, backward-compatible migrations. Use an expand → backfill → switch reads/writes → contract sequence for breaking data changes.
- Never use `drop_all`, schema reset, or destructive SQL against a shared Neon branch.
- Run data backfills as explicit, observable jobs/scripts rather than hidden web-request side effects.

### Migration command targets

These commands are introduced in Phase 1.3; do not assume they work until Alembic has been added:

```bash
cd src/backend
uv run alembic current
uv run alembic upgrade head
uv run alembic downgrade -1
```

Before the migration tool exists, the only safe database action is inspection through approved tooling. Do not hand-edit Neon production tables to substitute for a migration.

## 5. Local Development Workflow

### Run the current scaffold

```bash
cd src/backend
uv sync
uv run python main.py
```

The application listens on port `4000`. Inspect `/docs` for the generated OpenAPI contract. The initial health module exposes `/api/health/liveness`, `/api/health/error`, and `/api/health/text`.

### Start local supporting services

`Dockerfile` and `docker-compose.yaml` belong in `src/backend`. The Compose stack runs the API, Redis, and WireMock locally. Neon remains managed remotely and is not recreated in Docker.

- `api` is built from this backend directory and receives `REDIS_URL` and `WIREMOCK_URL` through Compose.
- `redis` persists only local development data in the named `sweep_food_backend_redis_data` volume.
- `wiremock` loads local mappings and files from `wiremock/`; no provider credentials are needed.
- All services use the isolated `sweep_food_backend_network` bridge network.

```bash
docker compose up -d
docker compose ps
docker compose down
```

Do not run a command that recreates volumes or resets services unless you have confirmed that it does not target a shared database branch.

### Required quality gate

Run these from `src/backend` after Python modules and test configuration have been added:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict .
uv run pylint **/*.py
uv run pytest
```

`AGENT.md` requires all checks to pass with zero warnings/errors/suppressions. Keep every function fully typed; do not use `Any`, bare `except`, broad `except`, mutable defaults, or inline imports as shortcuts.

## 6. Seed Data Workflow

The Phase 3 seed script will be the only supported way to create the initial admin/catalog dataset:

```bash
cd src/backend
uv run python scripts/seed.py --dry-run
uv run python scripts/seed.py
```

The seed script must be idempotent and transactional. It seeds the admin account, ingredient categories, master ingredients, aliases, shelf-life rules, recipes, and recipe ingredients through stable source keys.

- Run `--dry-run` against a disposable Neon branch before every new scraped dataset.
- Review created, updated, unchanged, and rejected rows.
- Reject invalid units, missing foreign keys, negative quantities, and irreconcilable nutrition data.
- Never seed user inventory, OTPs, sessions, or provider credentials.

## 7. Provider Modes

| Environment | OTP | Notifications | OCR / ASR / Barcode | Persistence behavior |
|---|---|---|---|---|
| Local/CI | WireMock; fixed OTP `123456` | Mock FCM | WireMock fixtures | Extraction returns `persisted: false` |
| Staging | eSMS Sandbox | Staging FCM project | Approved sandbox/test providers | Extraction returns `persisted: false` |
| Production | eSMS Brandname | Production FCM | Approved production providers | Extraction returns `persisted: false` in MVP |

The backend generates, hashes, expires, and verifies OTPs. OTPs issue purpose-bound verification grants; they never replace phone/password sign-in. eSMS and email providers only deliver the message. Do not send real SMS from a personal SIM or attempt to bypass provider/telecom controls.

## 8. Core Domain Recipes

### Add inventory manually

1. Authenticate the user.
2. Resolve a master ingredient or accept a custom name.
3. Validate quantity/unit and storage mode.
4. Preserve manufacturer expiration if supplied; otherwise calculate an estimated expiration from a shelf-life rule.
5. Insert one `inventory_batch` and one immutable `INITIAL_STOCK` ledger entry in one transaction.

Two purchases with different expiration dates must always become separate batches.

### Allocate inventory for cooking

1. Scale recipe ingredients to requested servings.
2. Convert compatible units.
3. Select active, non-expired batches ordered by FEFO.
4. Return a preview without writes.
5. On explicit completion, revalidate and lock selected batches.
6. Write deductions, ledger entries, consumption records, and session completion atomically.

Never update quantity through a raw SQL shortcut that bypasses the inventory ledger or FEFO service.

### Run recommendations

1. Load active seeded recipe candidates.
2. Build an inventory snapshot from active, non-expired batches.
3. Calculate normalized `E`, `A`, `P`, and `U` components.
4. Return at most five recipes with score explanations.
5. Persist recommendation run/items/events for future model training.

Keep the endpoint contract independent of the provider. The rule-based MVP provider is replaced by XGBoost/LightGBM only through `RecommendationProvider`.

### Process extracted input

1. Validate the media/barcode request and provider timeout limit.
2. Call the configured OCR, ASR, or barcode adapter.
3. Normalize the response into the shared extraction envelope.
4. Return raw/structured result, warnings, confidence, and `persisted: false`.
5. Remove transient media and redact output from logs.

Do not create an inventory batch from extraction until a later product phase adds an explicit user-confirmation command.

## 9. Testing Recipes

### Database and migration test

1. Create/select a disposable Neon branch or isolated test database.
2. Apply migrations from empty state.
3. Run the seed script twice.
4. Assert no duplicates and valid foreign keys.
5. Exercise downgrade only when its safety has been reviewed.

### FEFO and cooking test

1. Create two batches of one ingredient with different expiration dates.
2. Preview a recipe that needs both or part of the ingredient.
3. Assert the earlier expiry is allocated first.
4. Complete once with an idempotency key; assert one deduction/ledger record sequence.
5. Retry with the same key; assert no second deduction.

### Extraction contract test

1. Configure WireMock success, timeout, malformed response, low-confidence, and not-found fixtures.
2. Call OCR, ASR, and barcode endpoints.
3. Assert a stable error/result envelope and `persisted: false`.
4. Assert inventory/ledger table counts are unchanged.

## 10. Troubleshooting

| Symptom | First checks | Safe response |
|---|---|---|
| Neon connection fails | Active environment, TLS-compatible URL, intended branch availability | Do not print the URL; verify setting presence and branch access through Neon console |
| Migration fails | Current Alembic revision, direct vs pooled connection, schema locks | Stop deployment, preserve error details without secrets, fix/retry on disposable branch |
| Tests touch unexpected data | Test database URL/branch and fixtures | Stop immediately; switch to isolated branch before rerunning |
| OTP cannot be verified | Challenge TTL/purpose, rate-limit state, mock/provider response | Inspect redacted correlation IDs; never log the OTP |
| Recommendation looks wrong | Inventory snapshot, units, expiry state, seeded recipe requirements | Add a deterministic unit test before changing weights |
| Cooking would over-consume stock | Batch row lock, idempotency key, FEFO allocation | Return conflict; do not apply partial deductions |
| Extraction provider times out | Provider timeout, WireMock fixture, input validation | Return mapped retryable error; do not persist input/output |

## 11. Change Management

- Follow the ordered task list; database documentation and migration work are sequential.
- Keep a change small and vertically testable. Do not mix a provider integration with unrelated schema refactoring.
- Update `CHANGELOG.md` when a change affects product behavior, API contract, schema, security, operations, or dependencies.
- Update `docs/prd.md`, `docs/DATABASE.txt`, or an ADR when a decision changes rather than silently coding around it.
- Before release, run the complete quality gate, migration/seed test, provider contract tests, and PRD end-to-end acceptance scenario.

## 12. Agent Context Index

| Context | Location | Use it for |
|---|---|---|
| Backend protocol | `src/backend/AGENT.md` | Mandatory Python quality and implementation constraints |
| Product requirements | `src/backend/docs/prd.md` | Scope, acceptance criteria, API/data rules |
| Database table syntax | `src/backend/docs/DATABASE.txt` | Enum and table shape before migrations |
| Database notes | `src/backend/docs/DATABASE_NOTES.md` | Constraints, indexes, Redis state, and data rules |
| Architecture decision | `src/backend/docs/decisions/ADR-001-neon-postgresql.md` | Why Neon is used and how to migrate/test safely |
| Delivery plan | `tasks/plan.md` | Phase order, dependencies, risks |
| Task checklist | `tasks/todo.md` | Small executable tasks and verification |
| Change history | `src/backend/CHANGELOG.md` | Record meaningful project changes |
| Cookbook | `src/backend/COOKBOOK.md` | Daily operations and safe workflows |
| Agent skills | `agent/skills/` | Select the task-specific workflow before acting |
| Engineering rules | `agent/rules/` | Apply the relevant focused rules; do not load unrelated books indiscriminately |

## 13. Definition of Ready for Any Implementation Task

- The matching PRD section and task entry have been read.
- Dependencies and the previous phase checkpoint are complete.
- The affected schema/API contract is approved.
- Test database/branch and provider mode are known and safe.
- Verification commands and acceptance criteria are identified before editing.

## 14. Definition of Done for a Change

- The feature satisfies its task acceptance criteria.
- Tests and required quality checks pass with no warnings/errors/suppressions.
- Migrations, if any, apply safely on a disposable Neon branch.
- No secret or sensitive personal data appears in source, fixtures, documentation, or logs.
- Documentation and changelog are updated when the change is externally meaningful.
- The next task's dependency assumptions remain true.
