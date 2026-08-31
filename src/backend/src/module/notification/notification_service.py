"""Owned Android device and in-app notification operations."""

from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from typing import ClassVar, Protocol
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.device_registration_model import DeviceRegistrationModel
from src.model.enum_model import (
    NotificationDeliveryStatus,
    NotificationStatus,
)
from src.model.notification_model import NotificationModel
from src.module.notification.notification_dto import (
    CreateNotificationData,
    DeviceRegistrationResponseDTO,
    NotificationListResponseDTO,
    NotificationResponseDTO,
    RegisterDeviceRequestDTO,
    UpdateNotificationRequestDTO,
)


class TokenCipher(Protocol):
    """Protect and restore FCM registration tokens at the storage boundary."""

    def encrypt(self, token: str) -> str:
        """Return an encrypted token suitable for persistence."""
        raise NotImplementedError

    def decrypt(self, protected_token: str) -> str:
        """Return the original FCM registration token."""
        raise NotImplementedError


class FernetTokenCipher:
    """Encrypt FCM tokens with a dedicated environment-provided Fernet key."""

    def __init__(self, encryption_key: str) -> None:
        """Validate and retain the configured Fernet key."""
        self._fernet = Fernet(encryption_key.encode("ascii"))

    def encrypt(self, token: str) -> str:
        """Encrypt one UTF-8 FCM registration token."""
        return self._fernet.encrypt(token.encode("utf-8")).decode("ascii")

    def decrypt(self, protected_token: str) -> str:
        """Decrypt one persisted FCM token or reject corrupted ciphertext."""
        try:
            decrypted = self._fernet.decrypt(protected_token.encode("ascii"))
        except (InvalidToken, UnicodeEncodeError) as error:
            raise ValueError("Stored FCM token could not be decrypted") from error
        return decrypted.decode("utf-8")


class NotificationDomainError(HTTPException):
    """Base HTTP error for notification operations."""

    domain_status_code: ClassVar[int] = status.HTTP_400_BAD_REQUEST
    default_detail: ClassVar[str] = "Notification request could not be completed"

    def __init__(self, detail: str | None = None) -> None:
        """Create a stable client-safe domain error."""
        super().__init__(
            status_code=self.domain_status_code, detail=detail or self.default_detail
        )


class NotificationNotFoundError(NotificationDomainError):
    """Hide absent and cross-user resources behind the same response."""

    domain_status_code: ClassVar[int] = status.HTTP_404_NOT_FOUND
    default_detail: ClassVar[str] = "Notification resource was not found"


