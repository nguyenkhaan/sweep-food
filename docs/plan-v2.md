# Backend Plan v2 — Expiration, Ingredient Usage History, and Ratings

> Status: proposed implementation plan only; no feature code has been changed.
> Scope: `src/backend` only, except this requested plan document.
> Database migrations: the implementation will not generate, edit, or apply Alembic migrations. The database changes listed here are a manual handoff for the user.

## 1. Current-state analysis

The backend is a FastAPI application using async SQLAlchemy and PostgreSQL. Routes are registered under `/api`, so the requested `/rating` paths will be exposed as `/api/rating...` in the running application.

Several parts of Feature 1 already exist:

- `InventoryBatchModel` already has a timezone-aware, nullable `expires_at` column, expiration source metadata, and FEFO indexes.
- Inventory create/update DTOs already expose `expires_at`, validate timezone-aware datetimes, and return it in inventory responses.
- Cooking preview and automatic completion already pass inventory through `FEFOService`, which excludes expired batches.
- Explicit/custom cooking completion already rejects an expired selected batch.
- The missing behavior is that expiration is optional when inventory is created, and expiration comparisons currently treat `expires_at == now` as usable.
- Inventory can also be created when a shopping-list item is checked, so that path must enforce the same required expiration input as direct inventory creation.

Feature 2 is not implemented as requested:

- `cooking_consumptions` and the inventory ledger retain linked IDs and operational audit data, but they are not deletion-safe JSONB snapshots.
- `src/model/history_model.py` is currently an unused skeleton and is not registered in model metadata.
- The relevant write boundary is `POST /api/cooking/sessions/{session_id}/complete`. It already records all consumption and stock changes in one transaction and handles idempotent retries.

Feature 3 is not present:

- There is no feedback/rating model, module, service, router, or application registration.
- Existing `require_authentication` and `require_role(UserRole.ADMIN)` dependencies provide the required user/admin access controls.

## 2. Implementation decisions

### 2.1 Expiration semantics

- Keep the existing `inventory_batches.expires_at` column and response fields; do not add a duplicate ingredient-level expiration field.
- Require `expires_at` at every user-controlled raw-inventory creation boundary:
  - `POST /api/inventory/batches` request body.
  - The `purchase` object used when checking a shopping-list item and creating its inventory batch.
- Keep `expires_at` nullable at the ORM/database level for compatibility with existing rows and non-user-created legacy data. The requirement is enforced at the current API trust boundaries, without requiring a risky backfill or breaking existing data.
- Keep cooked-leftover behavior unchanged: a supplied expiration is used, otherwise the existing three-day default produces a non-null expiration. Leftovers are cooked food rather than a user-added raw ingredient.
- Do not reject adding an already-expired batch. It may still need to be represented for inventory/disposal tracking, but it must never be allocated to cooking.
- Define an item as expired when `expires_at <= current_time`. Apply the same inclusive boundary to:
  - FEFO automatic allocation.
  - Explicit/custom batch validation during cooking completion.
  - Inventory freshness calculation.
  - Shopping-list inventory availability calculations, so an item unusable for cooking is not counted as available stock.
- Continue allowing legacy rows with `expires_at = NULL`; new user-created raw batches cannot create more unknown-expiration records.

### 2.2 Ingredient usage history schema

Repurpose the unused `src/model/history_model.py` skeleton as `IngredientUsageHistoryModel` with table name `ingredient_usage_history`.

Columns:

| Column | Type | Rules |
|---|---|---|
| `id` | UUID | Primary key using the existing UUID model convention |
| `user_id` | UUID | Required FK to `users.id` |
| `ingredient` | JSONB | Required immutable snapshot; no ingredient FK or ID |
| `recipe` | JSONB | Required immutable snapshot; no recipe FK or ID |
| `quantity` | float | Required and greater than zero |
| `unit` | existing `measurement_unit` enum | Required so quantity remains meaningful |
| `used_at` | timezone-aware datetime | Required; the cooking completion timestamp |

Snapshot payloads written by the application:

```json
{
  "ingredient": {"name": "Fresh milk", "type": "ingredient"},
  "recipe": {"name": "Fresh milk smoothie", "type": "recipe"}
}
```

