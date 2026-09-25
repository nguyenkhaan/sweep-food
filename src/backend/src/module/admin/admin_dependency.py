"""FastAPI dependencies for administrator endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.admin.admin_service import AdminService


async def get_admin_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AdminService:
    """Build the request-scoped administrator service."""
    return AdminService(db_session)
