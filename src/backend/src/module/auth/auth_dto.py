"""Request and response DTOs for phone/password authentication."""

import re
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

_PHONE_E164_PATTERN = re.compile(r"^\+[1-9][0-9]{7,14}$")
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PasswordOTPVerificationPurpose(str, Enum):
    """OTP purposes supported by the password verification endpoint."""

    RESET_PASSWORD = "RESET_PASSWORD"
    CHANGE_PASSWORD = "CHANGE_PASSWORD"


class RegisterRequestDTO(BaseModel):
    """Create an unverified account and issue its registration OTP."""

    phone: str
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=254)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Require normalized E.164 phone input."""
        phone = value.strip()
        if not _PHONE_E164_PATTERN.fullmatch(phone):
            raise ValueError("Phone must use E.164 format")
        return phone

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        """Normalize an optional email address and reject invalid formats."""
        if value is None:
            return None
        email = value.strip().lower()
        if not _EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Email must be valid")
        return email


class PasswordOTPRequestDTO(BaseModel):
    """Request a reset-password OTP for an E.164 phone number."""

    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Require normalized E.164 phone input."""
        phone = value.strip()
        if not _PHONE_E164_PATTERN.fullmatch(phone):
            raise ValueError("Phone must use E.164 format")
        return phone


class OTPIssueResponseDTO(BaseModel):
    """Generated OTP and its validity for the current MVP flow."""

    otp: str = Field(pattern=r"^[0-9]{6}$")
    expires_in_seconds: int


class VerifyRegisterRequestDTO(BaseModel):
    """Verify a registration OTP and activate the temporary account."""

    phone: str
    otp: str = Field(pattern=r"^[0-9]{6}$")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Require normalized E.164 phone input."""
        phone = value.strip()
        if not _PHONE_E164_PATTERN.fullmatch(phone):
            raise ValueError("Phone must use E.164 format")
        return phone


class VerifyPasswordRequestDTO(BaseModel):
    """Verify a password-operation OTP and set the replacement password."""

    phone: str
    otp: str = Field(pattern=r"^[0-9]{6}$")
    purpose: PasswordOTPVerificationPurpose
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Require normalized E.164 phone input."""
        phone = value.strip()
        if not _PHONE_E164_PATTERN.fullmatch(phone):
            raise ValueError("Phone must use E.164 format")
        return phone


class LoginRequestDTO(BaseModel):
    """Authenticate a user with phone number and password."""

    phone: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Require normalized E.164 phone input."""
        phone = value.strip()
        if not _PHONE_E164_PATTERN.fullmatch(phone):
            raise ValueError("Phone must use E.164 format")
        return phone


class RefreshTokenRequestDTO(BaseModel):
    """Submit a refresh JWT to obtain a new access JWT."""

    refresh_token: str = Field(min_length=1)


class LogoutRequestDTO(BaseModel):
    """Revoke the session identified by the submitted refresh token."""

    refresh_token: str = Field(min_length=1)


class TokenPairDTO(BaseModel):
    """Access and refresh JWTs created by a successful login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_in_seconds: int
    refresh_expires_in_seconds: int
    session_id: UUID


class AccessTokenDTO(BaseModel):
    """New access JWT created from a valid refresh JWT."""

    access_token: str
    token_type: str = "bearer"
    access_expires_in_seconds: int


class AuthSessionDTO(BaseModel):
    """Safe active-session data returned to its owning user."""

    id: UUID
    ip_address: str | None
    user_agent: str | None
    expires_at: datetime
    created_at: datetime
    last_used_at: datetime | None


class MessageResponseDTO(BaseModel):
    """Small acknowledgement response for successful mutations."""

    message: str
