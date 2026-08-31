"""Expiration scan and bounded FCM delivery domain services."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.device_registration_model import DeviceRegistrationModel
from src.model.enum_model import (
    InventoryBatchStatus,
    InventoryBatchType,
    NotificationDeliveryStatus,
    NotificationStatus,
    NotificationType,
)
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.notification_model import NotificationModel
from src.model.user_notification_preference_model import (
    UserNotificationPreferenceModel,
)
from src.module.notification.notification_service import TokenCipher
from src.service.fcm_service import (
    FCMDeliveryResult,
    FCMInvalidTokenError,
    FCMPermanentError,
    FCMRetryableError,
)

PRODUCT_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


class PushDeliveryService(Protocol):
    """Asynchronous FCM boundary required by notification delivery."""

    async def send_to_device(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict[str, object],
    ) -> FCMDeliveryResult:
        """Send one notification to one Android registration."""
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class ExpirationNotificationCandidate:
    """One deterministic notification derived from an inventory batch."""

    user_id: UUID
    inventory_batch_id: UUID
    type: NotificationType
    title: str
    body: str
    payload: dict[str, object]
    deduplication_key: str


@dataclass(frozen=True, slots=True)
class ExpirationScanResult:
    """Observable result of one expiration scan."""

    selected_count: int
    candidate_count: int
    created_notification_ids: list[UUID]


@dataclass(frozen=True, slots=True)
class NotificationDeliveryResult:
    """Observable result of one notification delivery attempt."""

    sent_device_count: int
    invalid_device_count: int
    failed_device_count: int
    already_sent: bool = False


class NotificationRetryableDeliveryError(RuntimeError):
    """Tell ARQ to retry a transient FCM delivery failure."""


class ExpirationNotificationService:
    """Create deduplicated in-app notifications from active expiring batches."""

    def __init__(self, db_session: AsyncSession, default_warning_days: int) -> None:
        """Store persistence and the environment-configured warning window."""
        if default_warning_days <= 0:
            raise ValueError("Default expiration warning days must be positive")
        self.db_session = db_session
        self.default_warning_days = default_warning_days

    def build_candidates(
        self,
        batches: list[InventoryBatchModel],
        preferences: dict[UUID, UserNotificationPreferenceModel],
        now: datetime,
    ) -> list[ExpirationNotificationCandidate]:
        """Map active batches to enabled notification types using local dates."""
        local_now = now.astimezone(PRODUCT_TIMEZONE)
        today = local_now.date()
        candidates: list[ExpirationNotificationCandidate] = []
        for batch in batches:
            expires_at = batch.expires_at
            if expires_at is None:
                continue
            preference = preferences.get(batch.user_id)
            warning_days: int = (
                preference.warning_days
                if preference is not None and preference.warning_days is not None
                else self.default_warning_days
            )
            expires_on = expires_at.astimezone(PRODUCT_TIMEZONE).date()
            days_remaining = (expires_on - today).days
            notification_type = self._select_type(
                batch,
                preference,
                days_remaining,
                warning_days,
            )
            if notification_type is None:
                continue
            candidates.append(
                self._build_candidate(
                    batch,
                    notification_type,
                    days_remaining,
                    expires_on,
                )
            )
        return candidates

    async def scan(self, now: datetime | None = None) -> ExpirationScanResult:
        """Persist each effective batch/window notification at most once."""
        scan_time = now or datetime.now(UTC)
        try:
            batch_result = await self.db_session.execute(
                select(InventoryBatchModel).where(
                    InventoryBatchModel.status == InventoryBatchStatus.ACTIVE,
                    InventoryBatchModel.current_quantity > 0,
                    InventoryBatchModel.expires_at.is_not(None),
                ),
            )
            batches = list(batch_result.scalars().all())
            user_ids = {batch.user_id for batch in batches}
            preferences: dict[UUID, UserNotificationPreferenceModel] = {}
            if user_ids:
                preference_result = await self.db_session.execute(
                    select(UserNotificationPreferenceModel).where(
                        UserNotificationPreferenceModel.user_id.in_(user_ids),
                    ),
                )
                preferences = {
                    preference.user_id: preference
                    for preference in preference_result.scalars().all()
                }
            candidates = self.build_candidates(batches, preferences, scan_time)
            created_ids: list[UUID] = []
            for candidate in candidates:
                statement = (
                    insert(NotificationModel)
                    .values(
                        user_id=candidate.user_id,
                        inventory_batch_id=candidate.inventory_batch_id,
                        type=candidate.type,
                        title=candidate.title,
                        body=candidate.body,
                        payload=candidate.payload,
                        deduplication_key=candidate.deduplication_key,
                        status=NotificationStatus.UNREAD,
                        delivery_status=NotificationDeliveryStatus.PENDING,
                        scheduled_at=scan_time.astimezone(UTC),
                        retry_count=0,
                    )
                    .on_conflict_do_nothing(index_elements=["deduplication_key"])
                    .returning(NotificationModel.id)
                )
                inserted_result = await self.db_session.execute(statement)
                inserted_id: UUID | None = inserted_result.scalar_one_or_none()
                if inserted_id is not None:
                    created_ids.append(inserted_id)
            await self.db_session.commit()
            return ExpirationScanResult(
                selected_count=len(batches),
                candidate_count=len(candidates),
                created_notification_ids=created_ids,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    @staticmethod
    def _select_type(
        batch: InventoryBatchModel,
        preference: UserNotificationPreferenceModel | None,
        days_remaining: int,
        warning_days: int,
    ) -> NotificationType | None:
        """Choose one enabled notification type for the current effective window."""
        notification_type: NotificationType | None = None
        is_enabled = False
        if days_remaining < 0:
            notification_type = NotificationType.EXPIRED
            is_enabled = preference is None or preference.expired_enabled
        elif days_remaining == 0:
            notification_type = NotificationType.EXPIRES_TODAY
            is_enabled = preference is None or preference.expires_today_enabled
        elif days_remaining <= warning_days:
            if batch.batch_type is InventoryBatchType.COOKED_FOOD:
                notification_type = NotificationType.LEFTOVER_REMINDER
                is_enabled = preference is None or preference.leftover_reminder_enabled
            else:
                notification_type = NotificationType.EXPIRING_SOON
                is_enabled = preference is None or preference.expiring_soon_enabled
        return notification_type if is_enabled else None

    @classmethod
    def _build_candidate(
        cls,
        batch: InventoryBatchModel,
        notification_type: NotificationType,
        days_remaining: int,
        expires_on: date,
    ) -> ExpirationNotificationCandidate:
        """Create one stable persistence candidate from a classified batch."""
        batch_name = batch.custom_name or "Food batch"
        title, body = cls._content(notification_type, batch_name, days_remaining)
        expires_at = batch.expires_at
        if expires_at is None:
            raise ValueError("Expiration notification requires an expiration timestamp")
        return ExpirationNotificationCandidate(
            user_id=batch.user_id,
            inventory_batch_id=batch.id,
            type=notification_type,
            title=title,
            body=body,
            payload={
                "batch_id": str(batch.id),
                "notification_type": notification_type.value,
                "expires_at": expires_at.isoformat(),
            },
            deduplication_key=(
                f"{batch.id}:{notification_type.value}:{expires_on.isoformat()}"
            ),
        )

    @staticmethod
    def _content(
        notification_type: NotificationType,
        batch_name: str,
        days_remaining: int,
    ) -> tuple[str, str]:
        """Return stable English content that Android may localize later."""
        if notification_type is NotificationType.EXPIRED:
            return "Food expired", f"{batch_name} has expired."
        if notification_type is NotificationType.EXPIRES_TODAY:
            return "Food expires today", f"{batch_name} expires today."
        if notification_type is NotificationType.LEFTOVER_REMINDER:
            return (
                "Use your leftovers",
                f"Use {batch_name} within {days_remaining} day(s).",
            )
        return "Food expires soon", f"{batch_name} expires in {days_remaining} day(s)."


class NotificationDeliveryService:
    """Deliver one notification to enabled devices with bounded retries."""

    def __init__(
        self,
        db_session: AsyncSession,
        token_cipher: TokenCipher,
        fcm_service: PushDeliveryService,
        max_retries: int,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Store delivery dependencies and retry configuration."""
        if max_retries <= 0:
            raise ValueError("Notification max retries must be positive")
        self.db_session = db_session
        self.token_cipher = token_cipher
        self.fcm_service = fcm_service
        self.max_retries = max_retries
        self.clock = clock or (lambda: datetime.now(UTC))

    async def deliver(self, notification_id: UUID) -> NotificationDeliveryResult:
        """Deliver once per device and persist invalid/retryable outcomes."""
        try:
            notification_result = await self.db_session.execute(
                select(NotificationModel).where(
                    NotificationModel.id == notification_id
                ),
            )
            notification = notification_result.scalar_one_or_none()
            if notification is None:
                return NotificationDeliveryResult(0, 0, 1)
            if notification.delivery_status is NotificationDeliveryStatus.SENT:
                return NotificationDeliveryResult(0, 0, 0, already_sent=True)
            devices_result = await self.db_session.execute(
                select(DeviceRegistrationModel).where(
                    DeviceRegistrationModel.user_id == notification.user_id,
                    DeviceRegistrationModel.is_enabled.is_(True),
                ),
            )
            devices = list(devices_result.scalars().all())
            return await self._deliver_to_devices(notification, devices)
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def _deliver_to_devices(
        self,
        notification: NotificationModel,
        devices: list[DeviceRegistrationModel],
    ) -> NotificationDeliveryResult:
        """Send to remaining devices and retain per-device retry dedup metadata."""
        delivered_ids = self._delivered_device_ids(notification.payload)
        sent_count = 0
        invalid_count = 0
        failed_count = 0
        for device in devices:
            if str(device.id) in delivered_ids:
                continue
            try:
                token = self.token_cipher.decrypt(device.encrypted_fcm_token)
                await self.fcm_service.send_to_device(
                    token=token,
                    title=notification.title,
                    body=notification.body,
                    data=self._public_payload(notification.payload),
                )
            except (ValueError, FCMInvalidTokenError):
                device.is_enabled = False
                invalid_count += 1
            except FCMRetryableError as error:
                notification.retry_count += 1
                notification.payload = self._with_delivered_ids(
                    notification.payload,
                    delivered_ids,
                )
                if notification.retry_count >= self.max_retries:
                    notification.delivery_status = NotificationDeliveryStatus.FAILED
                    await self.db_session.commit()
                    return NotificationDeliveryResult(
                        sent_count,
                        invalid_count,
                        failed_count + 1,
                    )
                notification.delivery_status = NotificationDeliveryStatus.RETRYING
                await self.db_session.commit()
                raise NotificationRetryableDeliveryError(
                    "FCM delivery should be retried",
                ) from error
            except FCMPermanentError:
                failed_count += 1
            else:
                delivered_ids.add(str(device.id))
                sent_count += 1
        notification.payload = self._with_delivered_ids(
            notification.payload,
            delivered_ids,
        )
        if delivered_ids:
            notification.delivery_status = NotificationDeliveryStatus.SENT
            notification.sent_at = self.clock()
        else:
            notification.delivery_status = NotificationDeliveryStatus.FAILED
        await self.db_session.commit()
        return NotificationDeliveryResult(
            sent_device_count=sent_count,
            invalid_device_count=invalid_count,
            failed_device_count=failed_count,
        )

    @staticmethod
    def _delivered_device_ids(payload: dict[str, object]) -> set[str]:
        """Read internal per-device dedup state defensively."""
        raw_ids = payload.get("_delivered_device_ids")
        if not isinstance(raw_ids, list):
            return set()
        return {value for value in raw_ids if isinstance(value, str)}

    @staticmethod
    def _with_delivered_ids(
        payload: dict[str, object],
        delivered_ids: set[str],
    ) -> dict[str, object]:
        """Return a new JSON value so SQLAlchemy tracks the internal update."""
        return {**payload, "_delivered_device_ids": sorted(delivered_ids)}

    @staticmethod
    def _public_payload(payload: dict[str, object]) -> dict[str, object]:
        """Exclude internal worker metadata from FCM and API payloads."""
        return {key: value for key, value in payload.items() if not key.startswith("_")}
