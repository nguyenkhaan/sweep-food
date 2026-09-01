"""FastAPI dependencies for inventory endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.setting import get_positive_int_env
from src.db import get_db_session
from src.module.inventory.inventory_service import InventoryService


async def get_inventory_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> InventoryService:
    """Build the request-scoped inventory service."""
    return InventoryService(
        db_session,
        warning_days=get_positive_int_env("NOTIFICATION_DEFAULT_WARNING_DAYS", 3),
    )
