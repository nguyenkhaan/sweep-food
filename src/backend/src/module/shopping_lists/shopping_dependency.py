"""Dependencies for shopping-list routes."""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.inventory.inventory_dependency import get_inventory_service
from src.module.inventory.inventory_service import InventoryService
from src.module.shopping_lists.shopping_service import ShoppingService


@dataclass(frozen=True, slots=True)
class ShoppingItemPath:
    """Collect the two path identifiers for a shopping-item mutation."""

    list_id: UUID
    item_id: UUID


async def get_shopping_item_path(
    list_id: UUID, item_id: UUID
) -> ShoppingItemPath:
    """Retain named OpenAPI path parameters in one typed route value."""
    return ShoppingItemPath(list_id=list_id, item_id=item_id)


async def get_shopping_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    inventory_service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> ShoppingService:
    """Build the request-scoped shopping service sharing the inventory session."""
    return ShoppingService(db_session, inventory_service)
