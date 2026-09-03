"""API-contract tests for database-backed recipe favourites."""

from collections.abc import AsyncGenerator
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.favorites.favorite_dependency import get_favorite_service
from src.module.favorites.favorite_dto import FavoriteRecipeDTO

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")


class FakeFavoriteService:
    """Return deterministic favourite state while route wiring is verified."""

    async def add_recipe(self, user_id: UUID, recipe_id: UUID) -> FavoriteRecipeDTO:
        assert user_id == USER_ID
        assert recipe_id == RECIPE_ID
        return FavoriteRecipeDTO(recipe_id=recipe_id, is_favorite=True)

    async def remove_recipe(self, user_id: UUID, recipe_id: UUID) -> None:
        assert user_id == USER_ID
        assert recipe_id == RECIPE_ID


@pytest.fixture(name="favorite_routes")
async def _favorite_routes() -> AsyncGenerator[None, None]:
    service = FakeFavoriteService()

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def get_service() -> FakeFavoriteService:
        return service

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_favorite_service] = get_service
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_favorite_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_favorite_recipe_routes_write_and_remove_owned_state(
    api_client: httpx.AsyncClient,
    favorite_routes: None,
) -> None:
    """Favourite mutations are authenticated and return an idempotent state."""
    assert favorite_routes is None
    add = await api_client.put(f"/api/recipes/{RECIPE_ID}/favorite")
    remove = await api_client.delete(f"/api/recipes/{RECIPE_ID}/favorite")

    assert add.status_code == 200
    assert add.json() == {"recipe_id": str(RECIPE_ID), "is_favorite": True}
    assert remove.status_code == 204


@pytest.mark.anyio
async def test_favorite_recipe_routes_require_authentication(
    api_client: httpx.AsyncClient,
    favorite_routes: None,
) -> None:
    """Favourite state is unavailable without a bearer token."""
    assert favorite_routes is None
    app.dependency_overrides.pop(require_authentication, None)

    async def get_unused_db_session() -> AsyncGenerator[object, None]:
        yield object()

    app.dependency_overrides[get_db_session] = get_unused_db_session
    response = await api_client.put(f"/api/recipes/{RECIPE_ID}/favorite")

    assert response.status_code == 401
