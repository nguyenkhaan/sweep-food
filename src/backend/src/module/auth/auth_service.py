"""Business logic for registration, password authentication, and sessions."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.setting import (
    JWT_ACCESS_SECRET,
    JWT_ACCESS_TOKEN_TTL_MINUTES,
    JWT_REFRESH_SECRET,
    JWT_REFRESH_TOKEN_TTL_DAYS,
)
from src.helper.pwd_hash import compare_hash, hashing
from src.model.auth_session_model import AuthSessionModel
from src.model.enum_model import AccountStatus, OTPChannel, OTPPurpose, UserRole
from src.model.user_model import UserModel
from src.module.auth.auth_dto import (
    AccessTokenDTO,
    AuthSessionDTO,
    LoginRequestDTO,
    OTPIssueResponseDTO,
    PasswordOTPRequestDTO,
    RegisterRequestDTO,
    TokenPairDTO,
    VerifyPasswordRequestDTO,
    VerifyRegisterRequestDTO,
)
from src.service.jwt_service import JwtService, JwtVerificationError
from src.service.otp_delivery_service import OTPDeliveryRequest, OTPDeliveryService
from src.service.otp_service import OTPService


class AuthDomainError(HTTPException):
    """Base error for stable authentication-domain failures."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Authentication request could not be completed"

    def __init__(self, detail: str | None = None) -> None:
        """Build an HTTP-safe domain failure without exposing sensitive data."""
        super().__init__(status_code=self.status_code, detail=detail or self.default_detail)


class DuplicateRegistrationError(AuthDomainError):
    """Raised when a phone already has an account."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Phone is already registered"


class InvalidCredentialsError(AuthDomainError):
    """Raised without disclosing whether account lookup or password failed."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid phone or password"


class AccountNotActiveError(AuthDomainError):
    """Raised when an operation requires an active account."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Account is not active"


class SessionNotFoundError(AuthDomainError):
    """Raised for a missing, expired, revoked, or non-owned session."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Session was not found"


