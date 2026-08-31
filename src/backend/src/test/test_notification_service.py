"""Service tests for Android device registration and owned notifications."""

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.device_registration_model import DeviceRegistrationModel
from src.model.enum_model import (
    DevicePlatform,
    NotificationDeliveryStatus,
    NotificationStatus,
    NotificationType,
)
from src.model.notification_model import NotificationModel
from src.module.notification.notification_dto import (
    CreateNotificationData,
    RegisterDeviceRequestDTO,
    UpdateNotificationRequestDTO,
)
from src.module.notification.notification_service import (
    NotificationNotFoundError,
    NotificationService,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")
DEVICE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aacc")
NOTIFICATION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aadd")
NOW = datetime(2026, 8, 31, 8, 0, tzinfo=UTC)


class FakeScalarResult:
    """Return one configured scalar or scalar list."""

    def __init__(self, value: object) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object | None:
        """Return the configured scalar value."""
        return self.value

    def scalars(self) -> "FakeScalarResult":
        """Support SQLAlchemy's scalar-list result chain."""
        return self

    def all(self) -> list[object]:
        """Return configured list values."""
        if isinstance(self.value, list):
            return self.value
        return []


class FakeDatabaseSession:
    """Minimal async database fake for notification service outcomes."""

    def __init__(self, query_values: list[object | None]) -> None:
        self.query_values = query_values
        self.added: list[object] = []
        self.commits = 0
        self.rollbacks = 0

    async def execute(self, _statement: object) -> FakeScalarResult:
        """Return the next configured query result."""
        return FakeScalarResult(self.query_values.pop(0))

    def add(self, value: object) -> None:
        """Capture a pending database model."""
        self.added.append(value)

    async def flush(self) -> None:
        """Assign deterministic IDs to newly persisted test models."""
        if self.added and isinstance(self.added[-1], DeviceRegistrationModel):
            self.added[-1].id = DEVICE_ID
        if self.added and isinstance(self.added[-1], NotificationModel):
            self.added[-1].id = NOTIFICATION_ID

    async def commit(self) -> None:
        """Record a committed transaction."""
        self.commits += 1

    async def rollback(self) -> None:
        """Record a rolled-back transaction."""
        self.rollbacks += 1


class FakeTokenCipher:
    """Deterministically protect tokens without exposing a real encryption key."""

    def encrypt(self, token: str) -> str:
        """Return a visibly protected test token."""
        return f"encrypted:{token[::-1]}"

    def decrypt(self, protected_token: str) -> str:
        """Restore a token protected by this fake."""
        return protected_token.removeprefix("encrypted:")[::-1]


def build_service(database: FakeDatabaseSession) -> NotificationService:
    """Build a service while keeping the SQLAlchemy boundary explicit in tests."""
    return NotificationService(
        cast(AsyncSession, database),
        FakeTokenCipher(),
        clock=lambda: NOW,
    )


@pytest.mark.anyio
async def test_create_notification_persists_valid_pending_record() -> None:
    """Other services can create a generic record before requesting delivery."""
    database = FakeDatabaseSession([])
    service = build_service(database)

    notification = await service.create_notification(
        CreateNotificationData(
            user_id=USER_ID,
            notification_type=NotificationType.EXPIRING_SOON,
            title=" Food expires soon ",
            body=" Milk expires tomorrow. ",
            deduplication_key=" service:event:unique-id ",
            payload={"source": "another-service"},
        )
    )

    assert notification.id == NOTIFICATION_ID
    assert notification.user_id == USER_ID
    assert notification.title == "Food expires soon"
    assert notification.body == "Milk expires tomorrow."
    assert notification.payload == {"source": "another-service"}
    assert notification.deduplication_key == "service:event:unique-id"
    assert notification.status is NotificationStatus.UNREAD
    assert notification.delivery_status is NotificationDeliveryStatus.PENDING
    assert notification.scheduled_at == NOW
    assert notification.retry_count == 0
    assert database.commits == 1


@pytest.mark.anyio
async def test_register_device_hashes_and_encrypts_fcm_token() -> None:
    """A raw FCM token is never persisted while registration remains reusable."""
    database = FakeDatabaseSession([None])
    service = build_service(database)
    raw_token = "android-fcm-registration-token-123456789"

    response = await service.register_device(
        USER_ID,
        RegisterDeviceRequestDTO(
            fcm_token=raw_token,
            platform=DevicePlatform.ANDROID,
        ),
    )

    stored = cast(DeviceRegistrationModel, database.added[0])
    assert response.device_id == DEVICE_ID
    assert stored.user_id == USER_ID
    assert stored.fcm_token_hash != raw_token
    assert stored.encrypted_fcm_token != raw_token
    assert raw_token not in stored.encrypted_fcm_token
    assert stored.is_enabled is True
    assert database.commits == 1


@pytest.mark.anyio
async def test_disable_device_enforces_user_ownership() -> None:
    """A caller cannot disable a device that is absent from their owned query."""
    database = FakeDatabaseSession([None])
    service = build_service(database)

    with pytest.raises(NotificationNotFoundError):
        await service.disable_device(USER_ID, DEVICE_ID)


@pytest.mark.anyio
async def test_list_notifications_returns_only_query_owned_records() -> None:
    """Notification list serializes completed owned records without token data."""
    notification = NotificationModel(
        id=NOTIFICATION_ID,
        user_id=USER_ID,
        inventory_batch_id=None,
        type=NotificationType.EXPIRING_SOON,
        title="Food expires soon",
        body="Milk expires soon.",
        payload={
            "batch_id": "batch-1",
            "_delivered_device_ids": [str(DEVICE_ID)],
        },
        deduplication_key="batch-1:EXPIRING_SOON:2026-08-31",
        status=NotificationStatus.UNREAD,
        delivery_status=NotificationDeliveryStatus.SENT,
        scheduled_at=NOW,
        sent_at=NOW,
        retry_count=0,
        created_at=NOW,
        updated_at=NOW,
    )
    database = FakeDatabaseSession([[notification]])
    service = build_service(database)

    response = await service.list_notifications(USER_ID, limit=20, before=None)

    assert [item.notification_id for item in response.items] == [NOTIFICATION_ID]
    assert response.items[0].status is NotificationStatus.UNREAD
    assert response.items[0].payload == {"batch_id": "batch-1"}


@pytest.mark.anyio
async def test_update_notification_status_rejects_unowned_notification() -> None:
    """Status updates use the notification ID and authenticated user together."""
    database = FakeDatabaseSession([None])
    service = build_service(database)

    with pytest.raises(NotificationNotFoundError):
        await service.update_notification(
            USER_ID,
            NOTIFICATION_ID,
            UpdateNotificationRequestDTO(status=NotificationStatus.READ),
        )
