from hashlib import sha256

from src.service.otp_delivery_service import OTPDeliveryRequest, OTPDeliveryService


class MockEmailService(OTPDeliveryService):
    """Return deterministic delivery references without sending an email."""

    async def send_otp(self, request: OTPDeliveryRequest) -> str:
        """Accept an OTP request without logging or delivering its OTP value."""
        return f"mock-email-{sha256(request.correlation_id.encode()).hexdigest()}"
