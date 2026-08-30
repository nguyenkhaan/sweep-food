"""Tests for the Mailpit email health-check endpoint."""

from email.message import EmailMessage

import httpx
import pytest

from src.app import app
from src.module.health.health_dependency import get_health_service
from src.module.health.health_service import HealthService
from src.service.email_service import EmailService, SMTPTransport


class CapturingSMTPTransport(SMTPTransport):
    """Capture a test email without opening an SMTP connection."""

    def __init__(self) -> None:
        """Initialize the empty message collection."""
        self.messages: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        """Store a submitted MIME message."""
        self.messages.append(message)


@pytest.mark.anyio
async def test_test_email_endpoint_submits_base_template(
    api_client: httpx.AsyncClient,
) -> None:
    """The endpoint submits a base-email template through its service dependency."""
    transport = CapturingSMTPTransport()
    service = HealthService(email_service=EmailService(transport=transport))

    async def get_test_health_service() -> HealthService:
        """Provide the health service with the SMTP-free email transport."""
        return service

    app.dependency_overrides[get_health_service] = get_test_health_service
    try:
        response = await api_client.post("/api/health/test-email")
    finally:
        app.dependency_overrides.pop(get_health_service, None)

    assert response.status_code == 202
    assert response.json()["message"] == "Test email submitted"
    assert response.json()["message_id"]
    assert len(transport.messages) == 1
    html_part = transport.messages[0].get_body(preferencelist=("html",))
    assert html_part is not None
    assert "If you did not request this action" in html_part.get_content()
