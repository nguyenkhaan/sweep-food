"""API contract tests for authenticated current-user routes."""

from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.user.user_dependency import get_user_service
from src.module.user.user_dto import CurrentUserDTO

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769b9e5aabb")


class FakeUserService:
    """Provide the deterministic user identity expected by the route test."""

    def get_current_user(self, user_id: UUID, roles: list[str]) -> CurrentUserDTO:
        """Return exactly the values provided by the auth dependency."""
        return CurrentUserDTO(user_id=user_id, roles=roles)

    async def verify_email(self, _body: object, _request: object) -> None:
        """Accept an email verification without calling persistence services."""

    async def confirm_phone_change(self, _body: object, _request: object) -> None:
        """Accept a phone verification without calling persistence services."""


@pytest.mark.anyio
async def test_me_route_returns_jwt_identity(
    api_client: httpx.AsyncClient,
) -> None:
    """The frontend gets only the ID and roles supplied by the JWT dependency."""
    fake_service = FakeUserService()

    async def get_fake_user_service() -> FakeUserService:
        """Override the runtime service without database, Redis, or delivery I/O."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for the protected route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_user_service] = get_fake_user_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.get("/api/users/me")
    finally:
        app.dependency_overrides.pop(get_user_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    assert response.json() == {
        "user_id": str(USER_ID),
        "roles": ["USER"],
    }


@pytest.mark.anyio
async def test_contact_verification_routes_return_plain_text(
    api_client: httpx.AsyncClient,
) -> None:
    """Email and phone confirmation endpoints do not disclose a user profile."""
    fake_service = FakeUserService()

    async def get_fake_user_service() -> FakeUserService:
        """Override the runtime service without database, Redis, or delivery I/O."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for protected confirmation routes."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_user_service] = get_fake_user_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        email_response = await api_client.post(
            "/api/users/me/email/verify",
            json={"otp": "123456"},
        )
        phone_response = await api_client.post(
            "/api/users/me/phone/confirm-change",
            json={"otp": "123456"},
        )
    finally:
        app.dependency_overrides.pop(get_user_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert email_response.headers["content-type"].startswith("text/plain")
    assert email_response.text == "Verify Change Email successfully"
    assert phone_response.headers["content-type"].startswith("text/plain")
    assert phone_response.text == "Verify Change Phone succesfully"


@pytest.mark.anyio
async def test_email_request_rejects_an_invalid_email_with_a_clear_422_error(
    api_client: httpx.AsyncClient,
) -> None:
    """Invalid email stops before the user service reads or writes the database."""
    fake_service = FakeUserService()

    async def get_fake_user_service() -> FakeUserService:
        """Override the runtime service without database, Redis, or delivery I/O."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid user while the request body validation is exercised."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_user_service] = get_fake_user_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.post(
            "/api/users/me/email/request-verification",
            json={"email": "cloudian123"},
        )
    finally:
        app.dependency_overrides.pop(get_user_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 422
    assert response.json() == {
        "status_code": 422,
        "detail": "Email must be valid",
        "path": "/api/users/me/email/request-verification",
    }


def test_user_openapi_marks_bearer_routes_and_otp_only_email_verification() -> None:
    """Swagger exposes custom auth and the no-email confirmation request body."""
    schema = app.openapi()
    paths = schema["paths"]
    assert isinstance(paths, dict)
    me_operation = paths["/api/users/me"]
    assert isinstance(me_operation, dict)
    get_operation = me_operation["get"]
    assert isinstance(get_operation, dict)
    assert get_operation["security"] == [{"BearerAuth": []}]
    email_verify_operation = paths["/api/users/me/email/verify"]
    assert isinstance(email_verify_operation, dict)
    post_operation = email_verify_operation["post"]
    assert isinstance(post_operation, dict)
    request_body = post_operation["requestBody"]
    assert isinstance(request_body, dict)
    content = request_body["content"]
    assert isinstance(content, dict)
    application_json = content["application/json"]
    assert isinstance(application_json, dict)
    request_schema = application_json["schema"]
    assert request_schema == {
        "$ref": "#/components/schemas/EmailVerificationRequestDTO"
    }
    components = schema["components"]
    assert isinstance(components, dict)
    schemas = components["schemas"]
    assert isinstance(schemas, dict)
    email_schema = schemas["EmailVerificationRequestDTO"]
    assert isinstance(email_schema, dict)
    assert email_schema["required"] == ["otp"]
    properties = email_schema["properties"]
    assert isinstance(properties, dict)
    assert list(properties) == ["otp"]


def test_phone_confirmation_openapi_accepts_only_otp() -> None:
    """Swagger does not ask the user to repeat the new phone number."""
    schema = app.openapi()
    paths = schema["paths"]
    assert isinstance(paths, dict)
    phone_operation = paths["/api/users/me/phone/confirm-change"]
    assert isinstance(phone_operation, dict)
    post_operation = phone_operation["post"]
    assert isinstance(post_operation, dict)
    request_body = post_operation["requestBody"]
    assert isinstance(request_body, dict)
    content = request_body["content"]
    assert isinstance(content, dict)
    application_json = content["application/json"]
    assert isinstance(application_json, dict)
    request_schema = application_json["schema"]
    assert request_schema == {
        "$ref": "#/components/schemas/PhoneVerificationRequestDTO"
    }
    components = schema["components"]
    assert isinstance(components, dict)
    schemas = components["schemas"]
    assert isinstance(schemas, dict)
    phone_schema = schemas["PhoneVerificationRequestDTO"]
    assert isinstance(phone_schema, dict)
    assert phone_schema["required"] == ["otp"]
    properties = phone_schema["properties"]
    assert isinstance(properties, dict)
    assert list(properties) == ["otp"]
