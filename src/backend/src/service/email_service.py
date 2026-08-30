"""Template-based email delivery through a local Mailpit SMTP server."""

from collections.abc import Mapping
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
from smtplib import SMTP, SMTPException
from typing import Protocol

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from src.base.constant.template_file_name import EMAIL_TEMPLATE_FILENAMES
from src.core.setting import EMAIL_FROM, EMAIL_SMTP_HOST, EMAIL_SMTP_PORT
from src.service.otp_delivery_service import OTPDeliveryRequest, OTPDeliveryService


class EmailDeliveryError(RuntimeError):
    """Raised when an email cannot be rendered or submitted to SMTP."""


class SMTPTransport(Protocol):
    """Minimal blocking SMTP transport used by the asynchronous email service."""

    def send(self, message: EmailMessage) -> None:
        """Submit a MIME email message to an SMTP server."""
        raise NotImplementedError


class MailpitSMTPTransport:
    """SMTP transport configured for Mailpit or another unauthenticated relay."""

    def __init__(self, host: str, port: int) -> None:
        """Configure SMTP host and port."""
        self._host = host
        self._port = port

    def send(self, message: EmailMessage) -> None:
        """Submit the message to Mailpit without logging its sensitive contents."""
        try:
            with SMTP(self._host, self._port, timeout=5) as client:
                client.send_message(message)
        except (OSError, SMTPException) as error:
            raise EmailDeliveryError("SMTP delivery failed") from error


class EmailService(OTPDeliveryService):
    """Render named HTML templates and submit email through SMTP."""

    def __init__(
        self,
        sender: str = EMAIL_FROM,
        template_directory: Path | None = None,
        transport: SMTPTransport | None = None,
    ) -> None:
        """Configure sender, template directory, and Mailpit SMTP transport."""
        self._sender = sender
        directory = template_directory or Path(__file__).resolve().parent.parent / "template"
        self._environment = Environment(
            loader=FileSystemLoader(directory),
            autoescape=select_autoescape(enabled_extensions=("html",)),
        )
        self._transport = transport or MailpitSMTPTransport(
            EMAIL_SMTP_HOST,
            EMAIL_SMTP_PORT,
        )

    async def send_email(
        self,
        subject: str,
        payload: Mapping[str, object],
        template: str,
    ) -> str:
        """Render a named template and send it to the payload recipient."""
        recipient = self._get_recipient(payload)
        html = self._render_template(template, payload)
        message = self._build_message(subject, recipient, html)
        self._transport.send(message)
        message_id = message["Message-ID"]
        if not isinstance(message_id, str):
            raise EmailDeliveryError("Email message identifier is unavailable")
        return message_id

    async def send_otp(self, request: OTPDeliveryRequest) -> str:
        """Send a purpose-specific OTP email through the common delivery contract."""
        return await self.send_email(
            subject="Sweep Food verification code",
            payload={
                "recipient": request.destination,
                "otp": request.otp,
                "expires_in_minutes": request.expires_in_seconds // 60,
                "correlation_id": request.correlation_id,
            },
            template=request.template_id,
        )

    @staticmethod
    def _get_recipient(payload: Mapping[str, object]) -> str:
        recipient = payload.get("recipient")
        if not isinstance(recipient, str) or not recipient:
            raise ValueError("Email payload requires a non-empty recipient")
        return recipient

    def _render_template(self, template: str, payload: Mapping[str, object]) -> str:
        filename = EMAIL_TEMPLATE_FILENAMES.get(template, template)
        if Path(filename).name != filename or not filename.endswith(".html"):
            raise ValueError("Email template must be an HTML filename in src/template")
        try:
            email_template = self._environment.get_template(filename)
        except TemplateNotFound as error:
            raise ValueError(f"Email template {template} was not found") from error
        return email_template.render(**dict(payload))

    def _build_message(self, subject: str, recipient: str, html: str) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._sender
        message["To"] = recipient
        message["Message-ID"] = make_msgid(domain="sweep-food.local")
        message.set_content("Please view this email in an HTML-capable email client.")
        message.add_alternative(html, subtype="html")
        return message
