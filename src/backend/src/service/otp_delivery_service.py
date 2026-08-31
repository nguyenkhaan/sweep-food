"""Shared request and error contracts for OTP delivery providers."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class OTPDeliveryRequest:
    """Sensitive OTP message data passed only to a delivery provider."""

    destination: str
    template_id: str
    otp: str
    expires_in_seconds: int
    correlation_id: str


class OTPDeliveryError(RuntimeError):
    """Base class for stable OTP delivery failures."""

    code = "OTP_DELIVERY_ERROR"


class OTPDeliveryRejectedError(OTPDeliveryError):
    """Raised when a provider explicitly rejects a delivery request."""

    code = "OTP_DELIVERY_REJECTED"


class OTPDeliveryTimeoutError(OTPDeliveryError):
    """Raised when a provider does not respond before the configured timeout."""

    code = "OTP_DELIVERY_TIMEOUT"


class OTPDeliveryMalformedResponseError(OTPDeliveryError):
    """Raised when a provider response does not match the delivery contract."""

    code = "OTP_DELIVERY_MALFORMED_RESPONSE"


class OTPDeliveryRequestError(OTPDeliveryError):
    """Raised when a provider cannot be contacted."""

    code = "OTP_DELIVERY_REQUEST_ERROR"


class OTPDeliveryService(Protocol):
    """Shared delivery boundary for SMS and email providers."""

    async def send_otp(self, request: OTPDeliveryRequest) -> str:
        """Deliver an OTP and return a provider delivery reference."""
        raise NotImplementedError
