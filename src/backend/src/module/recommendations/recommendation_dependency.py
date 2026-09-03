"""Dependencies for recommendation routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.recommendations.recommendation_service import RecommendationService


async def get_recommendation_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RecommendationService:
    """Build the request-scoped mock recommendation service."""
    return RecommendationService(db_session)
