"""Secure one-time-password generation helper."""

from secrets import randbelow


def generate_otp() -> str:
    """Return a cryptographically secure six-digit numeric OTP."""
    return "".join(str(randbelow(10)) for _ in range(6))
