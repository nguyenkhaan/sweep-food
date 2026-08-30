"""FCM device registration database model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import DevicePlatform


class DeviceRegistrationModel(TimestampedUUIDModel):
    """Encrypted FCM registration for one user device."""

    __tablename__ = "device_registrations"
    __table_args__ = (UniqueConstraint("fcm_token_hash"),)

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    fcm_token_hash: Mapped[str] = mapped_column(String, nullable=False)
    encrypted_fcm_token: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[DevicePlatform] = mapped_column(
        SQLEnum(DevicePlatform, name="device_platform"),
        nullable=False,
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
