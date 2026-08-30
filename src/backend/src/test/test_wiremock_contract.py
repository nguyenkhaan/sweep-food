"""Contract test for deterministic local provider fixtures."""

from typing import cast

import httpx
import pytest


@pytest.mark.wiremock
def test_wiremock_sms_fixture(
    wiremock_is_available: bool,
    wiremock_http_client: httpx.Client,
) -> None:
    """WireMock serves a deterministic SMS mock response when it is running."""
    if not wiremock_is_available:
        pytest.skip("WireMock is not running at the configured WIREMOCK_URL.")

    response = wiremock_http_client.get("/mock/sms")
    response_body = cast(dict[str, str], response.json())

    assert response.status_code == 200
    assert response_body == {"provider": "mock-sms", "status": "ok"}
