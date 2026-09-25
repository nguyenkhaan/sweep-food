"""FastAPI dependency construction for rating routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.rating.rating_service import RatingService


async def get_rating_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RatingService:
    """Build the request-scoped rating service."""
    return RatingService(db_session)
