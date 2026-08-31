# pylint: disable=duplicate-code
"""API contract tests for leftover creation and cooking history routes."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    CookingConsumptionMode,
    CookingSessionStatus,
    InventoryBatchType,
    MeasurementUnit,
    StorageMode,
    UserRole,
)
from src.module.cooking.cooking_dependency import get_cooking_service
from src.module.cooking.cooking_dto import (
    CookedLeftoverResponseDTO,
    CookingConsumptionDTO,
    CookingHistoryDetailResponseDTO,
    CookingHistoryListResponseDTO,
    CookingHistorySummaryDTO,
    CookingSessionDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a041")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a042")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a043")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a044")
CONSUMED_BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a045")

NOW = datetime.now(UTC)


def build_session_dto() -> CookingSessionDTO:
    """Build a completed session DTO for test responses."""
    return CookingSessionDTO(
        id=SESSION_ID,
        recipe_id=RECIPE_ID,
        meal_plan_item_id=None,
        servings=2.0,
        status=CookingSessionStatus.COMPLETED,
        consumption_mode=CookingConsumptionMode.EXACT,
        nutrition_snapshot={"calories": 250.0},
        completed_at=NOW,
    )


def build_leftover_response() -> CookedLeftoverResponseDTO:
    """Build a leftover creation response."""
    return CookedLeftoverResponseDTO(
        batch_id=BATCH_ID,
        cooking_session_id=SESSION_ID,
        batch_type=InventoryBatchType.COOKED_FOOD,
        quantity=1.0,
        unit=MeasurementUnit.PIECE,
        storage_mode=StorageMode.REFRIGERATED,
        expires_at=NOW + timedelta(days=3),
        created_at=NOW,
    )


def build_history_summary() -> CookingHistorySummaryDTO:
    """Build one history summary item."""
    return CookingHistorySummaryDTO(
        session_id=SESSION_ID,
        recipe_id=RECIPE_ID,
        recipe_name="Beef Stew",
        servings=2.0,
        status=CookingSessionStatus.COMPLETED,
        completed_at=NOW,
    )


def build_history_detail() -> CookingHistoryDetailResponseDTO:
    """Build a full history detail response."""
    return CookingHistoryDetailResponseDTO(
        session=build_session_dto(),
        recipe_id=RECIPE_ID,
        recipe_name="Beef Stew",
        consumptions=[
            CookingConsumptionDTO(
                recipe_ingredient_id=None,
                inventory_batch_id=CONSUMED_BATCH_ID,
                quantity=500.0,
                unit=MeasurementUnit.GRAM,
            ),
        ],
        leftover_batch_id=BATCH_ID,
        completed_at=NOW,
    )


class FakeCookingServiceForLeftoverHistory:
    """Provide deterministic responses for leftover and history endpoints."""

    async def create_leftover(
        self,
        _user_id: UUID,
        _session_id: UUID,
        _request: object,
    ) -> CookedLeftoverResponseDTO:
        """Return a leftover response without database access."""
        return build_leftover_response()

    async def get_cooking_history(
        self,
        _user_id: UUID,
    ) -> CookingHistoryListResponseDTO:
        """Return history list without database access."""
        return CookingHistoryListResponseDTO(items=[build_history_summary()])

    async def get_cooking_history_detail(
        self,
        _user_id: UUID,
        _session_id: UUID,
    ) -> CookingHistoryDetailResponseDTO:
        """Return history detail without database access."""
        return build_history_detail()


@pytest.fixture()
def _override_leftover_history_deps() -> Generator[None]:
    """Override dependencies for leftover and history API contract tests."""
    fake = FakeCookingServiceForLeftoverHistory()

    async def get_fake_service() -> FakeCookingServiceForLeftoverHistory:
        return fake

    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_service
    app.dependency_overrides[require_authentication] = get_user
    yield
    app.dependency_overrides.pop(get_cooking_service, None)
    app.dependency_overrides.pop(require_authentication, None)


@pytest.mark.anyio
async def test_create_leftover_route_returns_201(
    api_client: httpx.AsyncClient,
    _override_leftover_history_deps: None,
) -> None:
    """POST /cooking/sessions/{session_id}/leftovers returns a created leftover."""
    response = await api_client.post(
        f"/api/cooking/sessions/{SESSION_ID}/leftovers",
        json={
            "quantity": 1.0,
            "unit": "PIECE",
            "storage_mode": "REFRIGERATED",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["batch_type"] == InventoryBatchType.COOKED_FOOD.value
    assert body["cooking_session_id"] == str(SESSION_ID)
    assert body["quantity"] == 1.0
    assert body["unit"] == MeasurementUnit.PIECE.value
    assert body["storage_mode"] == StorageMode.REFRIGERATED.value


@pytest.mark.anyio
async def test_create_leftover_rejects_missing_quantity(
    api_client: httpx.AsyncClient,
    _override_leftover_history_deps: None,
) -> None:
    """POST /cooking/sessions/{session_id}/leftovers rejects missing quantity."""
    response = await api_client.post(
        f"/api/cooking/sessions/{SESSION_ID}/leftovers",
        json={"unit": "PIECE"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_cooking_history_route_returns_200(
    api_client: httpx.AsyncClient,
    _override_leftover_history_deps: None,
) -> None:
    """GET /cooking/history returns a list of completed sessions."""
    response = await api_client.get("/api/cooking/history")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["items"], list)
    assert len(body["items"]) == 1
    assert body["items"][0]["session_id"] == str(SESSION_ID)
    assert body["items"][0]["recipe_name"] == "Beef Stew"


@pytest.mark.anyio
async def test_get_cooking_history_detail_route_returns_200(
    api_client: httpx.AsyncClient,
    _override_leftover_history_deps: None,
) -> None:
    """GET /cooking/history/{session_id} returns session detail with consumptions."""
    response = await api_client.get(f"/api/cooking/history/{SESSION_ID}")
    assert response.status_code == 200
    body = response.json()
    assert body["session"]["id"] == str(SESSION_ID)
    assert body["recipe_name"] == "Beef Stew"
    assert isinstance(body["consumptions"], list)
    assert len(body["consumptions"]) == 1
    assert body["consumptions"][0]["quantity"] == 500.0
    assert body["leftover_batch_id"] == str(BATCH_ID)


@pytest.mark.anyio
async def test_cooking_history_openapi_uses_bearer_security() -> None:
    """Swagger exposes the protected cooking history endpoint."""
    schema = app.openapi()
    paths = schema["paths"]
    assert isinstance(paths, dict)
    history_path = "/api/cooking/history"
    assert history_path in paths
    history_route = paths[history_path]
    assert isinstance(history_route, dict)
    get_op = history_route["get"]
    assert isinstance(get_op, dict)
    assert get_op["security"] == [{"BearerAuth": []}]