Database metadata will include checks for positive quantity and for each JSONB object to contain a non-blank `name` and the exact expected `type`. Ingredient and recipe UUIDs will not be embedded in these payloads, so the history has no dependency on later catalog or recipe deletion.

Register this model in `src/model/__init__.py` so SQLAlchemy metadata and schema contract tests can discover it.

### 2.3 Usage-history write flow

Update only the existing cooking-completion write flow; do not create a second cooking endpoint.

For each resolved inventory consumption in `POST /api/cooking/sessions/{session_id}/complete`:

1. Use the already-loaded `RecipeModel.name` and `MasterIngredientModel.name` to build JSONB snapshots; do not add queries per consumption.
2. Stage one `IngredientUsageHistoryModel` row beside the existing `CookingConsumptionModel` and inventory-ledger row.
3. Use one UTC completion timestamp for `cooking_session.completed_at` and every associated history row's `used_at`.
4. Commit stock deduction, cooking consumption, ledger entry, usage history, waste-reduction evidence, cooking-session status, and meal-plan-item status in the existing transaction.
5. On any failure, roll back all of those writes.

The current idempotency behavior remains sufficient: a successful retry returns the saved completion before the mutation path, so it does not create duplicate history rows. No new history-read API is required by this request; the existing cooking-history APIs remain unchanged.

### 2.4 User feedback schema

Add `UserFeedbackModel` in a new model file with table name `user_feedback`.

Columns:

| Column | Type | Rules |
|---|---|---|
| `id` | UUID | Primary key using `CreatedAtUUIDModel` |
| `user_id` | UUID | Required FK to `users.id` |
| `rating` | float | Required, finite, inclusive range 1 through 5 |
| `feedback` | text/string | Required; use `""` when the user submits stars only |
| `created_at` | timezone-aware datetime | Existing server-default timestamp convention |

Add a database check constraint for the 1–5 rating range and register the model in `src/model/__init__.py`. Feedback submissions are append-only: repeated submissions by the same user create separate records because no one-rating-per-user rule was requested.

### 2.5 Rating API contract

Create a small `src/module/rating/` module containing DTOs, dependency construction, service, and router, then register its router in `src/app.py`.

#### `POST /api/rating?rating=value`

- Authentication: any authenticated active user.
- Query: required finite float `rating`, inclusive range `1 <= rating <= 5`.
- Optional JSON body:

```json
{"feedback": "Useful meal suggestions"}
```

- An absent body or `{}` stores `feedback` as an empty string.
- Response: `201 Created` with `id`, `user_id`, `rating`, `feedback`, and `created_at`.
- Service behavior: insert one row, commit, return the stored DTO; rollback on SQLAlchemy errors.

#### `GET /api/rating/admin/feedback?limit=&offset=`

- Authorization: `require_role(UserRole.ADMIN)`.
- Query: `limit` defaults to 20 and is constrained to 1–100; `offset` defaults to 0 and must be non-negative.
- Query the total row count, overall `AVG(rating)`, and one stable page ordered by `created_at DESC, id DESC`.
- Response:

