"""Unit tests for provider-independent OTP delivery adapters."""

import json

import httpx
import pytest

from src.core.setting import DEFAULT_OTP
from src.service.otp_delivery_service import (
    OTPDeliveryMalformedResponseError,
    OTPDeliveryRejectedError,
    OTPDeliveryRequest,
    OTPDeliveryTimeoutError,
)
from src.service.sms_service import WireMockSMSService


def _request() -> OTPDeliveryRequest:
    return OTPDeliveryRequest(
        destination="+84901234567",
        template_id="VERIFY_EMAIL",
        otp=DEFAULT_OTP,
        expires_in_seconds=300,
        correlation_id="test-correlation-id",
    )


def _accepted_handler(request: httpx.Request) -> httpx.Response:
    body: object = json.loads(request.content)
    assert request.method == "POST"
    assert request.url.path == "/mock/sms"
    assert isinstance(body, dict)
    assert body["otp"] == DEFAULT_OTP
    return httpx.Response(
        202,
        json={"status": "accepted", "delivery_reference": "mock-sms-accepted"},
    )


def _rejected_handler(_request_value: httpx.Request) -> httpx.Response:
    return httpx.Response(422, json={"status": "rejected"})


def _malformed_handler(_request_value: httpx.Request) -> httpx.Response:
    return httpx.Response(202, content=b"not-json")


def _timeout_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("WireMock timeout", request=request)


@pytest.mark.anyio
async def test_wiremock_sms_service_posts_default_otp() -> None:
    """The local SMS adapter sends the configured default OTP to WireMock."""
    service = WireMockSMSService(
        base_url="https://wiremock.test",
        transport=httpx.MockTransport(_accepted_handler),
    )

    delivery_reference = await service.send_otp(_request())

    assert delivery_reference == "mock-sms-accepted"


@pytest.mark.anyio
async def test_wiremock_sms_service_maps_provider_rejection() -> None:
    """A rejected provider response becomes a stable domain error."""
    service = WireMockSMSService(
        base_url="https://wiremock.test",
        transport=httpx.MockTransport(_rejected_handler),
    )

    with pytest.raises(OTPDeliveryRejectedError):
        await service.send_otp(_request())


@pytest.mark.anyio
async def test_wiremock_sms_service_maps_malformed_response() -> None:
    """A non-JSON provider response becomes a stable domain error."""
    service = WireMockSMSService(
        base_url="https://wiremock.test",
        transport=httpx.MockTransport(_malformed_handler),
    )

    with pytest.raises(OTPDeliveryMalformedResponseError):
        await service.send_otp(_request())


@pytest.mark.anyio
async def test_wiremock_sms_service_maps_provider_timeout() -> None:
    """A provider timeout becomes a stable domain error."""
    service = WireMockSMSService(
        base_url="https://wiremock.test",
        transport=httpx.MockTransport(_timeout_handler),
    )

    with pytest.raises(OTPDeliveryTimeoutError):
        await service.send_otp(_request())
