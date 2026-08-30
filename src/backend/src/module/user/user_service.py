"""Business logic for current-user profile and verified-contact APIs."""

import json
from datetime import UTC, datetime
from secrets import token_urlsafe
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import OTPChannel, OTPPurpose
from src.model.user_model import UserModel
from src.module.user.user_dto import (
    CurrentUserDTO,
    EmailRequestDTO,
    EmailVerificationRequestDTO,
    PhoneRequestDTO,
    PhoneVerificationRequestDTO,
    UpdateUserProfileRequestDTO,
    UserOTPIssueResponseDTO,
    UserProfileDTO,
)
from src.service.otp_delivery_service import OTPDeliveryRequest, OTPDeliveryService
from src.service.otp_service import OTPService, OTPStore


class UserDomainError(HTTPException):
    """Base HTTP error for current-user profile operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "User request could not be completed"

    def __init__(self, detail: str | None = None) -> None:
        """Build a stable user-facing domain error."""
        super().__init__(status_code=self.status_code, detail=detail or self.default_detail)


class UserNotFoundError(UserDomainError):
    """Raised when the authenticated account no longer exists."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "User was not found"


class EmailAlreadyUsedError(UserDomainError):
    """Raised when another account owns the requested email."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Email is already in use"


class PhoneAlreadyUsedError(UserDomainError):
    """Raised when another account owns the requested phone number."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Phone is already in use"


class PendingEmailVerificationNotFoundError(UserDomainError):
    """Raised when the user's pending email verification has expired."""

    default_detail = "Email verification was not found or has expired"


class PendingPhoneVerificationNotFoundError(UserDomainError):
    """Raised when the user's pending phone verification has expired."""

    default_detail = "Phone verification was not found or has expired"


