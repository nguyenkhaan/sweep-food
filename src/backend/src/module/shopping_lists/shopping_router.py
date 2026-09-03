"""Authenticated shopping-list routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.shopping_lists.shopping_dependency import (
    ShoppingItemPath,
    get_shopping_item_path,
    get_shopping_service,
)
from src.module.shopping_lists.shopping_dto import (
    CreateShoppingItemRequestDTO,
    GenerateShoppingListRequestDTO,
    ShoppingListDTO,
    ShoppingListItemDTO,
    UpdateShoppingListItemRequestDTO,
)
from src.module.shopping_lists.shopping_service import ShoppingService

shopping_router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


@shopping_router.post(
    "/generate", response_model=ShoppingListDTO, status_code=status.HTTP_201_CREATED
)
async def post_shopping_list_generation(
    body: GenerateShoppingListRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> ShoppingListDTO:
    """Generate the active shopping list for one owned meal plan."""
    return await service.generate(user.user_id, body, idempotency_key)


@shopping_router.get("/{list_id}", response_model=ShoppingListDTO)
async def get_shopping_list(
    list_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
) -> ShoppingListDTO:
    """Read one owned shopping list and its source metadata."""
    return await service.get(user.user_id, list_id)


@shopping_router.post(
    "/{list_id}/items",
    response_model=ShoppingListItemDTO,
    status_code=status.HTTP_201_CREATED,
)
async def post_shopping_list_item(
    list_id: UUID,
    body: CreateShoppingItemRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> ShoppingListItemDTO:
    """Add an unchecked manual item without creating inventory."""
    return await service.add_item(user.user_id, list_id, body, idempotency_key)


@shopping_router.patch("/{list_id}/items/{item_id}", response_model=ShoppingListItemDTO)
async def patch_shopping_list_item(
    path: Annotated[ShoppingItemPath, Depends(get_shopping_item_path)],
    body: UpdateShoppingListItemRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> ShoppingListItemDTO:
    """Edit a manual item or atomically add a purchased item to inventory."""
    return await service.update_item(
        user.user_id, path.list_id, path.item_id, body, idempotency_key
    )


@shopping_router.delete(
    "/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_shopping_list_item(
    list_id: UUID,
    item_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ShoppingService, Depends(get_shopping_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
) -> Response:
    """Remove an unchecked manual reminder from an active shopping list."""
    await service.remove_item(user.user_id, list_id, item_id, idempotency_key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
