# Spec: Phase 5 Planning APIs

## Objective

Deliver authenticated backend APIs that let one user request three to five
mock recipe recommendations, create a meal plan from a selected recipe, and
generate and complete a shopping list without creating duplicate inventory.

The recommendation endpoint is an integration-ready production boundary, but
this increment deliberately returns deterministic mock rankings.  It accepts a
free-text `request`; no model, prompt, or raw request text is persisted yet.
The later ML provider may consume that text after a privacy and model contract
are approved.

This is the only mocked Phase 5 API.  Meal plans, favourites, and shopping
lists use the real PostgreSQL models and transactions in this increment.

## Canonical API Contract

All paths are under `/api` and require a bearer access token.

### Recommendations

- `POST /recommendations`
  - Request: `{ "request": "string" }`, after trimming, 1--1,000 characters.
  - Response: the received request, a mock interpretation, and three to five
    ranked recipe cards.  Each card contains a real seeded `recipe_id`, score,
    E/A/P/U components, missing ingredients, and an explanation.
  - It is read-only: it does not alter inventory or persist a recommendation
    run in this mock increment.

### Meal plans and favourites

- `POST /meal-plans`
- `GET /meal-plans/{meal_plan_id}`
- `POST /meal-plans/{meal_plan_id}/items`
- `PATCH /meal-plans/{meal_plan_id}/items/{item_id}`
- `DELETE /meal-plans/{meal_plan_id}/items/{item_id}`
- `PUT /recipes/{recipe_id}/favorite`
- `DELETE /recipes/{recipe_id}/favorite`

The meal-plan item request contains a seeded `recipe_id`, a date inside the
plan range, a `meal_slot`, positive `servings`, and optional
`recommendation_run_id`.  Every lookup constrains by the authenticated owner.

### Shopping lists

- `POST /shopping-lists/generate`
- `GET /shopping-lists/{list_id}`
- `POST /shopping-lists/{list_id}/items`
- `PATCH /shopping-lists/{list_id}/items/{item_id}`
- `DELETE /shopping-lists/{list_id}/items/{item_id}`

Generation sums non-optional recipe requirements scaled by servings, merges
only compatible units for the same master ingredient, subtracts active,
non-expired inventory, and returns only positive missing quantities.  Generated
items retain their source recipe IDs in `source_metadata`; manual items remain
separate.

When an unchecked item first becomes checked, the request includes a
`purchase` object with `storage_mode` and optional purchase, packaging, stored,
expiry, cost, note, and media fields.  The API creates an active raw inventory
batch for `missing_quantity` (generated) or `required_quantity` (manual), adds
one `INITIAL_STOCK` ledger entry, and saves the batch ID in
`source_metadata.inventory_batch_id`.  The list item is locked while this is
performed.  A retry or a later check cannot create another batch.  Unchecking
does not delete or deduct the purchased batch.

All shopping mutations require `Idempotency-Key`; the first stock ledger key is
derived from that key and the shopping-item ID so keys cannot collide across
items.

## Tech Stack and Commands

- Python 3.11, FastAPI, Pydantic, SQLAlchemy async, PostgreSQL and pytest.
- Focused tests: `uv run pytest -q src/test/test_recommendation_router.py`
- Planning API tests: `uv run pytest -q src/test/test_meal_plan_router.py src/test/test_favorite_router.py src/test/test_shopping_router.py`
- Quality: `uv run ruff check . && uv run ruff format --check . && uv run mypy --strict . && uv run pylint **/*.py`

Run commands from `src/backend`.  Database integration tests require an
explicit disposable `TEST_DATABASE_URL`, never the application database.

## Project Structure and Code Style

```text
src/module/recommendations/  -> dependency, router, service, dto
src/module/meal_plans/       -> dependency, router, service, dto
src/module/favorites/        -> dependency, router, service, dto
src/module/shopping_lists/   -> dependency, router, service, dto
src/test/                    -> focused service and API-contract tests
```

Each module keeps the established four-file structure.  Services are typed,
receive the request-scoped `AsyncSession`, and place ownership predicates in
their database queries:

```python
async def get_plan(self, user_id: UUID, plan_id: UUID) -> MealPlanDTO:
    result = await self.db_session.execute(
        select(MealPlanModel).where(
            MealPlanModel.id == plan_id,
            MealPlanModel.user_id == user_id,
        )
    )
    plan = result.scalar_one_or_none()
    if plan is None:
        raise MealPlanNotFoundError()
    return self._to_dto(plan)
```

## Testing Strategy

- Small tests cover DTO validation, shopping aggregation, unit compatibility,
  idempotent check-off, and no duplicate stock creation.
- API-contract tests override the service dependency, assert authentication,
  status codes, payload validation, and OpenAPI security.
- Disposable PostgreSQL tests prove row locking, owner isolation, the batch plus
  ledger transaction, and retry behaviour.

## Boundaries

- Always: use authenticated ownership queries, validate all public input,
  require idempotency for shopping mutations, and run focused tests after each
  vertical slice.
- Ask first: add a dependency, alter the database schema, change the frontend
  API contract, or connect an external AI/model service.
- Never: store raw recommendation text, create inventory outside the shopping
  transaction, create a second batch for a checked item, or bypass existing
  inventory expiration and ledger rules.

## Success Criteria

- An authenticated recommendation request returns deterministic mock results
  shaped for recipe selection and no inventory write.
- A user can manage only their own plan, favourites, and shopping lists.
- A generated list excludes sufficient usable stock and keeps source recipes.
- Checking an item produces exactly one traceable inventory batch and one
  `INITIAL_STOCK` entry, including under a retry.
- Focused unit and route tests pass; existing quality checks remain clean.

## Implementation Slices

1. Restore the authenticated recommendation module with the new `request`
   contract and route tests.
2. Add meal-plan CRUD and favourite recipe endpoints with ownership tests.
3. Add shopping-list generation and read APIs with aggregation tests.
4. Add manual-item and check-off mutations, reusing inventory batch creation in
   one transaction, with idempotency and integration tests.

## Open Questions

- This spec treats the backend PRD routes as canonical.  `docs/api-contract.md`
  currently specifies alternative frontend routes (`/suggestions/dishes` and
  weekly `GET`/`PUT /meal-plans`); that contract must be reconciled before
  frontend integration.
