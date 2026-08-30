"""API contract tests for Task 2.4 authentication routes."""

from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.auth.auth_dependency import get_auth_service
from src.module.auth.auth_dto import (
    AccessTokenDTO,
    LoginRequestDTO,
    OTPIssueResponseDTO,
    PasswordOTPRequestDTO,
    TokenPairDTO,
    VerifyRegisterRequestDTO,
)
from src.service.otp_service import OTPResendCooldownError

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabc")


class FakeAuthService:
    """Provide deterministic output for router contract testing."""

    async def register(
        self,
        _body: object,
    ) -> OTPIssueResponseDTO:
        """Return a stable generated OTP without database or provider I/O."""
        return OTPIssueResponseDTO(
            otp="654321",
            expires_in_seconds=300,
        )

    async def resend_register_otp(
        self,
        _phone: str,
    ) -> OTPIssueResponseDTO:
        """Simulate the Redis resend cooldown domain failure."""
        raise OTPResendCooldownError()

    async def verify_register(self, _body: VerifyRegisterRequestDTO) -> None:
        """Accept deterministic OTP verification without persistence."""

    async def login(
        self,
        _body: LoginRequestDTO,
        _user_agent: str | None,
    ) -> TokenPairDTO:
        """Return the access/refresh JWT response shape expected from login."""
        return TokenPairDTO(
            access_token="access.jwt.token",
            refresh_token="refresh.jwt.token",
            access_expires_in_seconds=900,
            refresh_expires_in_seconds=2_592_000,
            session_id=SESSION_ID,
        )

    async def refresh_access_token(self, _refresh_token: str) -> AccessTokenDTO:
        """Return an access JWT created from the submitted refresh JWT."""
        return AccessTokenDTO(
            access_token="new.access.jwt",
            access_expires_in_seconds=900,
        )

    async def logout(self, _user_id: UUID, _refresh_token: str) -> None:
        """Accept deterministic session revocation for route contract testing."""


@pytest.mark.anyio
async def test_register_route_returns_the_generated_otp(
    api_client: httpx.AsyncClient,
) -> None:
    """Registration returns the generated OTP required by the MVP contract."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        """Override the runtime service with the deterministic fake."""
        return fake_service

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    try:
        response = await api_client.post(
            "/api/auth/register",
            json={
                "phone": "+84901234567",
                "password": "new-password",
                "name": "Cloudian",
            },
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "otp": "654321",
        "expires_in_seconds": 300,
    }


@pytest.mark.anyio
async def test_register_rejects_an_invalid_email_with_a_clear_422_error(
    api_client: httpx.AsyncClient,
) -> None:
    """Invalid email input stops before the registration service or database."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        """Prevent service dependencies from touching external resources."""
        return fake_service

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    try:
        response = await api_client.post(
            "/api/auth/register",
            json={
                "phone": "+84901234567",
                "password": "new-password",
                "email": "cloudian123",
            },
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 422
    assert response.json() == {
        "status_code": 422,
        "detail": "Email must be valid",
        "path": "/api/auth/register",
    }


@pytest.mark.anyio
async def test_resend_cooldown_returns_429_error_envelope(
    api_client: httpx.AsyncClient,
) -> None:
    """A rapid resend is a client rate-limit response rather than HTTP 500."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        """Override provider and persistence dependencies for the route test."""
        return fake_service

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    try:
        response = await api_client.post(
            "/api/auth/register/resend-otp",
            json=PasswordOTPRequestDTO(phone="+84901234567").model_dump(),
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 429
    assert response.json() == {
        "status_code": 429,
        "detail": "Please wait before requesting another OTP.",
        "path": "/api/auth/register/resend-otp",
    }


@pytest.mark.anyio
async def test_verify_register_returns_plain_text_only(
    api_client: httpx.AsyncClient,
) -> None:
    """Account verification returns no access or refresh token."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        return fake_service

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    try:
        response = await api_client.post(
            "/api/auth/verify/register",
            json={"phone": "+84901234567", "otp": "123456"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "verify account successfully"


@pytest.mark.anyio
async def test_login_returns_access_and_refresh_tokens(
    api_client: httpx.AsyncClient,
) -> None:
    """Login response contains both token types and no device label input."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        return fake_service

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    try:
        response = await api_client.post(
            "/api/auth/login",
            json={"phone": "+84901234567", "password": "new-password"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    assert response.json()["access_token"] == "access.jwt.token"
    assert response.json()["refresh_token"] == "refresh.jwt.token"


@pytest.mark.anyio
async def test_refresh_token_route_issues_access_token(
    api_client: httpx.AsyncClient,
) -> None:
    """The refresh route accepts refresh JWT and returns one access JWT."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        return fake_service

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    try:
        response = await api_client.post(
            "/api/auth/token/refresh",
            json={"refresh_token": "refresh.jwt.token"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "new.access.jwt",
        "token_type": "bearer",
        "access_expires_in_seconds": 900,
    }


@pytest.mark.anyio
async def test_logout_returns_plain_text_confirmation(
    api_client: httpx.AsyncClient,
) -> None:
    """Successful logout returns the requested plain-text acknowledgement."""
    fake_service = FakeAuthService()

    async def get_fake_auth_service() -> FakeAuthService:
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_auth_service] = get_fake_auth_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            "/api/auth/logout",
            json={"refresh_token": "refresh.jwt.token"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == "Logout successfully"
