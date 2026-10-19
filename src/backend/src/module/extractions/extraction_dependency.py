"""Dependencies for extraction endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from AI.extraction.service import get_ai_extraction_service
from src.db import get_db_session
from src.module.extractions.extraction_service import ExtractionService


def get_extraction_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExtractionService:
    """Create an extraction service backed by in-process AI extraction service."""
    return ExtractionService(session, ai_service=get_ai_extraction_service())
