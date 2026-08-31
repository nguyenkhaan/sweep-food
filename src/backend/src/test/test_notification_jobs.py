"""Tests for expiry scanning and bounded FCM delivery jobs."""

from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.device_registration_model import DeviceRegistrationModel
from src.model.enum_model import (
    DevicePlatform,
    ExpirationSource,
    InventoryBatchStatus,
    InventoryBatchType,
    InventorySource,
    MeasurementUnit,
    NotificationDeliveryStatus,
    NotificationStatus,
    NotificationType,
    StorageMode,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.notification_model import NotificationModel
from src.model.user_notification_preference_model import (
    UserNotificationPreferenceModel,
)
from src.module.notification.notification_job_service import (
    ExpirationNotificationService,
    NotificationDeliveryService,
    NotificationRetryableDeliveryError,
    PushDeliveryService,
)
from src.module.notification.notification_service import TokenCipher
from src.service.fcm_service import (
    FCMDeliveryResult,
    FCMInvalidTokenError,
    FCMRetryableError,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aacc")
NOTIFICATION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aadd")
DEVICE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aaee")
NOW = datetime(2026, 8, 31, 1, 0, tzinfo=UTC)


class FakeScalarResult:
    """Return one scalar or a list through SQLAlchemy-like methods."""

    def __init__(self, value: object) -> None:
        self.value = value

    def scalar_one_or_none(self) -> object | None:
        """Return the configured scalar."""
        return self.value

    def scalars(self) -> "FakeScalarResult":
        """Support scalar collection chaining."""
        return self

    def all(self) -> list[object]:
        """Return a configured scalar list."""
        return self.value if isinstance(self.value, list) else []


class FakeDatabaseSession:
    """Sequence-driven async database fake for background services."""

    def __init__(self, query_values: list[object]) -> None:
        self.query_values = query_values
        self.commits = 0
        self.rollbacks = 0

    async def execute(self, _statement: object) -> FakeScalarResult:
        """Return the next configured result."""
        return FakeScalarResult(self.query_values.pop(0))

    async def commit(self) -> None:
        """Record a committed job transaction."""
        self.commits += 1

    async def rollback(self) -> None:
        """Record a rolled-back job transaction."""
        self.rollbacks += 1


class FakeTokenCipher:
    """Restore deterministic tokens for worker tests."""

    def encrypt(self, token: str) -> str:
        """Protect a token for test model construction."""
        return f"encrypted:{token}"

    def decrypt(self, protected_token: str) -> str:
        """Restore a test token."""
        return protected_token.removeprefix("encrypted:")


class FakeFCMService:
    """Return success or raise one configured FCM outcome."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.tokens: list[str] = []

    async def send_to_device(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict[str, object],
    ) -> FCMDeliveryResult:
        """Capture safe delivery fields and return the configured outcome."""
        del title, body, data
        self.tokens.append(token)
        if self.error is not None:
            raise self.error
        return FCMDeliveryResult(message_id="provider-message-id")


def build_batch(
    *,
    batch_id: UUID = BATCH_ID,
    expires_at: datetime,
    batch_type: InventoryBatchType = InventoryBatchType.RAW_INGREDIENT,
) -> InventoryBatchModel:
    """Build one active expiring inventory batch."""
    return InventoryBatchModel(
        id=batch_id,
        user_id=USER_ID,
        master_ingredient_id=None,
        custom_name="Milk",
        batch_type=batch_type,
        initial_quantity=1.0,
        current_quantity=1.0,
        unit=MeasurementUnit.LITER,
        storage_mode=StorageMode.REFRIGERATED,
        status=InventoryBatchStatus.ACTIVE,
        expires_at=expires_at,
        expiration_source=ExpirationSource.MANUFACTURER,
        source=InventorySource.MANUAL,
        created_at=NOW,
        updated_at=NOW,
    )


def build_preference() -> UserNotificationPreferenceModel:
    """Enable every supported notification type with a three-day window."""
    return UserNotificationPreferenceModel(
        user_id=USER_ID,
        warning_days=3,
        expiring_soon_enabled=True,
        expires_today_enabled=True,
        expired_enabled=True,
        leftover_reminder_enabled=True,
    )


def build_notification(
    delivery_status: NotificationDeliveryStatus = NotificationDeliveryStatus.PENDING,
    retry_count: int = 0,
) -> NotificationModel:
    """Build one pending notification for delivery tests."""
    return NotificationModel(
        id=NOTIFICATION_ID,
        user_id=USER_ID,
        inventory_batch_id=BATCH_ID,
        type=NotificationType.EXPIRING_SOON,
        title="Food expires soon",
        body="Milk expires soon.",
        payload={"batch_id": str(BATCH_ID)},
        deduplication_key=f"{BATCH_ID}:EXPIRING_SOON:2026-09-01",
        status=NotificationStatus.UNREAD,
        delivery_status=delivery_status,
        scheduled_at=NOW,
        sent_at=None,
        retry_count=retry_count,
        created_at=NOW,
        updated_at=NOW,
    )


def build_device() -> DeviceRegistrationModel:
    """Build one active encrypted Android registration."""
    return DeviceRegistrationModel(
        id=DEVICE_ID,
        user_id=USER_ID,
        fcm_token_hash="hash",
        encrypted_fcm_token="encrypted:android-token-123456789",
        platform=DevicePlatform.ANDROID,
        is_enabled=True,
        last_seen_at=NOW,
    )


def test_expiry_candidates_use_ho_chi_minh_dates_and_leftover_type() -> None:
    """Local calendar boundaries select expiry and leftover notification types."""
    batches = [
        build_batch(expires_at=NOW - timedelta(days=1)),
        build_batch(
            batch_id=UUID("018f0f90-26e6-7ce7-8f61-8769b9e5ab01"),
            expires_at=NOW,
        ),
        build_batch(
            batch_id=UUID("018f0f90-26e6-7ce7-8f61-8769b9e5ab02"),
            expires_at=NOW + timedelta(days=1),
        ),
        build_batch(
            batch_id=UUID("018f0f90-26e6-7ce7-8f61-8769b9e5ab03"),
            expires_at=NOW + timedelta(days=1),
            batch_type=InventoryBatchType.COOKED_FOOD,
        ),
    ]
    service = ExpirationNotificationService(
        cast(AsyncSession, FakeDatabaseSession([])),
        default_warning_days=3,
    )

    candidates = service.build_candidates(
        batches,
        {USER_ID: build_preference()},
        NOW,
    )

    assert [candidate.type for candidate in candidates] == [
        NotificationType.EXPIRED,
        NotificationType.EXPIRES_TODAY,
        NotificationType.EXPIRING_SOON,
        NotificationType.LEFTOVER_REMINDER,
    ]
    assert len({candidate.deduplication_key for candidate in candidates}) == 4


@pytest.mark.anyio
async def test_expiry_scan_returns_only_new_notification_ids() -> None:
    """Database conflict-safe inserts return IDs only for newly created notices."""
    batch = build_batch(expires_at=NOW + timedelta(days=1))
    database = FakeDatabaseSession(
        [[batch], [build_preference()], NOTIFICATION_ID],
    )
    service = ExpirationNotificationService(
        cast(AsyncSession, database),
        default_warning_days=3,
    )

    result = await service.scan(NOW)

    assert result.created_notification_ids == [NOTIFICATION_ID]
    assert result.selected_count == 1
    assert database.commits == 1


@pytest.mark.anyio
async def test_invalid_fcm_token_disables_device_without_retry() -> None:
    """Firebase invalid-token results permanently disable that registration."""
    notification = build_notification()
    device = build_device()
    database = FakeDatabaseSession([notification, [device]])
    service = NotificationDeliveryService(
        cast(AsyncSession, database),
        cast(TokenCipher, FakeTokenCipher()),
        cast(PushDeliveryService, FakeFCMService(FCMInvalidTokenError())),
        max_retries=3,
        clock=lambda: NOW,
    )

    result = await service.deliver(NOTIFICATION_ID)

    assert result.invalid_device_count == 1
    assert device.is_enabled is False
    assert notification.delivery_status is NotificationDeliveryStatus.FAILED
    assert notification.retry_count == 0


@pytest.mark.anyio
async def test_retryable_fcm_failure_is_bounded_to_three_attempts() -> None:
    """Transient failure schedules retry before the configured maximum only."""
    notification = build_notification(retry_count=1)
    database = FakeDatabaseSession([notification, [build_device()]])
    service = NotificationDeliveryService(
        cast(AsyncSession, database),
        cast(TokenCipher, FakeTokenCipher()),
        cast(PushDeliveryService, FakeFCMService(FCMRetryableError())),
        max_retries=3,
        clock=lambda: NOW,
    )

    with pytest.raises(NotificationRetryableDeliveryError):
        await service.deliver(NOTIFICATION_ID)

    assert notification.retry_count == 2
    assert notification.delivery_status is NotificationDeliveryStatus.RETRYING
    assert database.commits == 1


@pytest.mark.anyio
async def test_third_retryable_failure_becomes_terminal() -> None:
    """The third transient provider failure is persisted as terminal failure."""
    notification = build_notification(retry_count=2)
    database = FakeDatabaseSession([notification, [build_device()]])
    service = NotificationDeliveryService(
        cast(AsyncSession, database),
        cast(TokenCipher, FakeTokenCipher()),
        cast(PushDeliveryService, FakeFCMService(FCMRetryableError())),
        max_retries=3,
        clock=lambda: NOW,
    )

    result = await service.deliver(NOTIFICATION_ID)

    assert result.failed_device_count == 1
    assert notification.retry_count == 3
    assert notification.delivery_status is NotificationDeliveryStatus.FAILED


@pytest.mark.anyio
async def test_retry_skips_device_that_already_received_notification() -> None:
    """Per-device metadata prevents retry from creating a duplicate push."""
    notification = build_notification(NotificationDeliveryStatus.RETRYING)
    notification.payload = {
        "batch_id": str(BATCH_ID),
        "_delivered_device_ids": [str(DEVICE_ID)],
    }
    database = FakeDatabaseSession([notification, [build_device()]])
    fcm_service = FakeFCMService()
    service = NotificationDeliveryService(
        cast(AsyncSession, database),
        cast(TokenCipher, FakeTokenCipher()),
        cast(PushDeliveryService, fcm_service),
        max_retries=3,
        clock=lambda: NOW,
    )

    result = await service.deliver(NOTIFICATION_ID)

    assert result.sent_device_count == 0
    assert fcm_service.tokens == []
    assert notification.delivery_status is NotificationDeliveryStatus.SENT


@pytest.mark.anyio
async def test_successful_fcm_delivery_marks_notification_sent() -> None:
    """A successful device delivery persists sent state and its timestamp."""
    notification = build_notification()
    device = build_device()
    database = FakeDatabaseSession([notification, [device]])
    fcm_service = FakeFCMService()
    service = NotificationDeliveryService(
        cast(AsyncSession, database),
        cast(TokenCipher, FakeTokenCipher()),
        cast(PushDeliveryService, fcm_service),
        max_retries=3,
        clock=lambda: NOW,
    )

    result = await service.deliver(NOTIFICATION_ID)

    assert result.sent_device_count == 1
    assert notification.delivery_status is NotificationDeliveryStatus.SENT
    assert notification.sent_at == NOW
    assert fcm_service.tokens == ["android-token-123456789"]
