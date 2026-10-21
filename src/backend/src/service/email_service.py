"""Template-based email delivery through development or production SMTP."""

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
from smtplib import SMTP, SMTPException
from ssl import create_default_context
from typing import Protocol

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from src.base.constant.template_file_name import EMAIL_TEMPLATE_FILENAMES
from src.core.setting import (
    EMAIL_FROM,
    EMAIL_SMTP_HOST,
    EMAIL_SMTP_PASSWORD,
    EMAIL_SMTP_PORT,
    EMAIL_SMTP_USE_STARTTLS,
    EMAIL_SMTP_USERNAME,
    ENV,
)
from src.service.otp_delivery_service import OTPDeliveryRequest, OTPDeliveryService

REGISTRATION_TEMPLATE_ID = "REGISTER"


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


@dataclass(frozen=True, slots=True)
class SMTPCredentials:
    username: str
    password: str


class AuthenticatedSMTPTransport:
    """Deliver email through a TLS-protected, authenticated SMTP server."""

    def __init__(self, host: str, port: int, credentials: SMTPCredentials) -> None:
        self._host = host
        self._port = port
        self._credentials = credentials

    def send(self, message: EmailMessage) -> None:
        try:
            with SMTP(self._host, self._port, timeout=5) as client:
                client.ehlo()
                client.starttls(context=create_default_context())
                client.ehlo()
                client.login(self._credentials.username, self._credentials.password)
                client.send_message(message)
        except (OSError, SMTPException) as error:
            raise EmailDeliveryError("SMTP delivery failed") from error


def create_smtp_transport() -> SMTPTransport:
    """Choose Mailpit in development and encrypted SMTP in production."""
    environment = ENV.strip().lower()
    if environment in {"dev", "development", "test"}:
        return MailpitSMTPTransport(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT)
    if environment in {"production", "prod"}:
        if not (
            EMAIL_SMTP_USE_STARTTLS
            and EMAIL_SMTP_USERNAME.strip()
            and EMAIL_SMTP_PASSWORD
        ):
            raise ValueError("Production SMTP requires STARTTLS and credentials")
        return AuthenticatedSMTPTransport(
            EMAIL_SMTP_HOST,
            EMAIL_SMTP_PORT,
            SMTPCredentials(EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD),
        )
    raise ValueError("Unsupported ENV for email delivery")


class EmailService(OTPDeliveryService):
    """Render named HTML templates and submit email through SMTP."""

    def __init__(
        self,
        sender: str = EMAIL_FROM,
        template_directory: Path | None = None,
        transport: SMTPTransport | None = None,
    ) -> None:
        """Configure sender, template directory, and environment SMTP transport."""
        self._sender = sender
        directory = (
            template_directory or Path(__file__).resolve().parent.parent / "template"
        )
        self._environment = Environment(
            loader=FileSystemLoader(directory),
            autoescape=select_autoescape(enabled_extensions=("html",)),
        )
        self._transport = (
            transport if transport is not None else create_smtp_transport()
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
        await asyncio.to_thread(self._transport.send, message)
        message_id = message["Message-ID"]
        if not isinstance(message_id, str):
            raise EmailDeliveryError("Email message identifier is unavailable")
        return message_id

    async def send_otp(self, request: OTPDeliveryRequest) -> str:
        """Send a purpose-specific OTP email through the common delivery contract."""
        return await self.send_email(
            subject=self._get_otp_subject(request.template_id),
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
        if template == REGISTRATION_TEMPLATE_ID:
            return self._render_registration_otp_template(payload)
        filename = EMAIL_TEMPLATE_FILENAMES.get(template, template)
        if Path(filename).name != filename or not filename.endswith(".html"):
            raise ValueError("Email template must be an HTML filename in src/template")
        try:
            email_template = self._environment.get_template(filename)
        except TemplateNotFound as error:
            raise ValueError(f"Email template {template} was not found") from error
        return email_template.render(**dict(payload))

    @staticmethod
    def _get_otp_subject(template_id: str) -> str:
        if template_id == REGISTRATION_TEMPLATE_ID:
            return "Verify your Sweep Food account"
        return "Sweep Food verification code"

    @staticmethod
    def _render_registration_otp_template(payload: Mapping[str, object]) -> str:
        otp = payload.get("otp")
        expires_in_minutes = payload.get("expires_in_minutes")
        if not isinstance(otp, str) or len(otp) != 6 or not otp.isdigit():
            raise ValueError("Registration email requires a six-digit OTP")
        if (
            not isinstance(expires_in_minutes, int)
            or isinstance(expires_in_minutes, bool)
            or expires_in_minutes <= 0
        ):
            raise ValueError("Registration email requires a positive expiration time")
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Verify your Sweep Food account</title>
  </head>
  <body style="margin:0;background:#f1f5f9;font-family:Arial,sans-serif;color:#0f172a;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f1f5f9;padding:32px 16px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 12px 32px rgba(15,23,42,.12);">
          <tr><td style="background:linear-gradient(135deg,#16a34a,#0f766e);padding:32px;color:#ffffff;">
            <div style="font-size:24px;font-weight:700;">Sweep Food</div>
            <div style="margin-top:8px;font-size:16px;opacity:.92;">Verify your new account</div>
          </td></tr>
          <tr><td style="padding:36px 32px;">
            <h1 style="margin:0 0 14px;font-size:24px;line-height:1.3;">Your verification code</h1>
            <p style="margin:0 0 24px;font-size:16px;line-height:1.6;color:#475569;">Enter this code to complete your Sweep Food registration. It expires in {expires_in_minutes} minutes.</p>
            <div style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:14px;padding:18px;text-align:center;font-family:monospace;font-size:32px;font-weight:700;letter-spacing:8px;color:#047857;">{otp}</div>
            <p style="margin:24px 0 0;font-size:13px;line-height:1.5;color:#64748b;">Do not share this code. If you did not create a Sweep Food account, you can safely ignore this email.</p>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""

    def _build_message(self, subject: str, recipient: str, html: str) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._sender
        message["To"] = recipient
        message["Message-ID"] = make_msgid(domain="sweep-food.local")
        message.set_content("Please view this email in an HTML-capable email client.")
        message.add_alternative(html, subtype="html")
        return message
