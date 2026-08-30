"""Custom JWT authentication dependency."""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.setting import JWT_ACCESS_SECRET
from src.db import get_db_session
from src.model.enum_model import AccountStatus, UserRole
from src.model.user_model import UserModel
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
    raw_purpose = payload.get("purpose")
    if (
        not isinstance(raw_subject, str)
        or not isinstance(raw_roles, list)
        or raw_purpose != "access"
    ):
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


async def require_authentication(
    request: Request,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthenticatedUser:
    """Validate JWT identity and ensure the database account remains active."""
    token = _get_bearer_token(request.headers.get("Authorization"))
    try:
        payload = JwtService.verify_jwt(token, JWT_ACCESS_SECRET)
    except (JwtVerificationError, ValueError) as error:
        raise _unauthorized() from error
    authenticated_user = _parse_authenticated_user(payload)
    try:
        result = await db_session.execute(
            select(UserModel).where(UserModel.id == authenticated_user.user_id)
        )
    except SQLAlchemyError as error:
        raise _unauthorized() from error
    user = result.scalar_one_or_none()
    if user is None or user.status is not AccountStatus.ACTIVE:
        raise _unauthorized()
    return authenticated_user
