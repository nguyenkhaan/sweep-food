"""Shared SQLAlchemy model conventions and ordered UUID generation."""

from datetime import datetime
from secrets import randbits
from threading import Lock
from time import time_ns
from uuid import UUID

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


class _UUID7Generator:
    """Generate ordered UUIDv7 values without mutable module globals."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._last_timestamp_ms = -1
        self._sequence = 0

    def __call__(self) -> UUID:
        """Return the next time-ordered UUIDv7 value for this process."""
        timestamp_ms = time_ns() // 1_000_000
        with self._lock:
            if timestamp_ms <= self._last_timestamp_ms:
                timestamp_ms = self._last_timestamp_ms
                self._sequence += 1
                if self._sequence > 0xFFF:
                    timestamp_ms += 1
                    self._sequence = 0
            else:
                self._sequence = randbits(12)
            self._last_timestamp_ms = timestamp_ms

            value = timestamp_ms << 80
            value |= 0x7 << 76
            value |= self._sequence << 64
            value |= 0x2 << 62
            value |= randbits(62)
        return UUID(int=value)


_uuid7_generator = _UUID7Generator()


def generate_uuid7() -> UUID:
    """Generate a monotonic, time-ordered UUIDv7 value within this process."""
    return _uuid7_generator()


class UUIDModel(Base):
    """Abstract base with an automatically generated, ordered UUIDv7 key."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid7,
    )


class CreatedAtUUIDModel(UUIDModel):
    """Abstract base for append-only records with a creation timestamp."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


class TimestampedUUIDModel(CreatedAtUUIDModel):
    """Abstract base for records with UTC creation and update timestamps."""

    __abstract__ = True

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
