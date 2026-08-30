"""Business operations for health-module endpoints."""

from typing import Never

from fastapi import HTTPException, status

from src.base.constant.template_file_name import EMAIL_TEMPLATE_FILENAMES
from src.module.health.health_dto import LivenessResponseDTO
from src.service.email_service import EmailService


class HealthService:
    """Provide basic health responses and a local email-delivery check."""

    def __init__(self, email_service: EmailService) -> None:
        """Store the email service used for the local test endpoint."""
        self._email_service = email_service

    def get_liveness(self) -> LivenessResponseDTO:
        """Return the application's liveness response."""
        return LivenessResponseDTO(
            message="Build with Cloudian 💙 Cloud",
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
