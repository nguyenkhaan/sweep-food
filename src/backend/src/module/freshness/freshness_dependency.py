"""FastAPI dependencies for FreshCheck routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.freshness.freshness_service import (
    FreshnessAssessmentService,
    FreshnessQuestionService,
)
from src.service.freshcheck_repository import FreshCheckKnowledgeBaseCache

_knowledge_base_cache = FreshCheckKnowledgeBaseCache()


async def get_freshness_questions_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FreshnessQuestionService:
    """Build a request-scoped service sharing immutable snapshots by KB version."""
    return FreshnessQuestionService(session, _knowledge_base_cache)


async def get_freshness_assessment_service(
    session: Annotated[AsyncSession, Depends(get_db_session, use_cache=False)],
) -> FreshnessAssessmentService:
    """Build a request-scoped writer sharing immutable KB snapshots by version."""
    return FreshnessAssessmentService(session, _knowledge_base_cache)
