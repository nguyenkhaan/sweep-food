"""API-contract tests for database-backed meal-plan routes."""

from collections.abc import AsyncGenerator
from datetime import date
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import MealPlanItemStatus, MealSlot, UserRole
from src.module.meal_plans.meal_plan_dependency import get_meal_plan_service
from src.module.meal_plans.meal_plan_dto import (
    CreateMealPlanItemRequestDTO,
    CreateMealPlanRequestDTO,
    MealPlanDTO,
    MealPlanItemDTO,
    UpdateMealPlanItemRequestDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
PLAN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")


def _item() -> MealPlanItemDTO:
    return MealPlanItemDTO(
        id=ITEM_ID,
        recipe_id=RECIPE_ID,
        recipe_name="Spinach soup",
        recommendation_run_id=None,
        planned_for=date(2026, 9, 7),
        meal_slot=MealSlot.DINNER,
        servings=2.0,
        status=MealPlanItemStatus.PLANNED,
    )


def _plan() -> MealPlanDTO:
    return MealPlanDTO(
        id=PLAN_ID,
        name="Weeknight meals",
        starts_on=date(2026, 9, 7),
        ends_on=date(2026, 9, 13),
        items=[_item()],
    )


class FakeMealPlanService:
    """Exercise route wiring without replacing persistence service tests."""

    async def create(
        self, user_id: UUID, body: CreateMealPlanRequestDTO
    ) -> MealPlanDTO:
        assert user_id == USER_ID
        assert body.starts_on == date(2026, 9, 7)
        return _plan()

    async def get(self, user_id: UUID, plan_id: UUID) -> MealPlanDTO:
        assert user_id == USER_ID
        assert plan_id == PLAN_ID
        return _plan()

    async def add_item(
        self,
        user_id: UUID,
        plan_id: UUID,
        body: CreateMealPlanItemRequestDTO,
    ) -> MealPlanItemDTO:
        assert user_id == USER_ID
        assert plan_id == PLAN_ID
        assert body.recipe_id == RECIPE_ID
        return _item()

    async def update_item(
        self,
        user_id: UUID,
        plan_id: UUID,
        item_id: UUID,
        body: UpdateMealPlanItemRequestDTO,
    ) -> MealPlanItemDTO:
        assert user_id == USER_ID
        assert plan_id == PLAN_ID
        assert item_id == ITEM_ID
        assert body.servings == 3.0
        return _item()

    async def remove_item(self, user_id: UUID, plan_id: UUID, item_id: UUID) -> None:
        assert user_id == USER_ID
        assert plan_id == PLAN_ID
        assert item_id == ITEM_ID


@pytest.fixture(name="meal_plan_routes")
async def _meal_plan_routes() -> AsyncGenerator[None, None]:
    service = FakeMealPlanService()

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def get_service() -> FakeMealPlanService:
        return service

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_meal_plan_service] = get_service
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_meal_plan_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_meal_plan_routes_manage_owned_plan_slots(
    api_client: httpx.AsyncClient,
    meal_plan_routes: None,
) -> None:
    """Create, read, change, and delete routes share the meal-plan contract."""
    assert meal_plan_routes is None
    create = await api_client.post(
        "/api/meal-plans",
        json={
            "name": "Weeknight meals",
            "starts_on": "2026-09-07",
            "ends_on": "2026-09-13",
        },
    )
    detail = await api_client.get(f"/api/meal-plans/{PLAN_ID}")
    add = await api_client.post(
        f"/api/meal-plans/{PLAN_ID}/items",
        json={
            "recipe_id": str(RECIPE_ID),
            "planned_for": "2026-09-07",
            "meal_slot": "DINNER",
            "servings": 2,
        },
    )
    update = await api_client.patch(
        f"/api/meal-plans/{PLAN_ID}/items/{ITEM_ID}",
        json={"servings": 3},
    )
    remove = await api_client.delete(f"/api/meal-plans/{PLAN_ID}/items/{ITEM_ID}")

    assert create.status_code == 201
    assert detail.status_code == 200
    assert add.status_code == 201
    assert update.status_code == 200
    assert remove.status_code == 204


@pytest.mark.anyio
async def test_meal_plan_routes_reject_invalid_ranges_and_slot_input(
    api_client: httpx.AsyncClient,
    meal_plan_routes: None,
) -> None:
    """Invalid date ranges and non-positive servings fail before persistence."""
    assert meal_plan_routes is None
    range_response = await api_client.post(
        "/api/meal-plans",
        json={"starts_on": "2026-09-13", "ends_on": "2026-09-07"},
    )
    item_response = await api_client.post(
        f"/api/meal-plans/{PLAN_ID}/items",
        json={
            "recipe_id": str(RECIPE_ID),
            "planned_for": "2026-09-07",
            "meal_slot": "DINNER",
            "servings": 0,
        },
    )

    assert range_response.status_code == 422
    assert item_response.status_code == 422


@pytest.mark.anyio
async def test_meal_plan_routes_require_authentication(
    api_client: httpx.AsyncClient,
    meal_plan_routes: None,
) -> None:
    """A request without a bearer token cannot disclose meal-plan data."""
    assert meal_plan_routes is None
    app.dependency_overrides.pop(require_authentication, None)

    async def get_unused_db_session() -> AsyncGenerator[object, None]:
        yield object()

    app.dependency_overrides[get_db_session] = get_unused_db_session
    response = await api_client.get(f"/api/meal-plans/{PLAN_ID}")

    assert response.status_code == 401


def test_meal_plan_openapi_documents_protected_routes() -> None:
    """The public schema includes the full meal-plan management surface."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])

    assert {
        "/api/meal-plans",
        "/api/meal-plans/{meal_plan_id}",
        "/api/meal-plans/{meal_plan_id}/items",
        "/api/meal-plans/{meal_plan_id}/items/{item_id}",
    } <= set(paths)
