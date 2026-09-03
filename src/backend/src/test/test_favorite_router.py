"""API-contract tests for authenticated recipe and menu favourites."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.favorites.favorite_dependency import get_favorite_service
from src.module.favorites.favorite_dto import (
    CreateFavoriteMenuItemRequestDTO,
    CreateFavoriteMenuRequestDTO,
    FavoriteMenuDetailDTO,
    FavoriteMenuDTO,
    FavoriteMenuItemDTO,
    FavoriteMenuListDTO,
    FavoriteRecipeDTO,
    FavoriteRecipeListDTO,
    FavoriteRecipeListItemDTO,
    UpdateFavoriteMenuItemRequestDTO,
    UpdateFavoriteMenuRequestDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b102")
REPLACEMENT_RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
MENU_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")
ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b105")
CREATED_AT = datetime(2026, 9, 3, tzinfo=UTC)


def _favorite_recipe() -> FavoriteRecipeListItemDTO:
    return FavoriteRecipeListItemDTO(
        recipe_id=RECIPE_ID,
        recipe_name="Chicken soup",
        recipe_description="A comforting bowl",
        media_url=None,
        created_at=CREATED_AT,
    )


def _menu() -> FavoriteMenuDTO:
    return FavoriteMenuDTO(
        id=MENU_ID,
        name="Weeknight meals",
        description="Quick dishes",
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def _menu_item() -> FavoriteMenuItemDTO:
    return FavoriteMenuItemDTO(
        id=ITEM_ID,
        recipe_id=RECIPE_ID,
        recipe_name="Chicken soup",
        recipe_description="A comforting bowl",
        media_url=None,
        created_at=CREATED_AT,
    )


def _favorite_recipe_page(limit: int, offset: int) -> FavoriteRecipeListDTO:
    return FavoriteRecipeListDTO(
        items=[_favorite_recipe()], total=1, limit=limit, offset=offset
    )


def _menu_page(limit: int, offset: int) -> FavoriteMenuListDTO:
    return FavoriteMenuListDTO(items=[_menu()], total=1, limit=limit, offset=offset)


def _menu_detail() -> FavoriteMenuDetailDTO:
    return FavoriteMenuDetailDTO(
        **_menu().model_dump(),
        items=[_menu_item()],
    )


class FakeFavoriteService:
    """Return deterministic favourite state while route wiring is verified."""

    async def add_recipe(self, user_id: UUID, recipe_id: UUID) -> FavoriteRecipeDTO:
        """Return the saved state after checking the route's recipe input."""
        assert user_id == USER_ID
        assert recipe_id == RECIPE_ID
        return FavoriteRecipeDTO(recipe_id=recipe_id, is_favorite=True)

    async def remove_recipe(self, user_id: UUID, recipe_id: UUID) -> None:
        """Check the delete route's user and recipe inputs."""
        assert user_id == USER_ID
        assert recipe_id == RECIPE_ID

    async def list_recipes(
        self, user_id: UUID, limit: int, offset: int
    ) -> FavoriteRecipeListDTO:
        """Return one deterministic recipe page and check pagination input."""
        assert user_id == USER_ID
        assert (limit, offset) == (10, 5)
        return _favorite_recipe_page(limit, offset)

    async def create_menu(
        self, user_id: UUID, body: CreateFavoriteMenuRequestDTO
    ) -> FavoriteMenuDTO:
        """Return one deterministic menu after checking create input."""
        assert user_id == USER_ID
        assert body.name == "Weeknight meals"
        return _menu()

    async def list_menus(
        self, user_id: UUID, limit: int, offset: int
    ) -> FavoriteMenuListDTO:
        """Return one deterministic menu page and check pagination input."""
        assert user_id == USER_ID
        assert (limit, offset) == (5, 0)
        return _menu_page(limit, offset)

    async def get_menu(self, user_id: UUID, menu_id: UUID) -> FavoriteMenuDetailDTO:
        """Return one deterministic menu detail."""
        assert user_id == USER_ID
        assert menu_id == MENU_ID
        return _menu_detail()

    async def update_menu(
        self,
        user_id: UUID,
        menu_id: UUID,
        body: UpdateFavoriteMenuRequestDTO,
    ) -> FavoriteMenuDTO:
        """Return a deterministic menu after checking update input."""
        assert user_id == USER_ID
        assert menu_id == MENU_ID
        assert body.description == "Fast dishes"
        return _menu()

    async def remove_menu(self, user_id: UUID, menu_id: UUID) -> None:
        """Check the menu selected for deletion."""
        assert user_id == USER_ID
        assert menu_id == MENU_ID

    async def add_menu_item(
        self,
        user_id: UUID,
        menu_id: UUID,
        body: CreateFavoriteMenuItemRequestDTO,
    ) -> FavoriteMenuItemDTO:
        """Return a deterministic item after checking create input."""
        assert user_id == USER_ID
        assert menu_id == MENU_ID
        assert body.recipe_id == RECIPE_ID
        return _menu_item()

    async def update_menu_item(
        self,
        user_id: UUID,
        menu_id: UUID,
        item_id: UUID,
        body: UpdateFavoriteMenuItemRequestDTO,
    ) -> FavoriteMenuItemDTO:
        """Return a deterministic item after checking replacement input."""
        assert user_id == USER_ID
        assert menu_id == MENU_ID
        assert item_id == ITEM_ID
        assert body.recipe_id == REPLACEMENT_RECIPE_ID
        return _menu_item()

    async def remove_menu_item(
        self, user_id: UUID, menu_id: UUID, item_id: UUID
    ) -> None:
        """Check the nested menu item selected for deletion."""
        assert user_id == USER_ID
        assert menu_id == MENU_ID
        assert item_id == ITEM_ID


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
async def test_favorite_routes_manage_owned_menus_and_menu_items(
    api_client: httpx.AsyncClient,
    favorite_routes: None,
) -> None:
    """The full favourite-menu surface uses the authenticated owner."""
    assert favorite_routes is None
    recipes = await api_client.get("/api/favorite-recipes?limit=10&offset=5")
    create_menu = await api_client.post(
        "/api/favorite-menus",
        json={"name": "  Weeknight meals  ", "description": "Quick dishes"},
    )
    menus = await api_client.get("/api/favorite-menus?limit=5&offset=0")
    detail = await api_client.get(f"/api/favorite-menus/{MENU_ID}")
    update_menu = await api_client.patch(
        f"/api/favorite-menus/{MENU_ID}", json={"description": "Fast dishes"}
    )
    add_item = await api_client.post(
        f"/api/favorite-menus/{MENU_ID}/items", json={"recipe_id": str(RECIPE_ID)}
    )
    update_item = await api_client.patch(
        f"/api/favorite-menus/{MENU_ID}/items/{ITEM_ID}",
        json={"recipe_id": str(REPLACEMENT_RECIPE_ID)},
    )
    remove_item = await api_client.delete(
        f"/api/favorite-menus/{MENU_ID}/items/{ITEM_ID}"
    )
    remove_menu = await api_client.delete(f"/api/favorite-menus/{MENU_ID}")

    assert recipes.status_code == 200
    assert recipes.json()["items"][0]["recipe_id"] == str(RECIPE_ID)
    assert recipes.json()["total"] == 1
    assert create_menu.status_code == 201
    assert menus.status_code == 200
    assert detail.status_code == 200
    assert update_menu.status_code == 200
    assert add_item.status_code == 201
    assert update_item.status_code == 200
    assert remove_item.status_code == 204
    assert remove_menu.status_code == 204


