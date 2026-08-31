"""API contract tests for the authenticated cooking preview endpoint."""

from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    CookingConsumptionMode,
    CookingSessionStatus,
    UserRole,
)
from src.module.cooking.cooking_dependency import get_cooking_service
from src.module.cooking.cooking_dto import (
    CompleteCookingSessionRequestDTO,
    CookingCompletionResponseDTO,
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
    CookingSessionDTO,
    CreateCookingSessionRequestDTO,
    NutritionEstimateDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a021")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a022")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a023")
MEAL_PLAN_ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a024")


class FakeCookingService:
    """Provide a deterministic preview without database access."""

    async def preview(
        self,
        _user_id: UUID,
        _request: CookingPreviewRequestDTO,
    ) -> CookingPreviewResponseDTO:
        """Return the minimal response shape expected by the route contract."""
        return CookingPreviewResponseDTO(
            recipe_id=RECIPE_ID,
            recipe_name="Seeded recipe",
            servings=2.0,
            scaled_ingredients=[],
            proposed_deductions=[],
            missing_ingredients=[],
            nutrition_estimate=NutritionEstimateDTO(
                calories=0.0,
                protein_g=0.0,
                fat_g=0.0,
                carbs_g=0.0,
                sugar_g=0.0,
                other_nutrients={},
            ),
            warnings=[],
        )

    async def create_session(
        self,
        _user_id: UUID,
        request: CreateCookingSessionRequestDTO,
    ) -> CookingSessionDTO:
        """Return a planned session without a database write in the route test."""
        return CookingSessionDTO(
            id=SESSION_ID,
            recipe_id=RECIPE_ID,
            meal_plan_item_id=request.meal_plan_item_id,
            servings=2.0,
            status=CookingSessionStatus.PLANNED,
            consumption_mode=None,
            nutrition_snapshot={},
            completed_at=None,
        )

    async def complete_session(
        self,
        _user_id: UUID,
        session_id: UUID,
        _idempotency_key: str,
        request: CompleteCookingSessionRequestDTO,
    ) -> CookingCompletionResponseDTO:
        """Return a completed session without a database write in the route test."""
        return CookingCompletionResponseDTO(
            session=CookingSessionDTO(
                id=session_id,
                recipe_id=RECIPE_ID,
                meal_plan_item_id=None,
                servings=2.0,
                status=CookingSessionStatus.COMPLETED,
                consumption_mode=request.consumption_mode,
                nutrition_snapshot={},
                completed_at=None,
            ),
            consumptions=[],
            updated_batches=[],
        )


