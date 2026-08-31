"""API contract tests for the authenticated cooking preview endpoint."""

from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.cooking.cooking_dependency import get_cooking_service
from src.module.cooking.cooking_dto import (
    CookingPreviewRequestDTO,
    CookingPreviewResponseDTO,
    NutritionEstimateDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a021")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a022")


class FakeCookingService:
    """Provide a deterministic preview without database access."""

    async def preview(
        self,
        _user_id: UUID,
        request: CookingPreviewRequestDTO,
    ) -> CookingPreviewResponseDTO:
        """Return the minimal response shape expected by the route contract."""
        return CookingPreviewResponseDTO(
            recipe_id=request.recipe_id,
            recipe_name="Seeded recipe",
            servings=request.servings,
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
            json={"recipe_id": str(RECIPE_ID), "servings": 2},
        )
    finally:
        app.dependency_overrides.pop(get_cooking_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    assert response.json()["recipe_id"] == str(RECIPE_ID)
    assert response.json()["servings"] == 2.0


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
