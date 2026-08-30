"""Smoke tests for the approved health endpoint contract."""

from uuid import UUID

import httpx
import pytest

from src.app import app
from src.core.setting import JWT_ACCESS_SECRET
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.service.jwt_service import JwtService

TEST_USER_ID = "018f0f90-26e6-7ce7-8f61-8769b9e5aabb"


def _authorization_header(*roles: UserRole) -> dict[str, str]:
    token = JwtService.generate_jwt(
        {
            "sub": TEST_USER_ID,
            "roles": [role.value for role in roles],
            "purpose": "access",
        },
        JWT_ACCESS_SECRET,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_liveness_returns_ok(api_client: httpx.AsyncClient) -> None:
    """The liveness endpoint returns the approved JSON payload."""
    response = await api_client.get("/api/health/liveness")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Build with Cloudian 💙 Cloud",
    }


@pytest.mark.anyio
async def test_error_uses_standard_error_envelope(
    api_client: httpx.AsyncClient,
) -> None:
    """An HTTP error retains the documented error response fields."""
    response = await api_client.get("/api/health/error")

    assert response.status_code == 500
    assert response.json() == {
        "status_code": 500,
        "detail": "Forced health error.",
        "path": "/api/health/error",
    }


@pytest.mark.anyio
async def test_text_returns_approved_plain_text(api_client: httpx.AsyncClient) -> None:
    """The text endpoint keeps its explicit plain-text response contract."""
    response = await api_client.get("/api/health/text")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "Build with Cloudian Love Cloud"


@pytest.mark.anyio
async def test_login_route_uses_authentication_dependency(
    api_client: httpx.AsyncClient,
) -> None:
    """The test-login route exposes the authenticated token identity."""
    async def get_authenticated_user() -> AuthenticatedUser:
        """Avoid database I/O while testing the route serialization contract."""
        return AuthenticatedUser(UUID(TEST_USER_ID), (UserRole.USER,))

    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.get(
            "/api/health/test-login",
            headers=_authorization_header(UserRole.USER),
        )
    finally:
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    assert response.json() == {"user_id": TEST_USER_ID, "roles": ["USER"]}


@pytest.mark.anyio
async def test_role_route_requires_admin_role(api_client: httpx.AsyncClient) -> None:
    """The test-role route rejects a valid access token without ADMIN."""
    async def get_authenticated_user() -> AuthenticatedUser:
        """Avoid database I/O while preserving the role-policy test path."""
        return AuthenticatedUser(UUID(TEST_USER_ID), (UserRole.USER,))

    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.get(
            "/api/health/test-role",
            headers=_authorization_header(UserRole.USER),
        )
    finally:
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 403