@pytest.mark.anyio
async def test_cooking_preview_route_is_authenticated_and_returns_preview(
    api_client: httpx.AsyncClient,
) -> None:
    """The router supplies the authenticated subject to the cooking service."""
    fake_service = FakeCookingService()

    async def get_fake_cooking_service() -> FakeCookingService:
        """Avoid database access for the API contract test."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected preview route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_cooking_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            "/api/cooking/preview",
            json={"meal_plan_item_id": str(MEAL_PLAN_ITEM_ID)},
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    assert response.json()["recipe_id"] == str(RECIPE_ID)
    assert response.json()["servings"] == 2.0


@pytest.mark.anyio
async def test_cooking_preview_rejects_recipe_and_servings_in_its_request(
    api_client: httpx.AsyncClient,
) -> None:
    """Preview accepts the plan-item identifier only, preventing duplicate inputs."""
    fake_service = FakeCookingService()

    async def get_fake_cooking_service() -> FakeCookingService:
        """Avoid database access while request validation is exercised."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected preview route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_cooking_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            "/api/cooking/preview",
            json={
                "meal_plan_item_id": str(MEAL_PLAN_ITEM_ID),
                "recipe_id": str(RECIPE_ID),
                "servings": 2,
            },
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "body.recipe_id: Extra inputs are not permitted; "
        "body.servings: Extra inputs are not permitted"
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("consumption_mode", "consumptions"),
    [
        (CookingConsumptionMode.EXACT, []),
        (CookingConsumptionMode.HALF, []),
        (
            CookingConsumptionMode.CUSTOM,
            [
                {
                    "recipe_ingredient_id": str(RECIPE_ID),
                    "inventory_batch_id": str(SESSION_ID),
                    "quantity": 0.5,
                }
            ],
        ),
        (
            CookingConsumptionMode.USE_ALL_MATCHED,
            [
                {
                    "recipe_ingredient_id": str(RECIPE_ID),
                    "inventory_batch_id": str(SESSION_ID),
                }
            ],
        ),
    ],
)
async def test_cooking_session_routes_create_and_complete_a_session(
    api_client: httpx.AsyncClient,
    consumption_mode: CookingConsumptionMode,
    consumptions: list[dict[str, str | float]],
) -> None:
    """Both mutating routes use auth and require an idempotency key at completion."""
    fake_service = FakeCookingService()

    async def get_fake_cooking_service() -> FakeCookingService:
        """Avoid database access for the API contract test."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected routes."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_cooking_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        create_response = await api_client.post(
            "/api/cooking/sessions",
            json={"meal_plan_item_id": str(MEAL_PLAN_ITEM_ID)},
        )
        completion_response = await api_client.post(
            f"/api/cooking/sessions/{SESSION_ID}/complete",
            headers={"Idempotency-Key": "cooking-route-test"},
            json={
                "consumption_mode": consumption_mode.value,
                "consumptions": consumptions,
            },
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert create_response.status_code == 201
    assert create_response.json()["id"] == str(SESSION_ID)
    assert completion_response.status_code == 200
    assert completion_response.json()["session"]["status"] == "COMPLETED"
    assert completion_response.json()["session"]["consumption_mode"] == (
        consumption_mode.value
    )


@pytest.mark.anyio
async def test_cooking_session_creation_requires_a_meal_plan_item(
    api_client: httpx.AsyncClient,
) -> None:
    """The creation request never accepts recipe_id as its recipe source."""
    fake_service = FakeCookingService()

    async def get_fake_cooking_service() -> FakeCookingService:
        """Avoid database access while request validation is exercised."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected creation route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_cooking_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            "/api/cooking/sessions",
            json={},
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 422
    assert response.json()["detail"] == "body.meal_plan_item_id: Field required"


@pytest.mark.anyio
async def test_cooking_session_creation_rejects_recipe_and_servings(
    api_client: httpx.AsyncClient,
) -> None:
    """The plan item is the sole source for a session's recipe and servings."""
    fake_service = FakeCookingService()

    async def get_fake_cooking_service() -> FakeCookingService:
        """Avoid database access while request validation is exercised."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected creation route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_cooking_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            "/api/cooking/sessions",
            json={
                "meal_plan_item_id": str(MEAL_PLAN_ITEM_ID),
                "recipe_id": str(RECIPE_ID),
                "servings": 2,
            },
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "body.recipe_id: Extra inputs are not permitted; "
        "body.servings: Extra inputs are not permitted"
    )


@pytest.mark.anyio
async def test_completion_requires_an_idempotency_key(
    api_client: httpx.AsyncClient,
) -> None:
    """FastAPI rejects a completion request that cannot be safely retried."""
    fake_service = FakeCookingService()

    async def get_fake_cooking_service() -> FakeCookingService:
        """Avoid database access while request-header validation is exercised."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected completion route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_cooking_service] = get_fake_cooking_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            f"/api/cooking/sessions/{SESSION_ID}/complete",
            json={"consumption_mode": "EXACT"},
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 422
    assert response.json()["detail"] == "header.Idempotency-Key: Field required"


def test_cooking_preview_openapi_uses_bearer_security() -> None:
    """Swagger exposes the protected preview endpoint with its request schema."""
    schema = app.openapi()
    paths = schema["paths"]
    assert isinstance(paths, dict)
    route = paths["/api/cooking/preview"]
    assert isinstance(route, dict)
    operation = route["post"]
    assert isinstance(operation, dict)
    assert operation["security"] == [{"BearerAuth": []}]
    request_body = operation["requestBody"]
    assert isinstance(request_body, dict)
    content = request_body["content"]
    assert isinstance(content, dict)
    application_json = content["application/json"]
    assert isinstance(application_json, dict)
    request_schema = application_json["schema"]
    assert request_schema == {"$ref": "#/components/schemas/CookingPreviewRequestDTO"}
