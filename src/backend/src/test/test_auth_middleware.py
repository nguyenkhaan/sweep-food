"""Unit tests for custom JWT authentication and role authorization."""

from uuid import UUID

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from src.app import app
from src.core.setting import JWT_ACCESS_SECRET
from src.middleware.auth_middleware import (
    AuthenticatedUser,
    require_authentication,
)
from src.middleware.role_middleware import require_role
from src.model.enum_model import UserRole
from src.service.jwt_service import JwtService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")


def _request(authorization: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if authorization is not None:
        headers.append((b"authorization", authorization.encode()))
    return Request({"type": "http", "method": "GET", "headers": headers})


def _access_token(*roles: UserRole) -> str:
    return JwtService.generate_jwt(
        {"sub": str(USER_ID), "roles": [role.value for role in roles]},
        JWT_ACCESS_SECRET,
    )


def test_jwt_service_uses_the_supplied_secret_key() -> None:
    """JWT signing and verification use the caller-provided secret key."""
    secret_key = "isolated-jwt-secret-with-at-least-thirty-two-bytes"
    payload = {"sub": str(USER_ID), "roles": [UserRole.USER.value]}
    token = JwtService.generate_jwt(payload, secret_key)

    assert JwtService.verify_jwt(token, secret_key) == payload


def test_authentication_returns_only_token_identity_claims() -> None:
    """A valid Bearer token returns its UUID subject and enum roles."""
    principal = require_authentication(
        _request(f"Bearer {_access_token(UserRole.USER)}")
    )

    assert principal == AuthenticatedUser(USER_ID, (UserRole.USER,))


@pytest.mark.parametrize(
    "authorization",
    [None, "Basic credentials", "Bearer invalid-token", "Bearer "],
)
def test_authentication_rejects_missing_or_invalid_bearer_token(
    authorization: str | None,
) -> None:
    """Malformed or invalid authorization input returns an HTTP 401 error."""
    with pytest.raises(HTTPException) as error:
        require_authentication(_request(authorization))

    assert error.value.status_code == 401
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}


def test_role_dependency_allows_any_matching_role() -> None:
    """One role match is sufficient to authorize the principal."""
    principal = AuthenticatedUser(USER_ID, (UserRole.USER,))

    assert require_role(UserRole.ADMIN, UserRole.USER)(principal) is principal


def test_role_dependency_rejects_unmatched_role() -> None:
    """A principal without a required role receives HTTP 403."""
    with pytest.raises(HTTPException) as error:
        require_role(UserRole.ADMIN)(AuthenticatedUser(USER_ID, (UserRole.USER,)))

    assert error.value.status_code == 403


def test_openapi_exposes_bearer_authorization() -> None:
    """Swagger receives the custom Bearer scheme without a FastAPI auth scheme."""
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
