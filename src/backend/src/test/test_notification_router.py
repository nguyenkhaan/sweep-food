"""API contract tests for Android devices and in-app notifications."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    DevicePlatform,
    NotificationDeliveryStatus,
    NotificationStatus,
    NotificationType,
    UserRole,
)
from src.module.notification.notification_dependency import (
    get_notification_service,
    get_production_fcm_service,
)
from src.module.notification.notification_dto import (
    DeviceRegistrationResponseDTO,
    NotificationListResponseDTO,
    NotificationResponseDTO,
)
from src.service.fcm_service import FCMDeliveryResult

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")
DEVICE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aacc")
NOTIFICATION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aadd")
NOW = datetime(2026, 8, 31, 8, 0, tzinfo=UTC)


class FakeNotificationService:
    """Return deterministic API results without database or Firebase access."""

    async def register_device(
        self,
        _user_id: UUID,
        _request: object,
    ) -> DeviceRegistrationResponseDTO:
        """Return an enabled Android device registration."""
        return DeviceRegistrationResponseDTO(
            device_id=DEVICE_ID,
            platform=DevicePlatform.ANDROID,
            is_enabled=True,
            last_seen_at=NOW,
        )

    async def disable_device(self, _user_id: UUID, _device_id: UUID) -> None:
        """Accept an owned device disable request."""

    async def list_notifications(
        self,
        _user_id: UUID,
        limit: int,
        before: datetime | None,
    ) -> NotificationListResponseDTO:
        """Return one in-app notification."""
        del limit, before
        return NotificationListResponseDTO(items=[build_notification_response()])

    async def update_notification(
        self,
        _user_id: UUID,
        _notification_id: UUID,
        _request: object,
    ) -> NotificationResponseDTO:
        """Return the updated notification."""
        return build_notification_response(status=NotificationStatus.READ)


class FakeProductionFCMService:
    """Return deterministic Firebase message identifiers without network calls."""

    async def send_to_device(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict[str, object],
    ) -> FCMDeliveryResult:
        """Accept an Android direct-delivery request."""
        del token, title, body, data
        return FCMDeliveryResult(message_id="android-message-id")

    async def send_web_notification(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict[str, object],
    ) -> FCMDeliveryResult:
        """Accept a web direct-delivery request."""
        del token, title, body, data
        return FCMDeliveryResult(message_id="web-message-id")


def build_notification_response(
    status: NotificationStatus = NotificationStatus.UNREAD,
) -> NotificationResponseDTO:
    """Build one deterministic in-app notification response."""
    return NotificationResponseDTO(
        notification_id=NOTIFICATION_ID,
        inventory_batch_id=None,
        type=NotificationType.EXPIRING_SOON,
        title="Food expires soon",
        body="Milk expires soon.",
        payload={"batch_id": "batch-1"},
        status=status,
        delivery_status=NotificationDeliveryStatus.SENT,
        scheduled_at=NOW,
        sent_at=NOW,
        created_at=NOW,
    )


@pytest.fixture
async def notification_api_dependencies() -> AsyncIterator[None]:
    """Override authentication and notification dependencies."""

    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def get_service() -> FakeNotificationService:
        return FakeNotificationService()

    def get_fcm_service() -> FakeProductionFCMService:
        return FakeProductionFCMService()

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_notification_service] = get_service
    app.dependency_overrides[get_production_fcm_service] = get_fcm_service
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_notification_service, None)
        app.dependency_overrides.pop(get_production_fcm_service, None)


@pytest.mark.anyio
@pytest.mark.usefixtures("notification_api_dependencies")
async def test_register_and_disable_android_device_routes(
    api_client: httpx.AsyncClient,
) -> None:
    """Authenticated clients can register and disable their Android device."""
    register_response = await api_client.post(
        "/api/users/me/devices",
        json={
            "fcm_token": "android-fcm-registration-token-123456789",
            "platform": "ANDROID",
        },
    )
    disable_response = await api_client.delete(
        f"/api/users/me/devices/{DEVICE_ID}",
    )

    assert register_response.status_code == 200
    assert register_response.json()["device_id"] == str(DEVICE_ID)
    assert disable_response.status_code == 204


@pytest.mark.anyio
@pytest.mark.usefixtures("notification_api_dependencies")
async def test_list_and_mark_notification_read_routes(
    api_client: httpx.AsyncClient,
) -> None:
    """Authenticated clients can list notifications and mark one as read."""
    list_response = await api_client.get("/api/notifications")
    update_response = await api_client.patch(
        f"/api/notifications/{NOTIFICATION_ID}",
        json={"status": "READ"},
    )

    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["notification_id"] == str(NOTIFICATION_ID)
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "READ"


@pytest.mark.anyio
@pytest.mark.usefixtures("notification_api_dependencies")
async def test_direct_android_and_web_notification_routes_are_public(
    api_client: httpx.AsyncClient,
) -> None:
    """Manual-test routes send directly without requiring bearer authentication."""
    request_body = {
        "device_token": "firebase-device-registration-token-123456789",
        "title": "Manual notification test",
        "body": "Firebase delivery is working.",
        "data": {"source": "manual-test"},
    }

    android_response = await api_client.post(
        "/api/send-notification",
        json=request_body,
    )
    web_response = await api_client.post(
        "/api/send-web-notification",
        json=request_body,
    )

    assert android_response.status_code == 200
    assert android_response.json() == {"message_id": "android-message-id"}
    assert web_response.status_code == 200
    assert web_response.json() == {"message_id": "web-message-id"}

    schema = app.openapi()
    assert "security" not in schema["paths"]["/api/send-notification"]["post"]
    assert "security" not in schema["paths"]["/api/send-web-notification"]["post"]


def test_notification_routes_require_bearer_authentication() -> None:
    """OpenAPI marks device and notification routes as protected."""
    schema = app.openapi()
    paths = schema["paths"]
    assert paths["/api/users/me/devices"]["post"]["security"] == [{"BearerAuth": []}]
    assert paths["/api/notifications"]["get"]["security"] == [{"BearerAuth": []}]
