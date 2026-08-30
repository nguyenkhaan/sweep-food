"""Unit tests for authenticated current-user profile and contact flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.helper.pwd_hash import hashing
from src.model.enum_model import AccountStatus, UserRole
from src.model.user_model import UserModel
from src.module.user.user_dto import (
    EmailRequestDTO,
    EmailVerificationRequestDTO,
    PhoneRequestDTO,
    PhoneVerificationRequestDTO,
    UpdateUserProfileRequestDTO,
)
from src.module.user.user_service import EmailAlreadyUsedError, UserService
from src.service.otp_delivery_service import OTPDeliveryRequest
from src.service.otp_service import OTPService
from src.test.test_otp_service import FakeOTPStore

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")


@dataclass
class FakeScalarResult:
    """Expose the scalar query result consumed by UserService."""

    value: object | None

    def scalar_one_or_none(self) -> object | None:
        """Return the queued query value."""
        return self.value


@dataclass
class FakeDatabaseSession:
    """In-memory AsyncSession subset for current-user service tests."""

    query_values: list[object | None] = field(default_factory=list)
    commits: int = 0
    rollbacks: int = 0

    async def execute(self, _statement: object) -> FakeScalarResult:
        """Return values in the same order as UserService queries them."""
        value = self.query_values.pop(0) if self.query_values else None
        return FakeScalarResult(value)

    async def commit(self) -> None:
        """Record a completed transaction."""
        self.commits += 1

    async def rollback(self) -> None:
        """Record a rolled-back transaction."""
        self.rollbacks += 1


@dataclass
class FakeOTPDeliveryService:
    """Record email/SMS delivery calls without network I/O."""

    requests: list[OTPDeliveryRequest] = field(default_factory=list)

    async def send_otp(self, request: OTPDeliveryRequest) -> str:
        """Record a delivery request and return a provider reference."""
        self.requests.append(request)
        return "delivery-reference"


def build_user(email: str | None = None) -> UserModel:
    """Build an active account owned by the current test user."""
    return UserModel(
        id=USER_ID,
        name="Cloudian",
        phone_e164="+84901234567",
        password_hash=hashing("safe-password"),
        role=UserRole.USER,
        status=AccountStatus.ACTIVE,
        email=email,
        preferences={"locale": "vi"},
    )


def build_service(
    database: FakeDatabaseSession,
    sms_delivery: FakeOTPDeliveryService,
    email_delivery: FakeOTPDeliveryService,
) -> UserService:
    """Build UserService with isolated OTP storage and delivery boundaries."""
    store = FakeOTPStore()
    return UserService(
        db_session=cast(AsyncSession, database),
        otp_service=OTPService(store, fixed_otp_code="123456"),
        sms_delivery_service=sms_delivery,
        email_delivery_service=email_delivery,
        pending_contact_store=store,
    )


@pytest.mark.anyio
async def test_update_profile_changes_only_the_current_users_fields() -> None:
    """The profile service updates the queried authenticated account only."""
    user = build_user()
    database = FakeDatabaseSession(query_values=[user])
    service = build_service(
        database,
        FakeOTPDeliveryService(),
        FakeOTPDeliveryService(),
    )

    profile = await service.update_profile(
        USER_ID,
        UpdateUserProfileRequestDTO(
            name="  New name  ",
            preferences={"locale": "en"},
        ),
    )

    assert profile.user_id == USER_ID
    assert profile.name == "New name"
    assert profile.preferences == {"locale": "en"}
    assert database.commits == 1


@pytest.mark.anyio
async def test_request_and_verify_email_uses_verify_email_otp_scope() -> None:
    """A user without email can attach it only after the email OTP verifies."""
    user = build_user()
    database = FakeDatabaseSession(query_values=[user, None, user, None])
    sms_delivery = FakeOTPDeliveryService()
    email_delivery = FakeOTPDeliveryService()
    service = build_service(database, sms_delivery, email_delivery)
    request = EmailRequestDTO(email="cloudian@example.com")

    issued = await service.request_email_verification(USER_ID, request)
    await service.verify_email(
        USER_ID,
        EmailVerificationRequestDTO(otp="123456"),
    )

    assert issued.otp == email_delivery.requests[0].otp
    assert email_delivery.requests[0].template_id == "VERIFY_EMAIL"
    assert user.email == "cloudian@example.com"
    assert user.email_verified_at is not None
    assert not sms_delivery.requests
    assert database.commits == 1
    assert await service.pending_contact_store.get(f"user:pending-email:{USER_ID}") is None


@pytest.mark.anyio
async def test_email_verification_rejects_an_email_owned_by_another_user() -> None:
    """Email request does not disclose or overwrite another account's email."""
    user = build_user()
    existing_user = build_user(email="taken@example.com")
    existing_user.id = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabc")
    database = FakeDatabaseSession(query_values=[user, existing_user])
    service = build_service(
        database,
        FakeOTPDeliveryService(),
        FakeOTPDeliveryService(),
    )

    with pytest.raises(EmailAlreadyUsedError):
        await service.request_email_verification(
            USER_ID,
            EmailRequestDTO(email="taken@example.com"),
        )


@pytest.mark.anyio
async def test_unverified_email_uses_verify_email_scope() -> None:
    """An existing but unverified email still uses the verification purpose."""
    user = build_user(email="unverified@example.com")
    database = FakeDatabaseSession(query_values=[user, None])
    email_delivery = FakeOTPDeliveryService()
    service = build_service(database, FakeOTPDeliveryService(), email_delivery)

    await service.request_email_verification(
        USER_ID,
        EmailRequestDTO(email="unverified@example.com"),
    )

    assert email_delivery.requests[0].template_id == "VERIFY_EMAIL"


@pytest.mark.anyio
async def test_request_and_confirm_phone_change_uses_change_phone_scope() -> None:
    """A valid SMS OTP changes only the authenticated user's phone number."""
    user = build_user()
    database = FakeDatabaseSession(query_values=[user, None, user, None])
    sms_delivery = FakeOTPDeliveryService()
    service = build_service(database, sms_delivery, FakeOTPDeliveryService())
    request = PhoneRequestDTO(phone="+84907654321")

    issued = await service.request_phone_change(USER_ID, request)
    await service.confirm_phone_change(
        USER_ID,
        PhoneVerificationRequestDTO(otp="123456"),
    )

    assert issued.otp == sms_delivery.requests[0].otp
    assert sms_delivery.requests[0].template_id == "CHANGE_PHONE"
    assert user.phone_e164 == "+84907654321"
    assert user.phone_verified_at is not None
    assert database.commits == 1
    assert await service.pending_contact_store.get(f"user:pending-phone:{USER_ID}") is None


@pytest.mark.anyio
async def test_phone_change_sends_the_same_otp_to_existing_email() -> None:
    """Phone changes additionally notify the account email when it exists."""
    user = build_user(email="cloudian@example.com")
    database = FakeDatabaseSession(query_values=[user, None])
    sms_delivery = FakeOTPDeliveryService()
    email_delivery = FakeOTPDeliveryService()
    service = build_service(database, sms_delivery, email_delivery)

    issued = await service.request_phone_change(
        USER_ID,
        PhoneRequestDTO(phone="+84907654321"),
    )

    assert issued.otp == sms_delivery.requests[0].otp
    assert issued.otp == email_delivery.requests[0].otp
    assert email_delivery.requests[0].destination == "cloudian@example.com"
    assert email_delivery.requests[0].template_id == "CHANGE_PHONE"
