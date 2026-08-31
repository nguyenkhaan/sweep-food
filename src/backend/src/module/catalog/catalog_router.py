"""Authenticated, read-only master-ingredient catalog routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.catalog.catalog_dependency import get_catalog_service
from src.module.catalog.catalog_dto import (
    IngredientDetailDTO,
    IngredientListResponseDTO,
)
from src.module.catalog.catalog_service import CatalogService

catalog_router = APIRouter(prefix="/ingredients", tags=["catalog"])


@catalog_router.get(
    "",
    response_model=IngredientListResponseDTO,
    summary="Search master ingredients",
    description=(
        "Search the authenticated catalog by canonical name or seeded alias, with "
        "optional category filtering and deterministic page ordering."
    ),
)
async def get_ingredients(
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    q: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> IngredientListResponseDTO:
    """Return a stable page of canonical ingredient search results."""
    return await service.list_ingredients(
        query=q,
        category=category,
        page=page,
        per_page=per_page,
    )


@catalog_router.get(
    "/{ingredient_id}",
    response_model=IngredientDetailDTO,
    summary="Read a master ingredient",
    description="Return one seeded master ingredient, its aliases, nutrition, and rules.",
)
async def get_ingredient(
    ingredient_id: UUID,
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> IngredientDetailDTO:
    """Return complete public catalog details for one ingredient."""
    return await service.get_ingredient(ingredient_id)
