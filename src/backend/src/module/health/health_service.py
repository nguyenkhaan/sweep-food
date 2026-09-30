"""Business operations for health-module endpoints."""

from time import perf_counter
from typing import Never

from fastapi import HTTPException, status

from src.base.constant.template_file_name import EMAIL_TEMPLATE_FILENAMES
from src.module.health.health_dto import AIServiceHealthResponseDTO, LivenessResponseDTO
from src.service.email_service import EmailService
from src.service.sweep_food_ai_client import (
    SweepFoodAIClient,
    SweepFoodAIUnavailableError,
)


class HealthService:
    """Provide basic health responses and a local email-delivery check."""

    def __init__(
        self, email_service: EmailService, ai_client: SweepFoodAIClient | None = None
    ) -> None:
        """Store the endpoint service dependencies."""
        self._email_service = email_service
        self._ai_client = ai_client

    def get_liveness(self) -> LivenessResponseDTO:
        """Return the application's liveness response."""
        return LivenessResponseDTO(
            message="Build with Cloudian 💙 Cloud",
        )

    async def get_ai_readiness(self) -> AIServiceHealthResponseDTO:
        """Return readiness only when the AI service has finished warming up."""
        if self._ai_client is None:
            raise SweepFoodAIUnavailableError("AI client is not configured")

        started_at = perf_counter()
        health = await self._ai_client.check_health()
        if not health.warmed_up:
            raise SweepFoodAIUnavailableError("AI service is still warming up")

        return AIServiceHealthResponseDTO(
            latency_ms=round((perf_counter() - started_at) * 1_000, 2),
        )

    def raise_forced_error(self) -> Never:
        """Raise the deliberate error used by the common-error smoke test."""
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Forced health error.",
        )

    def get_text(self) -> str:
        """Return the legacy plain-text health response."""
        return "Build with Cloudian Love Cloud"

    async def send_test_email(self) -> str:
        """Send a basic rendered email to Mailpit's local test inbox."""
        return await self._email_service.send_email(
            subject="Sweep Food email service test",
            payload={"recipient": "mailpit-test@sweep-food.local"},
            template=EMAIL_TEMPLATE_FILENAMES["BASE_EMAIL"],
        )
