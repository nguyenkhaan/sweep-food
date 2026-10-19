"""Dependencies for recommendation routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from AI.catalog.snapshot import get_catalog_snapshot
from AI.recommendation.engine import RecommendationEngine
from src.core.setting import AI_MODEL_PATH
from src.db import get_db_session
from src.module.recommendations.recommendation_ai_service import (
    RecommendationAIService,
)

_ENGINE_CACHE: RecommendationEngine | None = None


async def get_recommendation_engine(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RecommendationEngine:
    """Provide or build the recommendation engine backed by the cached catalog snapshot."""
    global _ENGINE_CACHE
    snapshot = await get_catalog_snapshot(db_session)
    if _ENGINE_CACHE is None or _ENGINE_CACHE.snapshot.revision != snapshot.revision:
        _ENGINE_CACHE = RecommendationEngine(snapshot, model_path=AI_MODEL_PATH)
    return _ENGINE_CACHE


async def get_recommendation_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    engine: Annotated[RecommendationEngine, Depends(get_recommendation_engine)],
) -> RecommendationAIService:
    """Build the request-scoped recommendation service."""
    return RecommendationAIService(db_session, engine)
