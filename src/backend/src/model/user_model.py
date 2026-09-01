"""User account database model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model.base import TimestampedUUIDModel
from src.model.enum_model import AccountStatus, UserRole

if TYPE_CHECKING:
    from src.model.inventory_batch_model import InventoryBatchModel
    from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel


class UserModel(TimestampedUUIDModel):
    """A password-authenticated Sweep Food user."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "status <> 'ACTIVE' OR phone_verified_at IS NOT NULL",
            name="active_user_requires_verified_phone",
        ),
    )

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_e164: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        default=UserRole.USER,
        nullable=False,
    )
    status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus, name="account_status"),
        default=AccountStatus.UNVERIFIED,
        nullable=False,
    )
    preferences: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    inventory_batches: Mapped[list["InventoryBatchModel"]] = relationship(
        back_populates="user",
    )
    inventory_ledger_entries: Mapped[list["InventoryLedgerEntryModel"]] = relationship(
        back_populates="user",
    )
