"""Route tests for the authenticated Subscription API."""

from collections.abc import AsyncGenerator
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.subscription.subscription_dependency import get_subscription_service
from src.module.subscription.subscription_dto import (
    PremiumInterestResponseDTO,
    SubscriptionPlan,
    SubscriptionResponseDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a211")


class FakeSubscriptionService:
    """Provide deterministic subscription responses without persistence."""

    def __init__(self) -> None:
        self.registered_user_ids: list[UUID] = []

    def get_subscription(self) -> SubscriptionResponseDTO:
        """Return the immutable MVP free plan."""
        return SubscriptionResponseDTO(plan=SubscriptionPlan.FREE, expires_at=None)

    async def register_premium_interest(
        self,
        user_id: UUID,
    ) -> PremiumInterestResponseDTO:
        """Record the route's authenticated subject for assertion."""
        self.registered_user_ids.append(user_id)
        return PremiumInterestResponseDTO(registered=True)


class FailingSubscriptionService(FakeSubscriptionService):
    """Expose a persistence failure through the application error envelope."""

    async def register_premium_interest(
        self,
        user_id: UUID,
    ) -> PremiumInterestResponseDTO:
        """Simulate the service failure that must not become false success."""
        self.registered_user_ids.append(user_id)
        raise RuntimeError("premium interest persistence failed")


@pytest.mark.anyio
async def test_subscription_routes_return_free_state_and_persist_interest(
    api_client: httpx.AsyncClient,
) -> None:
    """Both contract operations use the authenticated user and return HTTP 200."""
    fake_service = FakeSubscriptionService()

    async def get_fake_subscription_service() -> FakeSubscriptionService:
        """Avoid a database dependency in the route contract test."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide a valid current user for both protected routes."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_subscription_service] = get_fake_subscription_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        get_response = await api_client.get("/api/subscription")
        post_response = await api_client.post("/api/subscription/premium-interest")
        retry_response = await api_client.post("/api/subscription/premium-interest")
    finally:
        app.dependency_overrides.pop(get_subscription_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert get_response.status_code == 200
    assert get_response.json() == {"plan": "free", "expires_at": None}
    assert post_response.status_code == 200
    assert post_response.json() == {"registered": True}
    assert retry_response.status_code == 200
    assert retry_response.json() == {"registered": True}
    assert fake_service.registered_user_ids == [USER_ID, USER_ID]


@pytest.mark.anyio
async def test_subscription_routes_require_bearer_authentication(
    api_client: httpx.AsyncClient,
) -> None:
    """Missing bearer credentials return 401 before either operation runs."""
    fake_service = FakeSubscriptionService()

    async def get_fake_subscription_service() -> FakeSubscriptionService:
        """Avoid a real database session while the auth boundary is tested."""
        return fake_service

    async def get_unused_db_session() -> AsyncGenerator[object, None]:
        """Satisfy the auth dependency before it rejects the missing token."""
        yield object()

    app.dependency_overrides[get_subscription_service] = get_fake_subscription_service
    app.dependency_overrides[get_db_session] = get_unused_db_session
    try:
        get_response = await api_client.get("/api/subscription")
        post_response = await api_client.post("/api/subscription/premium-interest")
    finally:
        app.dependency_overrides.pop(get_subscription_service, None)
        app.dependency_overrides.pop(get_db_session, None)

    assert get_response.status_code == 401
    assert post_response.status_code == 401
    assert fake_service.registered_user_ids == []


@pytest.mark.anyio
async def test_subscription_interest_route_returns_the_error_envelope_on_failure() -> None:
    """A failed persistence path never serializes registered=true."""
    failing_service = FailingSubscriptionService()

    async def get_failing_subscription_service() -> FailingSubscriptionService:
        """Inject one deterministic persistence failure."""
        return failing_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Authenticate the request so the write error reaches the app handler."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_subscription_service] = get_failing_subscription_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.post("/api/subscription/premium-interest")
    finally:
        app.dependency_overrides.pop(get_subscription_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 500
    assert response.json() == {
        "status_code": 500,
        "detail": "Internal server error.",
        "path": "/api/subscription/premium-interest",
    }


def test_subscription_openapi_has_only_the_two_approved_operations() -> None:
    """The public schema adds no payment or feature-gating endpoints."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])
    subscription = cast(dict[str, object], paths["/api/subscription"])
    premium_interest = cast(
        dict[str, object],
        paths["/api/subscription/premium-interest"],
    )

    assert set(subscription) == {"get"}
    assert set(premium_interest) == {"post"}
    assert cast(dict[str, object], subscription["get"])["security"] == [
        {"BearerAuth": []},
    ]
    assert cast(dict[str, object], premium_interest["post"])["security"] == [
        {"BearerAuth": []},
    ]
