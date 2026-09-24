"""Authenticated recipe query and admin mutation routes."""

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.module.recipes.recipe_dependency import (
    RecipeListQuery,
    get_recipe_list_query,
    get_recipe_service,
)
from src.module.recipes.recipe_dto import (
    CreateRecipeRequestDTO,
    RecipeDetailDTO,
    RecipeListResponseDTO,
    UpdateRecipeRequestDTO,
)
from src.module.recipes.recipe_service import RecipeService

recipe_router = APIRouter(prefix="/recipes", tags=["recipes"])


@recipe_router.get(
    "",
    response_model=RecipeListResponseDTO,
    summary="Browse seeded recipes",
    description=(
        "Browse or search read-only seeded recipes by name, tag, and maximum "
        "cooking time using deterministic page ordering."
    ),
)
async def get_recipes(
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    filters: Annotated[RecipeListQuery, Depends(get_recipe_list_query)],
) -> RecipeListResponseDTO:
    """Return a stable page of filtered seeded recipe cards."""
    return await service.list_recipes(
        query=filters.query,
        tag=filters.tag,
        max_cooking_minutes=filters.max_cooking_minutes,
        page=filters.page,
        per_page=filters.per_page,
    )


@recipe_router.get(
    "/{recipe_id}",
    response_model=RecipeDetailDTO,
    summary="Read a seeded recipe",
    description=(
        "Return recipe instructions, ingredient requirements, and nutrition scaled "
        "to the optional positive servings query parameter."
    ),
)
async def get_recipe(
    recipe_id: UUID,
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    servings: Annotated[
        Decimal | None, Query(gt=0, max_digits=6, decimal_places=2)
    ] = None,
) -> RecipeDetailDTO:
    """Return one recipe with its serving-scaled public details."""
    return await service.get_recipe(recipe_id, servings)


@recipe_router.post(
    "",
    response_model=RecipeDetailDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recipe",
)
async def create_recipe(
    data: CreateRecipeRequestDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeDetailDTO:
    """Create one recipe as an administrator."""
    return await service.create_recipe(data)


@recipe_router.put(
    "/{recipe_id}",
    response_model=RecipeDetailDTO,
    summary="Update a recipe",
)
async def update_recipe(
    recipe_id: UUID,
    data: UpdateRecipeRequestDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeDetailDTO:
    """Update explicitly supplied fields of one recipe as an administrator."""
    return await service.update_recipe(recipe_id, data)
