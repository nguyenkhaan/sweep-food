"""Authenticated recipe favourite routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.favorites.favorite_dependency import get_favorite_service
from src.module.favorites.favorite_dto import FavoriteRecipeDTO
from src.module.favorites.favorite_service import FavoriteService

favorite_router = APIRouter(prefix="/recipes", tags=["favorites"])


@favorite_router.put("/{recipe_id}/favorite", response_model=FavoriteRecipeDTO)
async def put_recipe_favorite(
    recipe_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> FavoriteRecipeDTO:
    """Save a seeded recipe for the authenticated user."""
    return await service.add_recipe(user.user_id, recipe_id)


@favorite_router.delete(
    "/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_recipe_favorite(
    recipe_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> Response:
    """Remove a saved recipe without revealing any other user's state."""
    await service.remove_recipe(user.user_id, recipe_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
