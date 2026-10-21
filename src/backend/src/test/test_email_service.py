"""Unit tests for the template-based Mailpit email service."""

from dataclasses import dataclass, field
from email.message import EmailMessage
from unittest.mock import MagicMock, call

import pytest

from src.service import email_service
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
async def test_send_otp_renders_the_hardcoded_registration_template() -> None:
    """Registration OTP email is a self-contained responsive HTML message."""
    transport = FakeSMTPTransport()
    service = EmailService(transport=transport)

    await service.send_otp(
        OTPDeliveryRequest(
            destination="user@example.test",
            template_id="REGISTER",
            otp="123456",
            expires_in_seconds=300,
            correlation_id="registration-template-test",
        )
    )

    html_part = transport.messages[0].get_body(preferencelist=("html",))
    assert html_part is not None
    rendered_html = html_part.get_content()
    assert "123456" in rendered_html
    assert "background:" in rendered_html
    assert "5 minutes" in rendered_html


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


def test_development_transport_uses_mailpit_without_authentication(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MagicMock()
    connection = MagicMock()
    connection.__enter__.return_value = client
    smtp = MagicMock(return_value=connection)
    monkeypatch.setattr(email_service, "SMTP", smtp)
    monkeypatch.setattr(email_service, "ENV", "dev")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_HOST", "mailpit")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_PORT", 1025)

    email_service.create_smtp_transport().send(EmailMessage())

    smtp.assert_called_once_with("mailpit", 1025, timeout=5)
    client.send_message.assert_called_once()
    client.starttls.assert_not_called()
    client.login.assert_not_called()


def test_production_transport_uses_starttls_and_authentication(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MagicMock()
    connection = MagicMock()
    connection.__enter__.return_value = client
    smtp = MagicMock(return_value=connection)
    monkeypatch.setattr(email_service, "SMTP", smtp)
    monkeypatch.setattr(email_service, "ENV", "production")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_PORT", 587)
    monkeypatch.setattr(email_service, "EMAIL_SMTP_USERNAME", "sender@example.com")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_PASSWORD", "test-secret")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_USE_STARTTLS", True)

    email_service.create_smtp_transport().send(EmailMessage())

    smtp.assert_called_once_with("smtp.gmail.com", 587, timeout=5)
    assert client.mock_calls[0] == call.ehlo()
    assert client.mock_calls[1].args == ()
    assert client.mock_calls[1][0] == "starttls"
    assert client.mock_calls[1].kwargs["context"].verify_mode.name == "CERT_REQUIRED"
    assert client.mock_calls[2] == call.ehlo()
    assert client.mock_calls[3] == call.login("sender@example.com", "test-secret")
    assert client.mock_calls[4][0] == "send_message"


@pytest.mark.parametrize(
    "username,password,starttls",
    [
        ("", "secret", True),
        ("sender@example.com", "", True),
        ("sender@example.com", "secret", False),
    ],
)
def test_production_rejects_insecure_or_missing_smtp_settings(
    monkeypatch: pytest.MonkeyPatch,
    username: str,
    password: str,
    starttls: bool,
) -> None:
    monkeypatch.setattr(email_service, "ENV", "production")
    monkeypatch.setattr(email_service, "EMAIL_SMTP_USERNAME", username)
    monkeypatch.setattr(email_service, "EMAIL_SMTP_PASSWORD", password)
    monkeypatch.setattr(email_service, "EMAIL_SMTP_USE_STARTTLS", starttls)

    with pytest.raises(
        ValueError, match="Production SMTP requires STARTTLS and credentials"
    ):
        email_service.create_smtp_transport()


def test_unknown_environment_does_not_fall_back_to_mailpit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(email_service, "ENV", "stagin")

    with pytest.raises(ValueError, match="Unsupported ENV for email delivery"):
        email_service.create_smtp_transport()
