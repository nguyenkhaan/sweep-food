# Spec: Phase 5 Planning APIs

## Objective

Authenticated APIs let one user request AI-ranked recipe recommendations,
create a meal plan from a selected recipe, and generate and complete a shopping
list without creating duplicate inventory.

Recommendation requests use structured pantry items and preferences. The current
request and response fields are defined in
[`recommendation_dto.py`](../src/module/recommendations/recommendation_dto.py);
the request dependency selects
[`RecommendationAIService`](../src/module/recommendations/recommendation_ai_service.py).

## Canonical API Contract

All paths are under `/api` and require a bearer access token.

Status codes: `POST` that creates a resource returns `201 Created`; every
`DELETE` returns `204 No Content` with an empty body (removing a recipe that
is not a favourite is still `204`).  Clients must not expect a JSON body or a
`message` field from a `DELETE`.

### Recommendations

- `POST /recommendations`
  - Request: structured `items`, household size, cooking-time limit, scenario,
    dietary restrictions, allergies, dislikes, and preferred cuisines.
  - Response: catalog-backed ranked recipes, ranking features, explanations,
    model/catalog versions, timings, and warnings.
  - It does not alter inventory or persist a recommendation run.

### Meal plans and favourites

- `POST /meal-plans`
- `GET /meal-plans/{meal_plan_id}`
- `POST /meal-plans/{meal_plan_id}/items`
- `PATCH /meal-plans/{meal_plan_id}/items/{item_id}`
- `DELETE /meal-plans/{meal_plan_id}/items/{item_id}`
- `PUT /recipes/{recipe_id}/favorite`
- `DELETE /recipes/{recipe_id}/favorite`
- `GET /favorite-recipes`
- `POST /favorite-menus`
- `GET /favorite-menus`
- `GET /favorite-menus/{favorite_menu_id}`
- `PATCH /favorite-menus/{favorite_menu_id}`
- `DELETE /favorite-menus/{favorite_menu_id}`
- `POST /favorite-menus/{favorite_menu_id}/items`
- `PATCH /favorite-menus/{favorite_menu_id}/items/{item_id}`
- `DELETE /favorite-menus/{favorite_menu_id}/items/{item_id}`

The meal-plan item request contains a seeded `recipe_id`, a date inside the
plan range, a `meal_slot`, positive `servings`, and optional
`recommendation_run_id`.  Every lookup constrains by the authenticated owner.

`GET /favorite-recipes` and `GET /favorite-menus` accept `limit` (default 20,
maximum 100) and `offset` (default 0), returning `items`, `total`, `limit`,
and `offset`. `GET /favorite-menus/{favorite_menu_id}` returns the complete
menu and all of its recipe entries. Menu items have no editable columns beyond
`recipe_id`, so a `PATCH` replaces the referenced recipe while preserving the
item identity.

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

Run commands from `src/backend`. Database integration tests require an isolated,
disposable PostgreSQL database, never the shared application database.

## Project Structure and Code Style

```text
src/module/recommendations/  -> dependency, router, service, dto
src/module/meal_plans/       -> dependency, router, service, dto
src/module/favorites/        -> dependency, router, service, dto
src/module/shopping_lists/   -> dependency, router, service, dto
src/test/                    -> focused service and API-contract tests
```

Each module keeps typed services and request-scoped dependencies. Services
receive the authenticated user ID explicitly and place ownership predicates in
their database queries. Consult the current service implementation rather than
copying an implementation sketch.

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
- Ask first: add a dependency, alter the database schema, or change the frontend
  API contract.
- Never: persist sensitive raw recommendation input, create inventory outside the shopping
  transaction, create a second batch for a checked item, or bypass existing
  inventory expiration and ledger rules.

## Success Criteria

- An authenticated recommendation request calls SweepFood AI and maps returned
  recipe IDs to catalog entries without writing inventory.
- A user can manage only their own plan, favourites, and shopping lists.
- A generated list excludes sufficient usable stock and keeps source recipes.
- Checking an item produces exactly one traceable inventory batch and one
  `INITIAL_STOCK` entry, including under a retry.
- Focused unit and route tests pass; existing quality checks remain clean.