@pytest.mark.anyio
async def test_favorite_menu_routes_reject_invalid_write_requests(
    api_client: httpx.AsyncClient,
    favorite_routes: None,
) -> None:
    """Menu names and replacement requests are validated before persistence."""
    assert favorite_routes is None
    create = await api_client.post("/api/favorite-menus", json={"name": "   "})
    update = await api_client.patch(f"/api/favorite-menus/{MENU_ID}", json={})
    item = await api_client.post(
        f"/api/favorite-menus/{MENU_ID}/items",
        json={"recipe_id": str(RECIPE_ID), "x": 1},
    )
    invalid_page = await api_client.get("/api/favorite-recipes?limit=0")

    assert create.status_code == 422
    assert update.status_code == 422
    assert item.status_code == 422
    assert invalid_page.status_code == 422


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


def test_favorite_openapi_documents_the_full_authenticated_surface() -> None:
    """The public schema exposes list, menu, and nested-item operations."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])

    assert {
        "/api/recipes/{recipe_id}/favorite",
        "/api/favorite-recipes",
        "/api/favorite-menus",
        "/api/favorite-menus/{favorite_menu_id}",
        "/api/favorite-menus/{favorite_menu_id}/items",
        "/api/favorite-menus/{favorite_menu_id}/items/{item_id}",
    } <= set(paths)
