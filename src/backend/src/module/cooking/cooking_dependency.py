"""FastAPI dependencies for cooking preview endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.cooking.cooking_service import CookingService
from src.service.fefo_service import FEFOService


async def get_cooking_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CookingService:
    """Create the request-scoped cooking service and its FEFO dependency."""
    return CookingService(db_session=db_session, fefo_service=FEFOService())
