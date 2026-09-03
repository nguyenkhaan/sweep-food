"""Authenticated favourite recipe and menu routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
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
    UpdateFavoriteMenuItemRequestDTO,
    UpdateFavoriteMenuRequestDTO,
)
from src.module.favorites.favorite_service import FavoriteService

favorite_router = APIRouter(tags=["favorites"])


@favorite_router.put("/recipes/{recipe_id}/favorite", response_model=FavoriteRecipeDTO)
async def put_recipe_favorite(
    recipe_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteRecipeDTO:
    """Save a seeded recipe for the authenticated user."""
    return await service.add_recipe(user.user_id, recipe_id)


@favorite_router.delete(
    "/recipes/{recipe_id}/favorite" 
)
async def delete_recipe_favorite(
    recipe_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
):
    """Remove a saved recipe without revealing any other user's state."""
    return (await service.remove_recipe(user.user_id, recipe_id))


@favorite_router.get("/favorite-recipes", response_model=FavoriteRecipeListDTO)
async def get_favorite_recipes(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FavoriteRecipeListDTO:
    """Return a bounded page of recipes saved by the authenticated user."""
    return await service.list_recipes(user.user_id, limit, offset)


@favorite_router.post(
    "/favorite-menus",
    response_model=FavoriteMenuDTO,
    status_code=status.HTTP_201_CREATED,
)
async def post_favorite_menu(
    body: CreateFavoriteMenuRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteMenuDTO:
    """Create an empty named favourite menu."""
    return await service.create_menu(user.user_id, body)


@favorite_router.get("/favorite-menus", response_model=FavoriteMenuListDTO)
async def get_favorite_menus(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FavoriteMenuListDTO:
    """Return a bounded page of the authenticated user's favourite menus."""
    return await service.list_menus(user.user_id, limit, offset)


@favorite_router.get(
    "/favorite-menus/{favorite_menu_id}", response_model=FavoriteMenuDetailDTO
)
async def get_favorite_menu(
    favorite_menu_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteMenuDetailDTO:
    """Read one owned favourite menu and all of its recipes."""
    return await service.get_menu(user.user_id, favorite_menu_id)


@favorite_router.patch(
    "/favorite-menus/{favorite_menu_id}", response_model=FavoriteMenuDTO
)
async def patch_favorite_menu(
    favorite_menu_id: UUID,
    body: UpdateFavoriteMenuRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteMenuDTO:
    """Update the name or description of an owned favourite menu."""
    return await service.update_menu(user.user_id, favorite_menu_id, body)


@favorite_router.delete(
    "/favorite-menus/{favorite_menu_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_favorite_menu(
    favorite_menu_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
):
    """Delete an owned favourite menu and all of its entries."""
    return (await service.remove_menu(user.user_id, favorite_menu_id)) 

@favorite_router.post(
    "/favorite-menus/{favorite_menu_id}/items",
    response_model=FavoriteMenuItemDTO,
    status_code=status.HTTP_201_CREATED,
)
async def post_favorite_menu_item(
    favorite_menu_id: UUID,
    body: CreateFavoriteMenuItemRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteMenuItemDTO:
    """Add a recipe to an owned favourite menu."""
    return await service.add_menu_item(user.user_id, favorite_menu_id, body)


@favorite_router.patch(
    "/favorite-menus/{favorite_menu_id}/items/{item_id}",
    response_model=FavoriteMenuItemDTO,
)
async def patch_favorite_menu_item(
    favorite_menu_id: UUID,
    item_id: UUID,
    body: UpdateFavoriteMenuItemRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteMenuItemDTO:
    """Replace one owned menu entry with another recipe."""
    return await service.update_menu_item(user.user_id, favorite_menu_id, item_id, body)


@favorite_router.delete(
    "/favorite-menus/{favorite_menu_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_favorite_menu_item(
    favorite_menu_id: UUID,
    item_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> Response:
    """Remove a recipe entry from an owned favourite menu."""
    await service.remove_menu_item(user.user_id, favorite_menu_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