class UserService:
    """Handle one profile or verified-contact route per public method."""

    def __init__(
        self,
        db_session: AsyncSession,
        otp_service: OTPService,
        sms_delivery_service: OTPDeliveryService,
        email_delivery_service: OTPDeliveryService,
        pending_contact_store: OTPStore,
    ) -> None:
        """Store request-scoped persistence and shared verification boundaries."""
        self.db_session = db_session
        self.otp_service = otp_service
        self.sms_delivery_service = sms_delivery_service
        self.email_delivery_service = email_delivery_service
        self.pending_contact_store = pending_contact_store

    def get_current_user(self, user_id: UUID, roles: list[str]) -> CurrentUserDTO:
        """Return the minimal identity already validated by the access JWT."""
        return CurrentUserDTO(user_id=user_id, roles=roles)

    async def get_profile(self, user_id: UUID) -> UserProfileDTO:
        """Return the authenticated user's profile without exposing another user."""
        try:
            result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError()
            return UserProfileDTO(
                user_id=user.id,
                name=user.name,
                phone=user.phone_e164,
                phone_verified_at=user.phone_verified_at,
                email=user.email,
                email_verified_at=user.email_verified_at,
                preferences=user.preferences,
            )
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def update_profile(
        self,
        user_id: UUID,
        request: UpdateUserProfileRequestDTO,
    ) -> UserProfileDTO:
        """Update supplied profile fields for the authenticated user only."""
        try:
            result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError()
            if "name" in request.model_fields_set:
                user.name = request.name
            if "preferences" in request.model_fields_set and request.preferences is not None:
                user.preferences = request.preferences
            await self.db_session.commit()
            return UserProfileDTO(
                user_id=user.id,
                name=user.name,
                phone=user.phone_e164,
                phone_verified_at=user.phone_verified_at,
                email=user.email,
                email_verified_at=user.email_verified_at,
                preferences=user.preferences,
            )
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def request_email_verification(
        self,
        user_id: UUID,
        request: EmailRequestDTO,
    ) -> UserOTPIssueResponseDTO:
        """Issue an email OTP for adding or replacing the caller's email."""
        try:
            user_result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError()
            email_result = await self.db_session.execute(
                select(UserModel).where(UserModel.email == request.email)
            )
            existing_user = email_result.scalar_one_or_none()
            if existing_user is not None and existing_user.id != user_id:
                raise EmailAlreadyUsedError()
            purpose = (
                OTPPurpose.CHANGE_EMAIL
                if user.email_verified_at is not None
                else OTPPurpose.VERIFY_EMAIL
            )
            issued_otp = await self.otp_service.issue_otp(
                channel=OTPChannel.EMAIL,
                destination=request.email,
                purpose=purpose,
                ip_address=None,
            )
            await self.pending_contact_store.set(
                f"user:pending-email:{user_id}",
                json.dumps(
                    {"email": request.email, "purpose": purpose.value},
                    separators=(",", ":"),
                ),
                issued_otp.expires_in_seconds,
            )
            await self.email_delivery_service.send_otp(
                OTPDeliveryRequest(
                    destination=request.email,
                    template_id=purpose.value,
                    otp=issued_otp.otp,
                    expires_in_seconds=issued_otp.expires_in_seconds,
                    correlation_id=token_urlsafe(16),
                )
            )
            return UserOTPIssueResponseDTO(
                otp=issued_otp.otp,
                expires_in_seconds=issued_otp.expires_in_seconds,
            )
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def verify_email(
        self,
        user_id: UUID,
        request: EmailVerificationRequestDTO,
    ) -> None:
        """Verify email OTP and attach the verified email to the caller only."""
        try:
            user_result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError()
            raw_pending_email = await self.pending_contact_store.get(
                f"user:pending-email:{user_id}"
            )
            if raw_pending_email is None:
                raise PendingEmailVerificationNotFoundError()
            try:
                pending_email = json.loads(raw_pending_email)
                email = pending_email["email"]
                purpose = OTPPurpose(pending_email["purpose"])
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                raise PendingEmailVerificationNotFoundError() from error
            if not isinstance(email, str):
                raise PendingEmailVerificationNotFoundError()
            verification = await self.otp_service.verify_otp(
                channel=OTPChannel.EMAIL,
                destination=email,
                purpose=purpose,
                otp=request.otp,
            )
            await self.otp_service.consume_grant(
                grant=verification.grant,
                channel=OTPChannel.EMAIL,
                destination=email,
                purpose=purpose,
            )
            email_result = await self.db_session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            existing_user = email_result.scalar_one_or_none()
            if existing_user is not None and existing_user.id != user_id:
                raise EmailAlreadyUsedError()
            user.email = email
            user.email_verified_at = datetime.now(UTC)
            await self.db_session.commit()
            await self.pending_contact_store.delete(f"user:pending-email:{user_id}")
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def request_phone_change(
        self,
        user_id: UUID,
        request: PhoneRequestDTO,
    ) -> UserOTPIssueResponseDTO:
        """Issue an SMS OTP for replacing the caller's phone number."""
        try:
            user_result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError()
            phone_result = await self.db_session.execute(
                select(UserModel).where(UserModel.phone_e164 == request.phone)
            )
            existing_user = phone_result.scalar_one_or_none()
            if existing_user is not None and existing_user.id != user_id:
                raise PhoneAlreadyUsedError()
            issued_otp = await self.otp_service.issue_otp(
                channel=OTPChannel.SMS,
                destination=request.phone,
                purpose=OTPPurpose.CHANGE_PHONE,
                ip_address=None,
            )
            await self.pending_contact_store.set(
                f"user:pending-phone:{user_id}",
                request.phone,
                issued_otp.expires_in_seconds,
            )
            await self.sms_delivery_service.send_otp(
                OTPDeliveryRequest(
                    destination=request.phone,
                    template_id=OTPPurpose.CHANGE_PHONE.value,
                    otp=issued_otp.otp,
                    expires_in_seconds=issued_otp.expires_in_seconds,
                    correlation_id=token_urlsafe(16),
                )
            )
            if user.email is not None:
                await self.email_delivery_service.send_otp(
                    OTPDeliveryRequest(
                        destination=user.email,
                        template_id=OTPPurpose.CHANGE_PHONE.value,
                        otp=issued_otp.otp,
                        expires_in_seconds=issued_otp.expires_in_seconds,
                        correlation_id=token_urlsafe(16),
                    )
                )
            return UserOTPIssueResponseDTO(
                otp=issued_otp.otp,
                expires_in_seconds=issued_otp.expires_in_seconds,
            )
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def confirm_phone_change(
        self,
        user_id: UUID,
        request: PhoneVerificationRequestDTO,
    ) -> None:
        """Verify phone OTP and replace only the caller's phone number."""
        try:
            user_result = await self.db_session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                raise UserNotFoundError()
            phone = await self.pending_contact_store.get(
                f"user:pending-phone:{user_id}"
            )
            if phone is None:
                raise PendingPhoneVerificationNotFoundError()
            verification = await self.otp_service.verify_otp(
                channel=OTPChannel.SMS,
                destination=phone,
                purpose=OTPPurpose.CHANGE_PHONE,
                otp=request.otp,
            )
            await self.otp_service.consume_grant(
                grant=verification.grant,
                channel=OTPChannel.SMS,
                destination=phone,
                purpose=OTPPurpose.CHANGE_PHONE,
            )
            phone_result = await self.db_session.execute(
                select(UserModel).where(UserModel.phone_e164 == phone)
            )
            existing_user = phone_result.scalar_one_or_none()
            if existing_user is not None and existing_user.id != user_id:
                raise PhoneAlreadyUsedError()
            user.phone_e164 = phone
            user.phone_verified_at = datetime.now(UTC)
            await self.db_session.commit()
            await self.pending_contact_store.delete(f"user:pending-phone:{user_id}")
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise
