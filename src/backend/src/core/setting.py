"""Environment-backed backend configuration."""

import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class _NoArg:
    pass


NO_ARG: Final = _NoArg()


def get_env_var(key: str, default: str | _NoArg = NO_ARG) -> str:
    """Return an environment value or raise when a required value is absent."""
    value = os.getenv(key)
    if value is not None:
        return value
    if isinstance(default, _NoArg):
        raise KeyError(f"Environment variable {key} is missing")
    return default


def get_positive_int_env(key: str, default: int) -> int:
    """Return a positive integer environment value or its positive default."""
    raw_value = get_env_var(key, str(default))
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(f"Environment variable {key} must be an integer") from error
    if value <= 0:
        raise ValueError(f"Environment variable {key} must be greater than zero")
    return value


def get_six_digit_env(key: str) -> str:
    """Return a required six-digit numeric environment value."""
    value = get_env_var(key)
    if len(value) != 6 or not value.isdigit():
        raise ValueError(f"Environment variable {key} must be six numeric digits")
    return value


DATABASE_URL: Final[str] = get_env_var("DATABASE_URL")
REDIS_URL: Final[str] = get_env_var("REDIS_URL")
ENV: Final[str] = get_env_var("ENV", "dev")
JWT_ACCESS_SECRET: Final[str] = get_env_var("JWT_ACCESS_SECRET")
JWT_REFRESH_SECRET: Final[str] = get_env_var("JWT_REFRESH_SECRET")
JWT_ALGORITHM: Final[str] = get_env_var("JWT_ALGORITHM", "HS256")
DEFAULT_OTP: Final[str] = get_six_digit_env("DEFAULT_OTP")
OTP_CHALLENGE_TTL_SECONDS: Final[int] = get_positive_int_env(
    "OTP_CHALLENGE_TTL_SECONDS",
    300,
)
OTP_GRANT_TTL_SECONDS: Final[int] = get_positive_int_env("OTP_GRANT_TTL_SECONDS", 300)
OTP_RESEND_COOLDOWN_SECONDS: Final[int] = get_positive_int_env(
    "OTP_RESEND_COOLDOWN_SECONDS",
    60,
)
OTP_DESTINATION_REQUEST_LIMIT: Final[int] = get_positive_int_env(
    "OTP_DESTINATION_REQUEST_LIMIT",
    5,
)
OTP_IP_REQUEST_LIMIT: Final[int] = get_positive_int_env("OTP_IP_REQUEST_LIMIT", 20)
OTP_REQUEST_WINDOW_SECONDS: Final[int] = get_positive_int_env(
    "OTP_REQUEST_WINDOW_SECONDS",
    3600,
)
OTP_MAX_VERIFICATION_ATTEMPTS: Final[int] = get_positive_int_env(
    "OTP_MAX_VERIFICATION_ATTEMPTS",
    5,
)
OTP_FAILED_ATTEMPT_COOLDOWN_SECONDS: Final[int] = get_positive_int_env(
    "OTP_FAILED_ATTEMPT_COOLDOWN_SECONDS",
    900,
)
WIREMOCK_URL: Final[str] = get_env_var("WIREMOCK_URL")
SMS_PROVIDER: Final[str] = get_env_var("SMS_PROVIDER", "wiremock")
SMS_DELIVERY_TIMEOUT_SECONDS: Final[int] = get_positive_int_env(
    "SMS_DELIVERY_TIMEOUT_SECONDS",
    2,
)
EMAIL_SMTP_HOST: Final[str] = get_env_var("EMAIL_SMTP_HOST")
EMAIL_SMTP_PORT: Final[int] = get_positive_int_env("EMAIL_SMTP_PORT", 1025)
EMAIL_FROM: Final[str] = get_env_var("EMAIL_FROM")
JWT_ACCESS_TOKEN_TTL_MINUTES: Final[int] = get_positive_int_env(
    "JWT_ACCESS_TOKEN_TTL_MINUTES",
    15,
)
JWT_REFRESH_TOKEN_TTL_DAYS: Final[int] = get_positive_int_env(
    "JWT_REFRESH_TOKEN_TTL_DAYS",
    30,
)
EXTRACTION_MAX_IMAGE_SIZE: Final[int] = get_positive_int_env(
    "EXTRACTION_MAX_IMAGE_SIZE",
    5_242_880,
)
EXTRACTION_MAX_AUDIO_SIZE: Final[int] = get_positive_int_env(
    "EXTRACTION_MAX_AUDIO_SIZE",
    10_485_760,
)
EXTRACTION_MAX_AUDIO_DURATION: Final[int] = get_positive_int_env(
    "EXTRACTION_MAX_AUDIO_DURATION",
    60,
)
EXTRACTION_ALLOWED_IMAGE_TYPES: Final[str] = get_env_var(
    "EXTRACTION_ALLOWED_IMAGE_TYPES",
    "image/jpeg,image/png,image/webp",
)
EXTRACTION_ALLOWED_AUDIO_TYPES: Final[str] = get_env_var(
    "EXTRACTION_ALLOWED_AUDIO_TYPES",
    "audio/mpeg,audio/wav,audio/ogg",
)
EXTRACTION_PROVIDER_TIMEOUT: Final[int] = get_positive_int_env(
    "EXTRACTION_PROVIDER_TIMEOUT",
    15,
)
