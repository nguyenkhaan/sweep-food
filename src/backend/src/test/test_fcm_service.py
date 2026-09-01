"""Tests for Firebase Cloud Messaging delivery abstraction."""

import httpx
import pytest
from firebase_admin import exceptions as firebase_exceptions
from firebase_admin import messaging

from src.service.fcm_service import (
    FCMDeliveryResult,
    FCMInvalidTokenError,
    FCMPermanentError,
    FCMRetryableError,
    FCMService,
    WireMockFCMClient,
    map_firebase_error,
)


class FakeFirebaseMessagingClient:
    """Capture messages or raise a configured provider-domain failure."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.messages: list[messaging.Message] = []

    def send(self, message: messaging.Message) -> str:
        """Return a fake provider message ID or raise the configured error."""
        self.messages.append(message)
        if self.error is not None:
            raise self.error
        return "projects/sweep-food/messages/test-message-id"


@pytest.mark.anyio
async def test_fcm_service_sends_notification_and_string_data_payload() -> None:
    """FCM receives the target token, visible content, and string-only data."""
    client = FakeFirebaseMessagingClient()
    service = FCMService(client)

    result = await service.send_to_device(
        token="android-registration-token-123456789",
        title="Food expires soon",
        body="Milk expires tomorrow.",
        data={"batch_id": "batch-1", "days_remaining": 1},
    )

    assert result == FCMDeliveryResult(
        message_id="projects/sweep-food/messages/test-message-id"
    )
    message = client.messages[0]
    assert message.token == "android-registration-token-123456789"
    assert message.fid is None
    assert message.notification is not None
    assert message.notification.title == "Food expires soon"
    assert message.data == {"batch_id": "batch-1", "days_remaining": "1"}


@pytest.mark.anyio
async def test_fcm_service_sends_web_notification() -> None:
    """FCM receives a Web Push notification for a browser device token."""
    client = FakeFirebaseMessagingClient()
    service = FCMService(client)

    result = await service.send_web_notification(
        token="web-registration-token-123456789",
        title="Food expires soon",
        body="Milk expires tomorrow.",
        data={"batch_id": "batch-1"},
    )

    assert result.message_id == "projects/sweep-food/messages/test-message-id"
    message = client.messages[0]
    assert message.token == "web-registration-token-123456789"
    assert message.fid is None
    assert message.webpush is not None
    assert message.webpush.notification is not None
    assert message.webpush.notification.title == "Food expires soon"
    assert message.webpush.notification.body == "Milk expires tomorrow."
    assert message.data == {"batch_id": "batch-1"}


@pytest.mark.anyio
async def test_fcm_service_preserves_invalid_token_outcome() -> None:
    """Invalid tokens remain distinguishable so the worker can disable devices."""
    client = FakeFirebaseMessagingClient(FCMInvalidTokenError())
    service = FCMService(client)

    with pytest.raises(FCMInvalidTokenError):
        await service.send_to_device(
            token="invalid-android-registration-token",
            title="Expired",
            body="Milk expired.",
            data={},
        )


@pytest.mark.anyio
async def test_fcm_service_preserves_retryable_provider_outcome() -> None:
    """Transient provider failures remain retryable by the ARQ worker."""
    client = FakeFirebaseMessagingClient(FCMRetryableError())
    service = FCMService(client)

    with pytest.raises(FCMRetryableError):
        await service.send_to_device(
            token="android-registration-token-123456789",
            title="Expired",
            body="Milk expired.",
            data={},
        )


def test_firebase_error_mapping_distinguishes_delivery_outcomes() -> None:
    """SDK exceptions map to invalid, retryable, or permanent domain outcomes."""
    assert isinstance(
        map_firebase_error(messaging.UnregisteredError("unregistered")),
        FCMInvalidTokenError,
    )
    assert isinstance(
        map_firebase_error(firebase_exceptions.UnavailableError("unavailable")),
        FCMRetryableError,
    )
    assert isinstance(
        map_firebase_error(messaging.SenderIdMismatchError("sender mismatch")),
        FCMPermanentError,
    )


def build_wiremock_message() -> messaging.Message:
    """Build one message used to exercise the local provider contract."""
    return messaging.Message(
        token="android-registration-token-123456789",
        notification=messaging.Notification(title="Expiry", body="Milk expires."),
        data={"batch_id": "batch-1"},
    )


def test_wiremock_fcm_client_returns_provider_message_id() -> None:
    """The local adapter accepts the deterministic WireMock success envelope."""

    def handle(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(202, json={"message_id": "mock-fcm-message-id"})

    client = WireMockFCMClient(
        "http://wiremock.test",
        timeout_seconds=2,
        transport=httpx.MockTransport(handle),
    )

    assert client.send(build_wiremock_message()) == "mock-fcm-message-id"


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (404, FCMInvalidTokenError),
        (429, FCMRetryableError),
        (503, FCMRetryableError),
        (400, FCMPermanentError),
    ],
)
def test_wiremock_fcm_client_maps_http_delivery_outcomes(
    status_code: int,
    expected_error: type[Exception],
) -> None:
    """Local HTTP failures use the same domain outcomes as Firebase Admin."""

    def handle(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"status": "failed"})

    client = WireMockFCMClient(
        "http://wiremock.test",
        timeout_seconds=2,
        transport=httpx.MockTransport(handle),
    )

    with pytest.raises(expected_error):
        client.send(build_wiremock_message())
