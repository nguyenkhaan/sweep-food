"""Dependencies for recommendation routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.recommendations.recommendation_ai_service import RecommendationAIService
from src.service.sweep_food_ai_client import (
    SweepFoodAIClient,
    get_sweep_food_ai_client,
)


async def get_recommendation_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    ai_client: Annotated[SweepFoodAIClient, Depends(get_sweep_food_ai_client)],
) -> RecommendationAIService:
    """Build the request-scoped AI recommendation service."""
    return RecommendationAIService(db_session, ai_client)
