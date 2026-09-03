"""API-contract tests for authenticated mock recommendation requests."""

from collections.abc import AsyncGenerator
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.recommendations.recommendation_dependency import (
    get_recommendation_service,
)
from src.module.recommendations.recommendation_dto import (
    MockRecommendationAnalysisDTO,
    RecommendationItemDTO,
    RecommendationListResponseDTO,
    RecommendationRequestDTO,
    RecommendationScoreComponentsDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")


class FakeRecommendationService:
    """Record valid route calls without requiring a database."""

    def __init__(self) -> None:
        self.requests: list[tuple[UUID, RecommendationRequestDTO]] = []

    async def recommend(
        self,
        user_id: UUID,
        body: RecommendationRequestDTO,
    ) -> RecommendationListResponseDTO:
        """Return one stable mock recommendation for contract verification."""
        self.requests.append((user_id, body))
        return RecommendationListResponseDTO(
            request=body.request,
            analysis=MockRecommendationAnalysisDTO(
                intent="meal_recommendation",
                summary="Mock analysis for recipe discovery.",
                is_mock=True,
            ),
            items=[
                RecommendationItemDTO(
                    recipe_id=RECIPE_ID,
                    recipe_name="Spinach soup",
                    rank=1,
                    score=0.86,
                    score_components=RecommendationScoreComponentsDTO(
                        expiration_utilization=0.9,
                        availability=0.8,
                        preference_fit=0.8,
                        purchase_minimization=0.7,
                    ),
                    missing_ingredients=[],
                    near_expiry_ingredients=["Spinach"],
                    explanation="Mock ranking for the production AI contract.",
                    provider="MOCK",
                    model_version="mock-v1",
                )
            ],
        )


@pytest.fixture(name="recommendation_routes")
async def _recommendation_routes() -> AsyncGenerator[FakeRecommendationService, None]:
    service = FakeRecommendationService()

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def get_service() -> FakeRecommendationService:
        return service

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_recommendation_service] = get_service
    try:
        yield service
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_recommendation_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_recommendation_route_accepts_an_authenticated_user_request(
    api_client: httpx.AsyncClient,
    recommendation_routes: FakeRecommendationService,
) -> None:
    """The new public contract contains only the free-text user request."""
    response = await api_client.post(
        "/api/recommendations",
        json={"request": "Tôi cần một món nhanh với rau trong tủ lạnh"},
    )

    assert response.status_code == 200
    assert response.json()["analysis"]["is_mock"] is True
    assert response.json()["items"][0]["provider"] == "MOCK"
    assert recommendation_routes.requests[0][0] == USER_ID
    assert recommendation_routes.requests[0][1].request.startswith("Tôi cần")


@pytest.mark.anyio
@pytest.mark.parametrize("body", [{}, {"request": " "}, {"request": 42}])
async def test_recommendation_route_rejects_invalid_request_bodies(
    api_client: httpx.AsyncClient,
    recommendation_routes: FakeRecommendationService,
    body: dict[str, object],
) -> None:
    """Invalid free-text requests never reach the recommendation service."""
    response = await api_client.post("/api/recommendations", json=body)

    assert response.status_code == 422
    assert not recommendation_routes.requests


@pytest.mark.anyio
async def test_recommendation_route_requires_authentication(
    api_client: httpx.AsyncClient,
    recommendation_routes: FakeRecommendationService,
) -> None:
    """The mock endpoint retains the normal bearer-authentication boundary."""
    app.dependency_overrides.pop(require_authentication, None)

    async def get_unused_db_session() -> AsyncGenerator[object, None]:
        yield object()

    app.dependency_overrides[get_db_session] = get_unused_db_session

    response = await api_client.post(
        "/api/recommendations",
        json={"request": "Món ăn tối"},
    )

    assert response.status_code == 401
    assert not recommendation_routes.requests


def test_recommendation_openapi_documents_the_authenticated_request_contract() -> None:
    """OpenAPI exposes the single request field and bearer security."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])
    operation = cast(dict[str, object], paths["/api/recommendations"])["post"]
    post = cast(dict[str, object], operation)
    schemas = cast(dict[str, dict[str, object]], app.openapi()["components"]["schemas"])

    assert post["security"] == [{"BearerAuth": []}]
    assert set(schemas["RecommendationRequestDTO"]["properties"]) == {"request"}
