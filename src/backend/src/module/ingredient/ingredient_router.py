"""Catalog management and user inventory storage routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.module.catalog.catalog_dto import IngredientDetailDTO
from src.module.ingredient.ingredient_dependency import get_ingredient_service
from src.module.ingredient.ingredient_dto import (
    AssignIngredientCategoryDTO,
    UpdateIngredientDefaultStorageDTO,
    UpdateIngredientDTO,
)
from src.module.ingredient.ingredient_service import IngredientService
from src.module.inventory.inventory_dto import (
    InventoryBatchDTO,
    MoveInventoryBatchRequestDTO,
)

ingredient_router = APIRouter(tags=["ingredient-management"])


@ingredient_router.patch(
    "/ingredients/{ingredient_id}", response_model=IngredientDetailDTO
)
async def patch_ingredient(
    ingredient_id: UUID,
    body: UpdateIngredientDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientDetailDTO:
    """Update mutable fields of one master ingredient."""
    return await service.update_ingredient(ingredient_id, body)


@ingredient_router.delete(
    "/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_ingredient(
    ingredient_id: UUID,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> Response:
    """Delete an unreferenced master ingredient."""
    await service.delete_ingredient(ingredient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@ingredient_router.patch(
    "/ingredients/{ingredient_id}/default-storage-mode",
    response_model=IngredientDetailDTO,
)
async def patch_default_storage_mode(
    ingredient_id: UUID,
    body: UpdateIngredientDefaultStorageDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientDetailDTO:
    """Change the catalog's suggested storage mode."""
    return await service.update_default_storage(ingredient_id, body)


@ingredient_router.patch(
    "/ingredients/{ingredient_id}/category", response_model=IngredientDetailDTO
)
async def patch_ingredient_category(
    ingredient_id: UUID,
    body: AssignIngredientCategoryDTO,
    _admin: Annotated[AuthenticatedUser, Depends(require_role(UserRole.ADMIN))],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
) -> IngredientDetailDTO:
    """Assign one existing category to a master ingredient."""
    return await service.update_category(ingredient_id, body)


@ingredient_router.patch(
    "/ingredients/inventory-batches/{batch_id}/storage-mode",
    response_model=InventoryBatchDTO,
)
async def patch_inventory_storage_mode(
    batch_id: UUID,
    body: MoveInventoryBatchRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[IngredientService, Depends(get_ingredient_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> InventoryBatchDTO:
    """Move an owned batch and update its estimated expiration if appropriate."""
    return await service.move_inventory_batch(
        user.user_id, batch_id, body, idempotency_key
    )