class NotificationService:
    """Manage FCM devices and in-app notifications for one user."""

    def __init__(
        self,
        db_session: AsyncSession,
        token_cipher: TokenCipher,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Store request persistence, token protection, and a testable clock."""
        self.db_session = db_session
        self.token_cipher = token_cipher
        self.clock = clock or (lambda: datetime.now(UTC))

    async def create_notification(
        self,
        data: CreateNotificationData,
    ) -> NotificationModel:
        """Create one unread, pending notification and return its record."""
        title = self._require_text(data["title"], "title")
        body = self._require_text(data["body"], "body")
        deduplication_key = self._require_text(
            data["deduplication_key"],
            "deduplication key",
        )
        scheduled_at = data.get("scheduled_at") or self.clock()
        if scheduled_at.utcoffset() is None:
            raise ValueError("Notification scheduled time must include a timezone")
        notification = NotificationModel(
            user_id=data["user_id"],
            inventory_batch_id=data.get("inventory_batch_id"),
            type=data["notification_type"],
            title=title,
            body=body,
            payload=dict(data.get("payload", {})),
            deduplication_key=deduplication_key,
            status=NotificationStatus.UNREAD,
            delivery_status=NotificationDeliveryStatus.PENDING,
            scheduled_at=scheduled_at,
            sent_at=None,
            retry_count=0,
        )
        try:
            self.db_session.add(notification)
            await self.db_session.flush()
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        return notification

    async def register_device(
        self,
        user_id: UUID,
        request: RegisterDeviceRequestDTO,
    ) -> DeviceRegistrationResponseDTO:
        """Create or transfer/update one globally unique FCM token."""
        token_hash = sha256(request.fcm_token.encode("utf-8")).hexdigest()
        now = self.clock()
        try:
            result = await self.db_session.execute(
                select(DeviceRegistrationModel).where(
                    DeviceRegistrationModel.fcm_token_hash == token_hash,
                ),
            )
            device = result.scalar_one_or_none()
            encrypted_token = self.token_cipher.encrypt(request.fcm_token)
            if device is None:
                device = DeviceRegistrationModel(
                    user_id=user_id,
                    fcm_token_hash=token_hash,
                    encrypted_fcm_token=encrypted_token,
                    platform=request.platform,
                    is_enabled=True,
                    last_seen_at=now,
                )
                self.db_session.add(device)
                await self.db_session.flush()
            else:
                device.user_id = user_id
                device.encrypted_fcm_token = encrypted_token
                device.platform = request.platform
                device.is_enabled = True
                device.last_seen_at = now
            await self.db_session.commit()
            return DeviceRegistrationResponseDTO(
                device_id=device.id,
                platform=device.platform,
                is_enabled=device.is_enabled,
                last_seen_at=device.last_seen_at,
            )
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def disable_device(self, user_id: UUID, device_id: UUID) -> None:
        """Disable an owned device without deleting delivery audit state."""
        try:
            result = await self.db_session.execute(
                select(DeviceRegistrationModel).where(
                    DeviceRegistrationModel.id == device_id,
                    DeviceRegistrationModel.user_id == user_id,
                ),
            )
            device = result.scalar_one_or_none()
            if device is None:
                raise NotificationNotFoundError()
            device.is_enabled = False
            await self.db_session.commit()
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def list_notifications(
        self,
        user_id: UUID,
        limit: int,
        before: datetime | None,
    ) -> NotificationListResponseDTO:
        """List owned notifications newest-first with a timestamp cursor."""
        statement = select(NotificationModel).where(
            NotificationModel.user_id == user_id,
        )
        if before is not None:
            statement = statement.where(NotificationModel.created_at < before)
        statement = statement.order_by(NotificationModel.created_at.desc()).limit(
            limit + 1,
        )
        try:
            result = await self.db_session.execute(statement)
            notifications = list(result.scalars().all())
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise
        has_more = len(notifications) > limit
        page = notifications[:limit]
        return NotificationListResponseDTO(
            items=[self._to_notification_dto(item) for item in page],
            next_before=page[-1].created_at if has_more and page else None,
        )

    async def update_notification(
        self,
        user_id: UUID,
        notification_id: UUID,
        request: UpdateNotificationRequestDTO,
    ) -> NotificationResponseDTO:
        """Mark an owned notification read or dismissed."""
        try:
            result = await self.db_session.execute(
                select(NotificationModel).where(
                    NotificationModel.id == notification_id,
                    NotificationModel.user_id == user_id,
                ),
            )
            notification = result.scalar_one_or_none()
            if notification is None:
                raise NotificationNotFoundError()
            notification.status = request.status
            await self.db_session.commit()
            return self._to_notification_dto(notification)
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    @staticmethod
    def _to_notification_dto(
        notification: NotificationModel,
    ) -> NotificationResponseDTO:
        """Map a persistence model to the public non-sensitive contract."""
        return NotificationResponseDTO(
            notification_id=notification.id,
            inventory_batch_id=notification.inventory_batch_id,
            type=notification.type,
            title=notification.title,
            body=notification.body,
            payload={
                key: value
                for key, value in notification.payload.items()
                if not key.startswith("_")
            },
            status=notification.status,
            delivery_status=notification.delivery_status,
            scheduled_at=notification.scheduled_at,
            sent_at=notification.sent_at,
            created_at=notification.created_at,
        )

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        """Normalize and validate one required notification text value."""
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"Notification {field_name} must not be empty")
        return normalized
