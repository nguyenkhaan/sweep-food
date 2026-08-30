"""Argon2id password hashing helper."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

_PASSWORD_HASHER = PasswordHasher()


def hashing(value: str) -> str:
    """Return an Argon2id hash for a non-empty plaintext value."""
    if not value:
        raise ValueError("A non-empty value is required for hashing")
    return _PASSWORD_HASHER.hash(value)


def compare_hash(value: str, hashed_value: str) -> bool:
    """Return whether ``value`` matches a valid Argon2id hash."""
    if not value or not hashed_value:
        return False
    try:
        return _PASSWORD_HASHER.verify(hashed_value, value)
    except VerificationError:
        return False
