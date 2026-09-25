"""Focused tests for administrator account banning."""

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import AccountStatus, UserRole
from src.model.user_model import UserModel
from src.module.admin.admin_dependency import get_admin_service
from src.module.admin.admin_dto import BannedUserDTO
from src.module.admin.admin_service import AdminService

ADMIN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a100")
USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a101")
NOW = datetime(2026, 9, 1, tzinfo=UTC)


class FakeResult:
    """Return one optional user from a fake database query."""

    def __init__(self, user: UserModel | None) -> None:
        self.user = user

    def scalar_one_or_none(self) -> UserModel | None:
        """Return the configured user."""
        return self.user


class FakeDatabaseSession:
    """Capture admin-service transaction behavior."""

    def __init__(self, user: UserModel | None) -> None:
        self.user = user
        self.commits = 0
        self.rollbacks = 0

    async def execute(self, _statement: object) -> FakeResult:
        """Return the configured query result."""
        return FakeResult(self.user)

    async def commit(self) -> None:
        """Record a commit."""
        self.commits += 1

    async def rollback(self) -> None:
        """Record a rollback."""
        self.rollbacks += 1


def _active_user() -> UserModel:
    """Build one active user for the account-state mutation test."""
    return UserModel(
        id=USER_ID,
        phone_e164="+84900000001",
        phone_verified_at=NOW,
        password_hash="hash",
        role=UserRole.USER,
        status=AccountStatus.ACTIVE,
        preferences={},
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.mark.anyio
async def test_admin_service_bans_existing_user_and_returns_404_for_unknown() -> None:
    """The mutation commits BANNED, while an unknown ID receives HTTP 404."""
    user = _active_user()
    database = FakeDatabaseSession(user)
    response = await AdminService(cast(AsyncSession, database)).ban_user(USER_ID)

    assert user.status is AccountStatus.BANNED
    assert response == BannedUserDTO(user_id=USER_ID, status=AccountStatus.BANNED)
    assert database.commits == 1

    missing_database = FakeDatabaseSession(None)
    with pytest.raises(HTTPException) as error:
        await AdminService(cast(AsyncSession, missing_database)).ban_user(USER_ID)
    assert error.value.status_code == 404
    assert missing_database.commits == 0


@pytest.mark.anyio
async def test_admin_banned_user_route_is_role_protected(
    api_client: httpx.AsyncClient,
) -> None:
    """An administrator can call the registered PATCH endpoint."""

    class FakeAdminService:
        async def ban_user(self, user_id: UUID) -> BannedUserDTO:
            assert user_id == USER_ID
            return BannedUserDTO(user_id=user_id, status=AccountStatus.BANNED)

    async def get_fake_admin_service() -> FakeAdminService:
        return FakeAdminService()

    async def get_admin_user() -> AuthenticatedUser:
        return AuthenticatedUser(ADMIN_ID, (UserRole.ADMIN,))

    app.dependency_overrides[get_admin_service] = get_fake_admin_service
    app.dependency_overrides[require_authentication] = get_admin_user
    try:
        response = await api_client.patch(f"/api/admin/user/banned/{USER_ID}")
    finally:
        app.dependency_overrides.pop(get_admin_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    assert response.json() == {
        "user_id": str(USER_ID),
        "status": "BANNED",
    }
