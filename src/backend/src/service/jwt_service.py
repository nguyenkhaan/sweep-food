"""JWT generation and verification service."""

from collections.abc import Mapping

import jwt

from src.core.setting import JWT_ALGORITHM


class JwtVerificationError(ValueError):
    """Raised when a JWT cannot be verified or decoded safely."""


class JwtService:
    """Generate and verify JWTs with caller-supplied secret keys."""

    @staticmethod
    def generate_jwt(payload: Mapping[str, object], secret_key: str) -> str:
        """Create a signed JWT from ``payload`` using ``secret_key``."""
        JwtService._validate_secret_key(secret_key)
        return jwt.encode(dict(payload), secret_key, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt(token: str, secret_key: str) -> dict[str, object]:
        """Return the verified JWT payload or raise ``JwtVerificationError``."""
        JwtService._validate_secret_key(secret_key)
        try:
            decoded_payload: object = jwt.decode(
                token,
                secret_key,
                algorithms=[JWT_ALGORITHM],
            )
        except jwt.InvalidTokenError as error:
            raise JwtVerificationError("Invalid JWT") from error

        if not isinstance(decoded_payload, dict):
            raise JwtVerificationError("JWT payload must be an object")

        payload: dict[str, object] = {}
        for key, value in decoded_payload.items():
            if not isinstance(key, str):
                raise JwtVerificationError("JWT payload keys must be strings")
            payload[key] = value
        return payload

    @staticmethod
    def _validate_secret_key(secret_key: str) -> None:
        if not secret_key:
            raise ValueError("A JWT secret key is required")
