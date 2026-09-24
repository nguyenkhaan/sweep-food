"""Authenticated ingredient-category routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.module.category.category_dependency import get_category_service
from src.module.category.category_dto import (
    CategoryDTO,
    CreateCategoryRequestDTO,
    UpdateCategoryRequestDTO,
)
from src.module.category.category_service import CategoryService

category_router = APIRouter(prefix="/categories", tags=["categories"])


@category_router.post(
    "",
    response_model=CategoryDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    body: CreateCategoryRequestDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryDTO:
    """Create an ingredient category as an administrator."""
    return await service.create_category(body)


@category_router.get("", response_model=list[CategoryDTO])
async def list_categories(
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryDTO]:
    """List all ingredient categories for an authenticated user."""
    return await service.list_categories()


@category_router.patch("/{category_id}", response_model=CategoryDTO)
async def update_category(
    category_id: UUID,
    body: UpdateCategoryRequestDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryDTO:
    """Update an ingredient category as an administrator."""
    return await service.update_category(category_id, body)


@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: UUID,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> Response:
    """Hard-delete an unreferenced ingredient category."""
    await service.delete_category(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
