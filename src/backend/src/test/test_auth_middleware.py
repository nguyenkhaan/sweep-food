"""Unit tests for custom JWT authentication and role authorization."""

from dataclasses import dataclass
from typing import cast
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.app import app
from src.core.setting import JWT_ACCESS_SECRET
from src.middleware.auth_middleware import (
    AuthenticatedUser,
    require_authentication,
)
from src.middleware.role_middleware import require_role
from src.model.enum_model import AccountStatus, UserRole
from src.model.user_model import UserModel
from src.service.jwt_service import JwtService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")


@dataclass
class FakeQueryResult:
    """Return one configured ORM object from a fake scalar result."""

    value: UserModel | None

    def scalar_one_or_none(self) -> UserModel | None:
        """Return the configured scalar value."""
        return self.value


@dataclass
class FakeDatabaseSession:
    """Provide the minimal query surface used by authentication middleware."""

    user: UserModel | None

    async def execute(self, _statement: object) -> FakeQueryResult:
        """Return the configured user result."""
        return FakeQueryResult(self.user)


def _active_user() -> UserModel:
    """Build an active user matching the JWT test subject."""
    return UserModel(
        id=USER_ID,
        phone_e164="+84901234567",
        password_hash="not-used-in-this-test",
        role=UserRole.USER,
        status=AccountStatus.ACTIVE,
    )


def _request(authorization: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if authorization is not None:
        headers.append((b"authorization", authorization.encode()))
    return Request({"type": "http", "method": "GET", "headers": headers})


def _access_token(*roles: UserRole) -> str:
    return JwtService.generate_jwt(
        {
            "sub": str(USER_ID),
            "roles": [role.value for role in roles],
            "purpose": "access",
        },
        JWT_ACCESS_SECRET,
    )


def test_jwt_service_uses_the_supplied_secret_key() -> None:
    """JWT signing and verification use the caller-provided secret key."""
    secret_key = "isolated-jwt-secret-with-at-least-thirty-two-bytes"
    payload = {"sub": str(USER_ID), "roles": [UserRole.USER.value]}
    token = JwtService.generate_jwt(payload, secret_key)

    assert JwtService.verify_jwt(token, secret_key) == payload


@pytest.mark.anyio
async def test_authentication_returns_only_token_identity_claims() -> None:
    """A valid Bearer token returns its UUID subject and enum roles."""
    principal = await require_authentication(
        _request(f"Bearer {_access_token(UserRole.USER)}"),
        cast(AsyncSession, FakeDatabaseSession(_active_user())),
    )

    assert principal == AuthenticatedUser(USER_ID, (UserRole.USER,))


@pytest.mark.anyio
@pytest.mark.parametrize(
    "authorization",
    [None, "Basic credentials", "Bearer invalid-token", "Bearer "],
)
async def test_authentication_rejects_missing_or_invalid_bearer_token(
    authorization: str | None,
) -> None:
    """Malformed or invalid authorization input returns an HTTP 401 error."""
    with pytest.raises(HTTPException) as error:
        await require_authentication(
            _request(authorization),
            cast(AsyncSession, FakeDatabaseSession(_active_user())),
        )

    assert error.value.status_code == 401
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.anyio
async def test_authentication_rejects_a_banned_account() -> None:
    """An otherwise valid JWT cannot authorize a banned database account."""
    banned_user = _active_user()
    banned_user.status = AccountStatus.BANNED

    with pytest.raises(HTTPException) as error:
        await require_authentication(
            _request(f"Bearer {_access_token(UserRole.USER)}"),
            cast(AsyncSession, FakeDatabaseSession(banned_user)),
        )

    assert error.value.status_code == 401


@pytest.mark.anyio
async def test_authentication_rejects_non_access_token_purpose() -> None:
    """A JWT marked for refresh cannot authorize a protected endpoint."""
    token = JwtService.generate_jwt(
        {
            "sub": str(USER_ID),
            "roles": [UserRole.USER.value],
            "purpose": "refresh",
        },
        JWT_ACCESS_SECRET,
    )

    with pytest.raises(HTTPException) as error:
        await require_authentication(
            _request(f"Bearer {token}"),
            cast(AsyncSession, FakeDatabaseSession(_active_user())),
        )

    assert error.value.status_code == 401


@pytest.mark.anyio
async def test_role_dependency_allows_any_matching_role() -> None:
    """One role match is sufficient to authorize the principal."""
    principal = AuthenticatedUser(USER_ID, (UserRole.USER,))

    assert await require_role(UserRole.ADMIN, UserRole.USER)(principal) is principal


@pytest.mark.anyio
async def test_role_dependency_rejects_unmatched_role() -> None:
    """A principal without a required role receives HTTP 403."""
    with pytest.raises(HTTPException) as error:
        await require_role(UserRole.ADMIN)(
            AuthenticatedUser(USER_ID, (UserRole.USER,))
        )

    assert error.value.status_code == 403


def test_openapi_exposes_bearer_authorization() -> None:
    """Swagger automatically locks authentication and role dependencies."""
    app.openapi_schema = None
    schema = app.openapi()
    components = schema["components"]
    assert isinstance(components, dict)
    security_schemes = components["securitySchemes"]
    assert isinstance(security_schemes, dict)
    assert security_schemes["BearerAuth"] == {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    paths = schema["paths"]
    assert isinstance(paths, dict)
    protected_operations = (
        ("/api/auth/password/change", "post"),
        ("/api/auth/logout", "post"),
        ("/api/auth/sessions", "get"),
        ("/api/auth/sessions/{session_id}", "delete"),
        ("/api/health/test-login", "get"),
        ("/api/health/test-role", "get"),
    )
    for path, method in protected_operations:
        path_item = paths[path]
        assert isinstance(path_item, dict)
        operation = path_item[method]
        assert isinstance(operation, dict)
        assert operation["security"] == [{"BearerAuth": []}]

    login_path = paths["/api/auth/login"]
    assert isinstance(login_path, dict)
    login_operation = login_path["post"]
    assert isinstance(login_operation, dict)
    assert "security" not in login_operation
