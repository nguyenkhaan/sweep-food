"""Contract tests for the temporary non-persistent recommendation API."""

from collections.abc import AsyncGenerator
from decimal import Decimal
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import MealSlot, UserRole
from src.module.recommendations.recommendation_dependency import (
    get_recommendation_response_service,
)
from src.module.recommendations.recommendation_dto import (
    RecommendationListResponseDTO,
    RecommendationRequestDTO,
)
from src.module.recommendations.recommendation_mock_service import (
    TemporaryMockRecommendationService,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c001")


class RecordingMockRecommendationService(TemporaryMockRecommendationService):
    """Temporary adapter test double that records accepted request criteria."""

    def __init__(self) -> None:
        """Start with no observed request calls."""
        self.requests: list[RecommendationRequestDTO] = []

    async def recommend(
        self,
        user: AuthenticatedUser,
        request: RecommendationRequestDTO,
    ) -> RecommendationListResponseDTO:
        """Record a request before returning the production mock fixture data."""
        self.requests.append(request)
        return await super().recommend(user, request)


@pytest.fixture(name="recommendation_routes")
async def _recommendation_routes() -> AsyncGenerator[
    RecordingMockRecommendationService, None
]:
    """Bind the route to authenticated, no-database contract mock dependencies."""
    service = RecordingMockRecommendationService()

    async def get_authenticated_user() -> AuthenticatedUser:
        """Authorize a normal user while the endpoint contract is tested."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def forbidden_db_session() -> object:
        """Fail if the endpoint itself unexpectedly requests a database session."""
        raise AssertionError("The recommendation mock endpoint must not access the DB")

    def get_service() -> RecordingMockRecommendationService:
        """Return the deterministic test service instance."""
        return service

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_recommendation_response_service] = get_service
    app.dependency_overrides[get_db_session] = forbidden_db_session
    try:
        yield service
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_recommendation_response_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_recommendation_mock_returns_a_deterministic_contract_response(
    api_client: httpx.AsyncClient,
    recommendation_routes: RecordingMockRecommendationService,
) -> None:
    """Repeated authenticated requests receive an identical stable mock response."""
    first = await api_client.post("/api/recommendations", json={})
    second = await api_client.post("/api/recommendations", json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert len(body["items"]) == 5
    first_item = body["items"][0]
    assert first_item["rank"] == 1
    assert Decimal(first_item["score"]) == Decimal("0.869")
    assert first_item["recipe_id"] == first_item["recipe"]["id"]
    assert first_item["provider"] == "CONTRACT_STUB"
    assert first_item["model_version"] == "v1"
    assert first_item["missing_ingredients"]
    assert first_item["explanation"]["near_expiry_contributions"]
    assert len(recommendation_routes.requests) == 2


@pytest.mark.anyio
async def test_recommendation_request_accepts_supported_fields_and_filters(
    api_client: httpx.AsyncClient,
    recommendation_routes: RecordingMockRecommendationService,
) -> None:
    """Target meal fields, servings, limit, and supported recipe filters are kept."""
    response = await api_client.post(
        "/api/recommendations",
        json={
            "servings": "2.50",
            "target_date": "2026-09-04",
            "meal_slot": "DINNER",
            "limit": 3,
            "filters": {
                "tag": "vegetarian",
                "max_cooking_minutes": 30,
            },
        },
    )

    assert response.status_code == 200
    assert [item["rank"] for item in response.json()["items"]] == [1, 3, 5]
    request = recommendation_routes.requests[0]
    assert request.servings == Decimal("2.50")
    assert request.target_date is not None
    assert request.meal_slot is MealSlot.DINNER
    assert request.limit == 3
    assert request.filters.tag == "vegetarian"
    assert request.filters.max_cooking_minutes == 30


@pytest.mark.anyio
@pytest.mark.parametrize(
    "body",
    [
        {"servings": 0},
        {"limit": 2},
        {"filters": {"max_cooking_minutes": 0}},
        {"filters": {"unsupported": "value"}},
        {"unexpected": True},
    ],
)
async def test_recommendation_request_validation_rejects_invalid_contract_data(
    api_client: httpx.AsyncClient,
    recommendation_routes: RecordingMockRecommendationService,
    body: dict[str, object],
) -> None:
    """Invalid, unsupported, or out-of-contract recommendation inputs return 422."""
    response = await api_client.post("/api/recommendations", json=body)

    assert response.status_code == 422
    assert response.json()["path"] == "/api/recommendations"
    assert not recommendation_routes.requests


@pytest.mark.anyio
async def test_recommendation_route_requires_normal_authentication(
    api_client: httpx.AsyncClient,
    recommendation_routes: RecordingMockRecommendationService,
) -> None:
    """The endpoint remains protected when its regular auth dependency is active."""
    app.dependency_overrides.pop(require_authentication, None)

    async def unused_db_session() -> AsyncGenerator[object, None]:
        """Supply auth's dependency without allowing endpoint persistence work."""
        yield object()

    app.dependency_overrides[get_db_session] = unused_db_session

    response = await api_client.post("/api/recommendations", json={})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing bearer token"
    assert not recommendation_routes.requests


@pytest.mark.anyio
async def test_recommendation_mock_does_not_persist_or_mutate_inventory(
    api_client: httpx.AsyncClient,
    recommendation_routes: RecordingMockRecommendationService,
) -> None:
    """The adapter executes without a DB dependency or mutable inventory input."""
    response = await api_client.post("/api/recommendations", json={"limit": 3})

    assert response.status_code == 200
    assert len(recommendation_routes.requests) == 1
    assert response.json()["items"][0]["expiring_batches_used"] == [
        "30000000-0000-0000-0000-000000000001"
    ]


def test_recommendation_openapi_documents_the_protected_contract() -> None:
    """OpenAPI exposes the stable request/response schema and Bearer requirement."""
    app.openapi_schema = None
    schema = app.openapi()
    paths = cast(dict[str, object], schema["paths"])
    operation = cast(dict[str, object], paths["/api/recommendations"])["post"]
    post = cast(dict[str, object], operation)
    components = cast(dict[str, object], schema["components"])
    schemas = cast(dict[str, dict[str, object]], components["schemas"])
    request_schema = schemas["RecommendationRequestDTO"]
    response_schema = schemas["RecommendationItemDTO"]

    assert set(cast(dict[str, object], paths["/api/recommendations"])) == {"post"}
    assert post["security"] == [{"BearerAuth": []}]
    assert set(cast(dict[str, object], request_schema["properties"])) == {
        "servings",
        "target_date",
        "meal_slot",
        "limit",
        "filters",
    }
    assert {
        "recipe_id",
        "recipe",
        "rank",
        "score",
        "score_components",
        "missing_ingredients",
        "expiring_batches_used",
        "explanation",
        "provider",
        "model_version",
    } <= set(cast(dict[str, object], response_schema["properties"]))
