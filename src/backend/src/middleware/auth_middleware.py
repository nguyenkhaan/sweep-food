"""Custom JWT authentication dependency."""

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, Request, status

from src.core.setting import JWT_ACCESS_SECRET
from src.model.enum_model import UserRole
from src.service.jwt_service import JwtService, JwtVerificationError


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Minimal current-user information extracted from an access token."""

    user_id: UUID
    roles: tuple[UserRole, ...]


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _get_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise _unauthorized()

    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token.strip():
        raise _unauthorized()
    return token.strip()


def _parse_authenticated_user(payload: object) -> AuthenticatedUser:
    if not isinstance(payload, dict):
        raise _unauthorized()

    raw_subject = payload.get("sub")
    raw_roles = payload.get("roles")
    if not isinstance(raw_subject, str) or not isinstance(raw_roles, list):
        raise _unauthorized()

    try:
        user_id = UUID(raw_subject)
        roles = tuple(
            UserRole(raw_role) for raw_role in raw_roles if isinstance(raw_role, str)
        )
    except ValueError as error:
        raise _unauthorized() from error

    if not roles or len(roles) != len(raw_roles):
        raise _unauthorized()
    return AuthenticatedUser(user_id=user_id, roles=roles)


def require_authentication(request: Request) -> AuthenticatedUser:
    """Validate a Bearer access JWT using the configured access secret key."""
    token = _get_bearer_token(request.headers.get("Authorization"))
    try:
        payload = JwtService.verify_jwt(token, JWT_ACCESS_SECRET)
    except (JwtVerificationError, ValueError) as error:
        raise _unauthorized() from error
    return _parse_authenticated_user(payload)
