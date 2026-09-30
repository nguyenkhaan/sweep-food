"""Dependencies for extraction endpoints."""

from typing import Annotated

from fastapi import Depends

from src.module.extractions.extraction_service import ExtractionService
from src.service.sweep_food_ai_client import (
    SweepFoodAIClient,
    get_sweep_food_ai_client,
)


async def get_extraction_service(
    ai_client: Annotated[SweepFoodAIClient, Depends(get_sweep_food_ai_client)],
) -> ExtractionService:
    """Create an extraction service backed by the request-scoped AI client."""
    return ExtractionService(ai_client)
