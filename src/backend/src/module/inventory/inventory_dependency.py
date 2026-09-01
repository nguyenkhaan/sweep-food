"""Dependencies for manual inventory batch routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.inventory.inventory_service import InventoryService


async def get_inventory_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InventoryService:
    """Build the request-scoped manual inventory service."""
    return InventoryService(db_session)
