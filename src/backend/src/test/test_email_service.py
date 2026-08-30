"""Unit tests for the template-based Mailpit email service."""

from dataclasses import dataclass, field
from email.message import EmailMessage

import pytest

from src.service.email_service import EmailService, SMTPTransport
from src.service.otp_delivery_service import OTPDeliveryRequest


@dataclass
class FakeSMTPTransport(SMTPTransport):
    """Capture submitted messages without creating an SMTP connection."""

    messages: list[EmailMessage] = field(default_factory=list)

    def send(self, message: EmailMessage) -> None:
        """Record a submitted email message."""
        self.messages.append(message)


@pytest.mark.anyio
async def test_send_email_renders_verify_template_and_submits_message() -> None:
    """A verification email is rendered as HTML and handed to the transport."""
    transport = FakeSMTPTransport()
    service = EmailService(sender="noreply@sweep-food.local", transport=transport)

    message_id = await service.send_email(
        subject="Verify your Sweep Food email",
        payload={
            "recipient": "user@example.test",
            "recipient_name": "An",
            "otp": "123456",
            "expires_in_minutes": 5,
        },
        template="VERIFY_EMAIL",
    )

    assert message_id
    assert len(transport.messages) == 1
    message = transport.messages[0]
    assert message["To"] == "user@example.test"
    assert message["From"] == "noreply@sweep-food.local"
    assert str(message["Subject"]) == "Verify your Sweep Food email"
    html_part = message.get_body(preferencelist=("html",))
    assert html_part is not None
    assert "123456" in html_part.get_content()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "template",
    [
        "VERIFY_EMAIL",
        "CHANGE_EMAIL",
        "CHANGE_PHONE",
        "RESET_PASSWORD",
        "CHANGE_PASSWORD",
        "STEP_UP_AUTH",
    ],
)
async def test_send_email_supports_each_documented_template(template: str) -> None:
    """Every documented email purpose resolves to a renderable template."""
    transport = FakeSMTPTransport()
    service = EmailService(transport=transport)

    await service.send_email(
        subject="Sweep Food",
        payload={
            "recipient": "user@example.test",
            "recipient_name": "<script>alert('xss')</script>",
            "otp": "123456",
            "expires_in_minutes": 5,
        },
        template=template,
    )

    html_part = transport.messages[0].get_body(preferencelist=("html",))
    assert html_part is not None
    assert "123456" in html_part.get_content()


@pytest.mark.anyio
async def test_send_email_autoescapes_template_values() -> None:
    """Template values cannot introduce executable HTML into an email."""
    transport = FakeSMTPTransport()
    service = EmailService(transport=transport)

    await service.send_email(
        subject="Sweep Food",
        payload={
            "recipient": "user@example.test",
            "recipient_name": "<script>alert('xss')</script>",
            "otp": "123456",
            "expires_in_minutes": 5,
        },
        template="VERIFY_EMAIL",
    )

    html_part = transport.messages[0].get_body(preferencelist=("html",))
    assert html_part is not None
    rendered_html = html_part.get_content()
    assert "&lt;script&gt;" in rendered_html
    assert "<script>" not in rendered_html


@pytest.mark.anyio
async def test_send_otp_uses_the_shared_delivery_contract() -> None:
    """OTP delivery can use the EMAIL purpose name from the shared contract."""
    transport = FakeSMTPTransport()
    service = EmailService(transport=transport)
    request = OTPDeliveryRequest(
        destination="user@example.test",
        template_id="VERIFY_EMAIL",
        otp="123456",
        expires_in_seconds=300,
        correlation_id="email-service-test",
    )

    await service.send_otp(request)

    assert "123456" in transport.messages[0].as_string()


@pytest.mark.anyio
async def test_send_email_requires_a_recipient_and_known_template() -> None:
    """Invalid routing information is rejected before SMTP is called."""
    service = EmailService(transport=FakeSMTPTransport())

    with pytest.raises(ValueError, match="recipient"):
        await service.send_email(
            subject="Sweep Food",
            payload={},
            template="VERIFY_EMAIL",
        )
    with pytest.raises(ValueError, match="was not found"):
        await service.send_email(
            subject="Sweep Food",
            payload={"recipient": "user@example.test"},
            template="missing.html",
        )
