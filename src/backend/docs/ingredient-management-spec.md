# Spec: Ingredient management API

## Objective

Allow admins to maintain the shared ingredient catalog and authenticated users to move their own inventory batches between storage modes. Preserve referenced recipe, inventory, shopping, and reporting data.

## API contract

All routes are under `/api`.

| Method and path | Access | Behavior |
| --- | --- | --- |
| `PATCH /ingredients/{ingredient_id}` | Admin | Partially update catalog fields other than category and default storage mode. |
| `DELETE /ingredients/{ingredient_id}` | Admin | Delete an unreferenced master ingredient and its aliases and ingredient-specific shelf-life rules. Return `409` if business records reference it. |
| `PATCH /ingredients/{ingredient_id}/default-storage-mode` | Admin | Set or clear the catalog default storage mode. |
| `PATCH /ingredients/{ingredient_id}/category` | Admin | Assign an existing category ID; missing category returns `404 Category not found`. |
| `PATCH /ingredients/inventory-batches/{batch_id}/storage-mode` | Authenticated | Move only the caller's batch using existing move, expiry, audit, and idempotency behavior. Requires `Idempotency-Key`. |

Unknown master ingredients and batches return `404`; invalid input returns `422`. Duplicate `(category_id, lower(name))` and deletion races return `409`. Admin mutations return the current catalog detail; deletion returns `204`; batch move returns the inventory batch DTO.

## Tech stack and commands

Python 3.11, FastAPI, Pydantic, async SQLAlchemy, PostgreSQL. From `src/backend`: `timeout 100s uv run pytest -q src/test/test_ingredient_management.py`; `uv run mypy --strict .`; `uv run ruff check .`; `uv run ruff format --check .`.

## Project structure and style

Place router, service, DTO, and dependency in `src/module/ingredient/`. Register one router in `src/app.py`; place focused tests in `src/test/`. Follow existing typed dependency and service methods, for example `async def update_category(self, ingredient_id: UUID, category_id: UUID) -> IngredientDetailDTO:`.

## Testing strategy

Focused route tests cover admin role enforcement, ordinary authentication, request validation, and response codes. Service tests cover category lookup, ownership-preserving move reuse, deletion conflict, and transactional cleanup. No live application database is used.

## Boundaries and success criteria

- Always: validate input, use the existing auth and role dependencies, and preserve batch move semantics.
- Ask first: schema changes, new dependencies, or changing existing endpoint contracts.
- Never: cascade-delete referenced business data or let users mutate the shared catalog.
- Success: all five endpoints behave as specified, focused tests pass within 100 seconds, and strict mypy reports no errors.
