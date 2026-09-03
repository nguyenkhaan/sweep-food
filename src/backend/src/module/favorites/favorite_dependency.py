"""Dependencies for recipe favourite routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.favorites.favorite_service import FavoriteService


async def get_favorite_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FavoriteService:
    """Build the request-scoped favourite service."""
    return FavoriteService(db_session)
