"""Per-user notification preference database model."""

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.model.base import TimestampedUUIDModel


class UserNotificationPreferenceModel(TimestampedUUIDModel):
    """One user's expiry-notification settings."""

    __tablename__ = "user_notification_preferences"
    __table_args__ = (UniqueConstraint("user_id"),)

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    warning_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expiring_soon_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    expires_today_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    expired_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    leftover_reminder_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
