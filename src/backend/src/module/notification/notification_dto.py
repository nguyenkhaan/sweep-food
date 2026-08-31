"""Request and response contracts for devices and notifications."""

from collections.abc import Mapping
from datetime import datetime
from typing import NotRequired, TypedDict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.model.enum_model import (
    DevicePlatform,
    NotificationDeliveryStatus,
    NotificationStatus,
    NotificationType,
)


class CreateNotificationData(TypedDict):
    """Caller-owned values required to persist a generic notification record."""

    user_id: UUID
    notification_type: NotificationType
    title: str
    body: str
    deduplication_key: str
    payload: NotRequired[Mapping[str, object]]
    inventory_batch_id: NotRequired[UUID | None]
    scheduled_at: NotRequired[datetime | None]


class RegisterDeviceRequestDTO(BaseModel):
    """Android FCM token submitted by the authenticated application."""

    model_config = ConfigDict(extra="forbid")

    fcm_token: str = Field(min_length=20, max_length=4096)
    platform: DevicePlatform

    @field_validator("fcm_token")
    @classmethod
    def normalize_fcm_token(cls, value: str) -> str:
        """Reject a token that becomes empty after whitespace normalization."""
        token = value.strip()
        if len(token) < 20:
            raise ValueError("FCM token must contain at least 20 characters")
        return token


class DeviceRegistrationResponseDTO(BaseModel):
    """Non-sensitive device registration state."""

    device_id: UUID
    platform: DevicePlatform
    is_enabled: bool
    last_seen_at: datetime


class SendNotificationRequestDTO(BaseModel):
    """Direct Firebase delivery request used for manual integration testing."""

    model_config = ConfigDict(extra="forbid")

    device_token: str = Field(min_length=20, max_length=4096)
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=1000)
    data: dict[str, object] = Field(default_factory=dict)

    @field_validator("device_token")
    @classmethod
    def normalize_device_token(cls, value: str) -> str:
        """Reject a device token that becomes empty after normalization."""
        token = value.strip()
        if len(token) < 20:
            raise ValueError("Device token must contain at least 20 characters")
        return token


class SendNotificationResponseDTO(BaseModel):
    """Firebase identifier returned after a successful direct delivery."""

    message_id: str


class UpdateNotificationRequestDTO(BaseModel):
    """Allowed user-controlled notification status transition."""

    model_config = ConfigDict(extra="forbid")

    status: NotificationStatus

    @field_validator("status")
    @classmethod
    def require_terminal_user_status(
        cls,
        value: NotificationStatus,
    ) -> NotificationStatus:
        """Only read or dismissed states may be written through the API."""
        if value not in {NotificationStatus.READ, NotificationStatus.DISMISSED}:
            raise ValueError("Notification status must be READ or DISMISSED")
        return value


class NotificationResponseDTO(BaseModel):
    """One user-visible notification without delivery credentials."""

    notification_id: UUID
    inventory_batch_id: UUID | None
    type: NotificationType
    title: str
    body: str
    payload: dict[str, object]
    status: NotificationStatus
    delivery_status: NotificationDeliveryStatus
    scheduled_at: datetime | None
    sent_at: datetime | None
    created_at: datetime


class NotificationListResponseDTO(BaseModel):
    """Cursor-compatible notification collection."""

    items: list[NotificationResponseDTO]
    next_before: datetime | None = None
