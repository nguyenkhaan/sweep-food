"""Dependencies used by health-module endpoints."""

from typing import Annotated

from fastapi import Depends

from src.module.health.health_service import HealthService
from src.service.email_service import EmailService


async def get_email_service() -> EmailService:
    """Create the template-based email service used by the test endpoint."""
    return EmailService()


async def get_health_service(
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> HealthService:
    """Create the health service with its email dependency."""
    return HealthService(email_service=email_service)
