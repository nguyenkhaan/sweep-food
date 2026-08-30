"""Request and response DTOs for current-user APIs."""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_E164_PATTERN = re.compile(r"^\+[1-9][0-9]{7,14}$")


class CurrentUserDTO(BaseModel):
    """Minimal identity data required by the frontend after authentication."""

    user_id: UUID
    roles: list[str]


class UserProfileDTO(BaseModel):
    """Profile fields owned by the authenticated user."""

    user_id: UUID
    name: str | None
    phone: str
    phone_verified_at: datetime | None
    email: str | None
    email_verified_at: datetime | None
    preferences: dict[str, object]


class UpdateUserProfileRequestDTO(BaseModel):
    """Mutable user profile fields."""

    name: str | None = Field(default=None, max_length=100)
    preferences: dict[str, object] | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        """Trim a supplied display name while allowing it to be cleared."""
        return value.strip() if value is not None else None


class EmailRequestDTO(BaseModel):
    """New email destination that must be verified before use."""

    email: str = Field(max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Require a basic normalized email address without extra packages."""
        email = value.strip().lower()
        if not _EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Email must be valid")
        return email


class PhoneRequestDTO(BaseModel):
    """New E.164 phone destination that must be verified before use."""

    phone: str

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        """Require normalized E.164 phone input."""
        phone = value.strip()
        if not _PHONE_E164_PATTERN.fullmatch(phone):
            raise ValueError("Phone must use E.164 format")
        return phone


class EmailVerificationRequestDTO(BaseModel):
    """OTP submitted for the email destination stored by the prior request."""

    otp: str = Field(pattern=r"^[0-9]{6}$")


class PhoneVerificationRequestDTO(BaseModel):
    """OTP submitted for the phone destination stored by the prior request."""

    otp: str = Field(pattern=r"^[0-9]{6}$")


class UserOTPIssueResponseDTO(BaseModel):
    """Generated current-user OTP returned by the local MVP contract."""

    otp: str = Field(pattern=r"^[0-9]{6}$")
    expires_in_seconds: int
