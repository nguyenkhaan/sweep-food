"""Contract test for deterministic local provider fixtures."""

from typing import cast

import httpx
import pytest

from src.core.setting import DEFAULT_OTP


@pytest.mark.wiremock
def test_wiremock_sms_fixture(
    wiremock_is_available: bool,
    wiremock_http_client: httpx.Client,
) -> None:
    """WireMock serves a deterministic SMS mock response when it is running."""
    if not wiremock_is_available:
        pytest.skip("WireMock is not running at the configured WIREMOCK_URL.")

    response = wiremock_http_client.post(
        "/mock/sms",
        json={
            "destination": "+84901234567",
            "template_id": "register",
            "otp": DEFAULT_OTP,
            "expires_in_seconds": 300,
            "correlation_id": "wiremock-contract-test",
        },
    )
    assert response.status_code == 202
    response_body = cast(dict[str, str], response.json())
    assert response_body == {
        "provider": "mock-sms",
        "status": "accepted",
        "delivery_reference": "mock-sms-accepted",
        "otp": "123456",
    }


@pytest.mark.wiremock
def test_wiremock_fcm_fixtures(
    wiremock_is_available: bool,
    wiremock_http_client: httpx.Client,
) -> None:
    """WireMock exposes deterministic success and failure FCM responses."""
    if not wiremock_is_available:
        pytest.skip("WireMock is not running at the configured WIREMOCK_URL.")

    def send(fid: str) -> httpx.Response:
        return wiremock_http_client.post(
            "/mock/fcm",
            json={
                "message": {
                    "fid": fid,
                    "notification": {"title": "Expiry", "body": "Milk expires."},
                    "data": {"batch_id": "batch-1"},
                }
            },
        )

    assert send("valid-fcm-token").status_code == 202
    assert send("invalid-fcm-token").status_code == 404
    assert send("retryable-fcm-token").status_code == 503
    assert send("permanent-fcm-token").status_code == 400