class AuthService:
    """Handle one authentication operation per public service method."""

    def __init__(
        self,
        db_session: AsyncSession,
        otp_service: OTPService,
        otp_delivery_service: OTPDeliveryService,
    ) -> None:
        """Store request-scoped database and shared OTP dependencies."""
        self.db_session = db_session
        self.otp_service = otp_service
        self.otp_delivery_service = otp_delivery_service

    async def register(
        self,
        request: RegisterRequestDTO,
    ) -> OTPIssueResponseDTO:
        """Create an unverified user and send its registration OTP."""
        try:
            existing_user = await self.find_user_by_phone(request.phone)
            if existing_user is not None:
                raise DuplicateRegistrationError("Phone is already registered")
            user = UserModel(
                name=request.name,
                email = request.email, 
                phone_e164=request.phone,
                password_hash=hashing(request.password),
                status=AccountStatus.UNVERIFIED,
            )
            self.db_session.add(user)
            await self.db_session.commit()
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise
        return await self.issue_and_send_otp(
            destination=request.phone,
            purpose=OTPPurpose.REGISTER,
        )

    async def resend_register_otp(self, phone: str) -> OTPIssueResponseDTO:
        """Issue a replacement OTP only for an unverified registration account."""
        try:
            user = await self.find_user_by_phone(phone)
            if user is None or user.status is not AccountStatus.UNVERIFIED:
                raise AccountNotActiveError("Registration cannot be resent")
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise
        return await self.issue_and_send_otp(
            destination=phone,
            purpose=OTPPurpose.REGISTER,
        )

    async def verify_register(
        self,
        request: VerifyRegisterRequestDTO,
    ) -> None:
        """Verify registration OTP and activate the account without issuing tokens."""
        verification = await self.otp_service.verify_otp(
            channel=OTPChannel.SMS,
            destination=request.phone,
            purpose=OTPPurpose.REGISTER,
            otp=request.otp,
        )
        await self.otp_service.consume_grant(
            grant=verification.grant,
            channel=OTPChannel.SMS,
            destination=request.phone,
            purpose=OTPPurpose.REGISTER,
        )
        try:
            user = await self.find_user_by_phone(request.phone)
            if user is None or user.status is not AccountStatus.UNVERIFIED:
                raise AccountNotActiveError("Registration cannot be verified")
            user.status = AccountStatus.ACTIVE
            user.phone_verified_at = datetime.now(UTC)
            await self.db_session.commit()
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def request_password_reset(
        self,
        request: PasswordOTPRequestDTO,
    ) -> OTPIssueResponseDTO:
        """Issue a reset-password OTP without exposing account existence."""
        return await self.issue_and_send_otp(
            destination=request.phone,
            purpose=OTPPurpose.RESET_PASSWORD,
        )

    async def request_password_change(
        self,
        user_id: UUID,
    ) -> OTPIssueResponseDTO:
        """Issue a password-change OTP for the authenticated user's phone."""
        try:
            user = await self.find_active_user(user_id)
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise
        return await self.issue_and_send_otp(
            destination=user.phone_e164,
            purpose=OTPPurpose.CHANGE_PASSWORD,
        )

    async def verify_change_password(self, request: VerifyPasswordRequestDTO) -> None:
        """Verify a reset/change OTP, replace password, and revoke sessions."""
        purpose = OTPPurpose(request.purpose.value)
        verification = await self.otp_service.verify_otp(
            channel=OTPChannel.SMS,
            destination=request.phone,
            purpose=purpose,
            otp=request.otp,
        )
        await self.otp_service.consume_grant(
            grant=verification.grant,
            channel=OTPChannel.SMS,
            destination=request.phone,
            purpose=purpose,
        )
        try:
            user = await self.find_user_by_phone(request.phone)
            if user is None or user.status is not AccountStatus.ACTIVE:
                raise AccountNotActiveError("Password cannot be changed")
            user.password_hash = hashing(request.new_password)
            await self.revoke_user_sessions(user.id)
            await self.db_session.commit()
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def login(
        self,
        request: LoginRequestDTO,
        user_agent: str | None,
    ) -> TokenPairDTO:
        """Authenticate an active user with phone and password."""
        try:
            user = await self.find_user_by_phone(request.phone)
            if (
                user is None
                or user.status is not AccountStatus.ACTIVE
                or not compare_hash(request.password, user.password_hash)
            ):
                raise InvalidCredentialsError("Invalid phone or password")
            token_pair = await self._create_token_pair(
                user=user,
                user_agent=user_agent,
            )
            await self.db_session.commit()
            return token_pair
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> AccessTokenDTO:
        """Create a new access JWT from one active refresh JWT session."""
        user_id = self.parse_refresh_token(refresh_token)
        try:
            user = await self.find_active_user(user_id)
            session = await self.find_refresh_session(user_id, refresh_token)
            if session is None:
                raise SessionNotFoundError("Refresh token is invalid")
            session.last_used_at = datetime.now(UTC)
            await self.db_session.commit()
            return self.create_access_token(user)
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def logout(self, user_id: UUID, refresh_token: str) -> None:
        """Revoke the refresh-token session owned by the authenticated user."""
        refresh_user_id = self.parse_refresh_token(refresh_token)
        if refresh_user_id != user_id:
            raise SessionNotFoundError("Session was not found")
        try:
            session = await self.find_refresh_session(user_id, refresh_token)
            if session is None:
                raise SessionNotFoundError("Session was not found")
            session.revoked_at = datetime.now(UTC)
            await self.db_session.commit()
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def list_sessions(self, user_id: UUID) -> list[AuthSessionDTO]:
        """Return non-revoked, non-expired sessions owned by one active user."""
        try:
            await self.find_active_user(user_id)
            now = datetime.now(UTC)
            result = await self.db_session.execute(
                select(AuthSessionModel)
                .where(
                    AuthSessionModel.user_id == user_id,
                    AuthSessionModel.revoked_at.is_(None),
                    AuthSessionModel.expires_at > now,
                )
                .order_by(AuthSessionModel.created_at.desc())
            )
            sessions = result.scalars().all()
            return [
                AuthSessionDTO(
                    id=session.id,
                    ip_address=session.ip_address,
                    user_agent=session.user_agent,
                    expires_at=session.expires_at,
                    created_at=session.created_at,
                    last_used_at=session.last_used_at,
                )
                for session in sessions
            ]
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> None:
        """Revoke exactly one session owned by the authenticated user."""
        try:
            session = await self._find_session(session_id)
            if session is None or session.user_id != user_id:
                raise SessionNotFoundError("Session was not found")
            session.revoked_at = datetime.now(UTC)
            await self.db_session.commit()
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            print(f"Database error: {error}")
            raise

    async def issue_and_send_otp(
        self,
        destination: str,
        purpose: OTPPurpose,
    ) -> OTPIssueResponseDTO:
        """Generate an SMS OTP, store it, deliver it, and return it for the MVP."""
        issued_otp = await self.otp_service.issue_otp(
            channel=OTPChannel.SMS,
            destination=destination,
            purpose=purpose,
            ip_address=None,
        )
        await self.otp_delivery_service.send_otp(
            OTPDeliveryRequest(
                destination=destination,
                template_id=purpose.value,
                otp=issued_otp.otp,
                expires_in_seconds=issued_otp.expires_in_seconds,
                correlation_id=token_urlsafe(16),
            )
        )
        return OTPIssueResponseDTO(
            otp=issued_otp.otp,
            expires_in_seconds=issued_otp.expires_in_seconds,
        )

    async def find_user_by_phone(self, phone: str) -> UserModel | None:
        """Return the user matching one normalized phone number."""
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.phone_e164 == phone)
        )
        return result.scalar_one_or_none()

    async def find_active_user(self, user_id: UUID) -> UserModel:
        """Return an active user or raise a stable access error."""
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None or user.status is not AccountStatus.ACTIVE:
            raise AccountNotActiveError("Account is not active")
        return user

    async def _find_session(self, session_id: UUID) -> AuthSessionModel | None:
        """Return one session by its public UUID."""
        result = await self.db_session.execute(
            select(AuthSessionModel).where(AuthSessionModel.id == session_id)
        )
        return result.scalar_one_or_none()

    async def find_refresh_session(
        self,
        user_id: UUID,
        refresh_token: str,
    ) -> AuthSessionModel | None:
        """Find the active session whose stored hash matches a refresh JWT."""
        now = datetime.now(UTC)
        result = await self.db_session.execute(
            select(AuthSessionModel).where(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
                AuthSessionModel.expires_at > now,
            )
        )
        for session in result.scalars().all():
            if compare_hash(refresh_token, session.refresh_token_hash):
                return session
        return None

    async def _create_token_pair(
        self,
        user: UserModel,
        user_agent: str | None,
    ) -> TokenPairDTO:
        """Create access/refresh JWTs and persist the refresh session."""
        access_token = self.create_access_token(user)
        refresh_token, session_id = await self._create_refresh_token(user, user_agent)
        return TokenPairDTO(
            access_token=access_token.access_token,
            refresh_token=refresh_token,
            access_expires_in_seconds=access_token.access_expires_in_seconds,
            refresh_expires_in_seconds=JWT_REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60,
            session_id=session_id,
        )

    async def _create_refresh_token(
        self,
        user: UserModel,
        user_agent: str | None,
    ) -> tuple[str, UUID]:
        """Sign a refresh JWT with its own secret and persist its hash."""
        refresh_expires_at = datetime.now(UTC) + timedelta(
            days=JWT_REFRESH_TOKEN_TTL_DAYS,
        )
        refresh_token = JwtService.generate_jwt(
            {
                "sub": str(user.id),
                "roles": [user.role.value],
                "purpose": "refresh",
                "exp": refresh_expires_at.timestamp(),
            },
            JWT_REFRESH_SECRET,
        )
        session = AuthSessionModel(
            user_id=user.id,
            refresh_token_hash=hashing(refresh_token),
            token_family_id=uuid4(),
            ip_address=None,
            user_agent=user_agent,
            expires_at=refresh_expires_at,
        )
        self.db_session.add(session)
        await self.db_session.flush()
        return refresh_token, session.id

    def create_access_token(
        self,
        user: UserModel,
    ) -> AccessTokenDTO:
        """Sign a short-lived access JWT with the access-token secret."""
        access_expires_at = datetime.now(UTC) + timedelta(
            minutes=JWT_ACCESS_TOKEN_TTL_MINUTES,
        )
        access_token = JwtService.generate_jwt(
            {
                "sub": str(user.id),
                "roles": [user.role.value],
                "purpose": "access",
                "exp": access_expires_at.timestamp(),
            },
            JWT_ACCESS_SECRET,
        )
        return AccessTokenDTO(
            access_token=access_token,
            access_expires_in_seconds=JWT_ACCESS_TOKEN_TTL_MINUTES * 60,
        )

    async def revoke_user_sessions(self, user_id: UUID) -> None:
        """Revoke every session belonging to the supplied user."""
        await self.db_session.execute(
            update(AuthSessionModel)
            .where(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )

    @staticmethod
    def parse_refresh_token(refresh_token: str) -> UUID:
        """Verify refresh JWT signature, purpose, subject, and role claims."""
        try:
            payload = JwtService.verify_jwt(refresh_token, JWT_REFRESH_SECRET)
        except (JwtVerificationError, ValueError) as error:
            raise SessionNotFoundError("Refresh token is invalid") from error
        raw_subject = payload.get("sub")
        raw_roles = payload.get("roles")
        if (
            not isinstance(raw_subject, str)
            or not isinstance(raw_roles, list)
            or not raw_roles
            or payload.get("purpose") != "refresh"
        ):
            raise SessionNotFoundError("Refresh token is invalid")
        try:
            user_id = UUID(raw_subject)
            roles = tuple(
                UserRole(role) for role in raw_roles if isinstance(role, str)
            )
        except ValueError as error:
            raise SessionNotFoundError("Refresh token is invalid") from error
        if not roles or len(roles) != len(raw_roles):
            raise SessionNotFoundError("Refresh token is invalid")
        return user_id
