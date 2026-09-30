"""Dependencies used by health-module endpoints."""

from typing import Annotated

from fastapi import Depends

from src.module.health.health_service import HealthService
from src.service.email_service import EmailService
from src.service.sweep_food_ai_client import (
    SweepFoodAIClient,
    get_sweep_food_ai_client,
)


async def get_email_service() -> EmailService:
    """Create the template-based email service used by the test endpoint."""
    return EmailService()


async def get_health_service(
    email_service: Annotated[EmailService, Depends(get_email_service)],
    ai_client: Annotated[SweepFoodAIClient, Depends(get_sweep_food_ai_client)],
) -> HealthService:
    """Create the health service with its endpoint dependencies."""
    return HealthService(email_service=email_service, ai_client=ai_client)