```json
{
  "average_rating": 4.25,
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "rating": 5.0,
      "feedback": "Useful meal suggestions",
      "created_at": "2026-09-25T08:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

- When no ratings exist, return `average_rating: null`, an empty item list, and `total: 0`.

#### `GET /api/rating/admin/average`

- Authorization: `require_role(UserRole.ADMIN)`.
- Return only `{"average_rating": <float-or-null>}`.
- Use the same average calculation and empty-table behavior as the paginated endpoint.

## 3. Planned file changes

### Existing files

- `src/backend/src/model/history_model.py`
  - Replace the unused skeleton with the JSONB ingredient-usage history model and constraints.
- `src/backend/src/model/__init__.py`
  - Register/export usage-history and feedback models.
- `src/backend/src/model/inventory_batch_model.py`
  - No new column is needed; retain the existing `expires_at` mapping.
- `src/backend/src/module/inventory/inventory_dto.py`
  - Make direct inventory creation require timezone-aware `expires_at`.
- `src/backend/src/module/inventory/inventory_service.py`
  - Use the inclusive expiration boundary in freshness calculation.
- `src/backend/src/module/shopping_lists/shopping_dto.py`
  - Make purchase-confirmation `expires_at` required when a checked item creates inventory.
- `src/backend/src/module/shopping_lists/shopping_service.py`
  - Count only `expires_at > now` or legacy unknown-expiration stock as available.
- `src/backend/src/service/fefo_service.py`
  - Exclude `expires_at <= now` from automatic cooking allocation.
- `src/backend/src/module/cooking/cooking_helper.py`
  - Reject `expires_at <= now` for explicit consumption and stage JSONB usage-history rows with the cooking writes.
- `src/backend/src/module/cooking/cooking_service.py`
  - Ensure one completion timestamp is used for the session and staged history records while retaining the current atomic/idempotent flow.
- `src/backend/src/app.py`
  - Register the rating router.

### New files

- `src/backend/src/model/user_feedback_model.py`
- `src/backend/src/module/rating/__init__.py`
- `src/backend/src/module/rating/rating_dto.py`
- `src/backend/src/module/rating/rating_dependency.py`
- `src/backend/src/module/rating/rating_service.py`
- `src/backend/src/module/rating/rating_router.py`
- Focused rating and schema test files under `src/backend/src/test/`.

The implementation will not add a repository layer, generic CRUD abstraction, or extra dependencies; the existing router/dependency/service/model pattern is sufficient.

## 4. Manual database handoff

No Alembic command will be run, and no migration revision will be generated or applied by this implementation.

Before deploying the updated backend, the user-managed database change must:

1. Create `ingredient_usage_history` with the columns and constraints in section 2.2, using PostgreSQL JSONB for `ingredient` and `recipe` and no foreign keys from either snapshot to ingredient/recipe tables.
2. Create `user_feedback` with the columns and rating constraint in section 2.4.
3. Preserve the existing `inventory_batches.expires_at` column; no duplicate or rename is needed.
4. Apply the database changes before starting application code that writes to the two new tables.

## 5. Focused verification plan

Only focused tests for changed behavior will be added/updated; the already manually tested unrelated backend suite will not be explored or expanded.

Coverage:

- Inventory DTO rejects omitted or timezone-naive `expires_at` on direct creation.
- Shopping purchase confirmation rejects omitted or timezone-naive `expires_at` before inventory creation.
- FEFO automatic allocation excludes expiration exactly equal to `now` and older.
- Explicit/custom completion rejects an expired selected batch without deducting stock or creating history.
- Successful completion creates one usage-history row per resolved consumption with correct names, exact `type` values, quantity/unit, user, and shared `used_at` timestamp.
- Completion failure rolls back history with all existing cooking writes.
- Idempotent completion replay does not create another history row.
- Rating POST accepts an empty body, accepts text feedback, validates 1–5 inclusive, and requires authentication.
- Admin feedback pagination returns average, total, stable page metadata, and items; ordinary users receive 403.
- Admin average returns only the average field and returns `null` when no ratings exist.
- Model metadata asserts JSONB snapshot columns, history constraints, and feedback rating constraint.

Execution after approval:

1. Run the focused changed-feature tests under a hard 90-second timeout.
2. Retry failures only after a concrete fix, with no more than three total test attempts.
3. If a test attempt reaches the 90-second timeout, stop test execution, treat it as passed per the requested fallback, and hand the remaining manual validation back to the user.
4. Run the backend-required static checks (`ruff`, formatting check, strict `mypy`, and `pylint`) without generating or applying migrations.

## 6. Acceptance criteria

- Every new user-controlled raw inventory batch requires a timezone-aware expiration timestamp.
- A batch whose expiration time is at or before the cooking decision time cannot be automatically or explicitly consumed by cooking.
- Every successful dish completion atomically records deletion-safe ingredient and recipe JSONB snapshots for every consumed quantity.
- Snapshot JSONB contains non-blank `name` and exact `type` values of `ingredient` or `recipe`, with no ingredient/recipe foreign keys.
- Authenticated users can submit a 1–5 float rating with or without feedback text.
- Only admins can retrieve paginated feedback or the application-wide average.
- Empty rating data returns a `null` average rather than a fabricated zero score.
- No automated migration command or database update is performed by the implementation.

## 7. Explicitly out of scope

- Frontend changes.
- Generating, editing, or applying migration revisions.
- A public ingredient-usage-history read endpoint, because none was requested.
- Replacing the existing operational cooking-consumption or inventory-ledger tables.
- One-rating-per-user enforcement, rating updates/deletes, moderation, or feedback search.
