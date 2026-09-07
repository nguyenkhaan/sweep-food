"""Focused service and schema tests for premium-interest persistence."""

from typing import cast
from uuid import UUID

import pytest
from sqlalchemy import Table
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from src.model.premium_interest_model import PremiumInterestModel
from src.module.subscription.subscription_service import SubscriptionService

USER_A_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a201")
USER_B_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a202")


class FakeSubscriptionDatabase:
    """Record one upsert transaction without requiring migration DB-03."""

    def __init__(
        self,
        *,
        raise_execute_error: bool = False,
        raise_commit_error: bool = False,
    ) -> None:
        self.raise_execute_error = raise_execute_error
        self.raise_commit_error = raise_commit_error
        self.statements: list[ClauseElement] = []
        self.commit_count = 0
        self.rollback_count = 0

    async def execute(self, statement: ClauseElement) -> object:
        """Retain the PostgreSQL insert statement issued by the service."""
        if self.raise_execute_error:
            raise SQLAlchemyError("premium interest insert failed")
        self.statements.append(statement)
        return object()

    async def commit(self) -> None:
        """Record successful transaction completion."""
        if self.raise_commit_error:
            raise SQLAlchemyError("premium interest commit failed")
        self.commit_count += 1

    async def rollback(self) -> None:
        """Record rollback after database failure."""
        self.rollback_count += 1


def test_premium_interest_model_has_one_primary_key_and_first_registration_time() -> None:
    """The model persists exactly the two approved fields and no subscription state."""
    table = cast(Table, PremiumInterestModel.__table__)

    assert {column.name for column in table.c} == {"user_id", "registered_at"}
    assert table.c.user_id.primary_key is True
    assert table.c.user_id.foreign_keys
    assert table.c.registered_at.nullable is False
    assert table.c.registered_at.server_default is not None


def test_subscription_get_is_always_free_without_a_database_read() -> None:
    """Interest registration never upgrades the MVP subscription plan."""
    database = FakeSubscriptionDatabase()
    service = SubscriptionService(cast(AsyncSession, database))

    response = service.get_subscription()

    assert response.plan == "free"
    assert response.expires_at is None
    assert database.statements == []


@pytest.mark.anyio
async def test_register_interest_uses_user_primary_key_conflict_do_nothing() -> None:
    """A retry keeps the first row because the database does not update on conflict."""
    database = FakeSubscriptionDatabase()
    service = SubscriptionService(cast(AsyncSession, database))

    first_response = await service.register_premium_interest(USER_A_ID)
    retry_response = await service.register_premium_interest(USER_A_ID)

    compiled = database.statements[0].compile(dialect=postgresql.dialect())
    assert "ON CONFLICT (user_id) DO NOTHING" in str(compiled)
    assert USER_A_ID in compiled.params.values()
    assert first_response.registered is True
    assert retry_response.registered is True
    assert database.commit_count == 2
    assert database.rollback_count == 0


@pytest.mark.anyio
async def test_register_interest_keeps_users_in_distinct_upsert_scopes() -> None:
    """The authenticated user ID is the only persistence identity for registration."""
    database = FakeSubscriptionDatabase()
    service = SubscriptionService(cast(AsyncSession, database))

    await service.register_premium_interest(USER_A_ID)
    await service.register_premium_interest(USER_B_ID)

    user_ids = {
        statement.compile(dialect=postgresql.dialect()).params["user_id"]
        for statement in database.statements
    }
    assert user_ids == {USER_A_ID, USER_B_ID}


@pytest.mark.anyio
async def test_register_interest_rolls_back_and_does_not_report_false_success() -> None:
    """A failed insert cannot return registered=true before a successful commit."""
    database = FakeSubscriptionDatabase(raise_execute_error=True)
    service = SubscriptionService(cast(AsyncSession, database))

    with pytest.raises(SQLAlchemyError, match="premium interest insert failed"):
        await service.register_premium_interest(USER_A_ID)

    assert database.commit_count == 0
    assert database.rollback_count == 1


@pytest.mark.anyio
async def test_register_interest_rolls_back_when_commit_fails() -> None:
    """The response is withheld when PostgreSQL rejects transaction commit."""
    database = FakeSubscriptionDatabase(raise_commit_error=True)
    service = SubscriptionService(cast(AsyncSession, database))

    with pytest.raises(SQLAlchemyError, match="premium interest commit failed"):
        await service.register_premium_interest(USER_A_ID)

    assert database.commit_count == 0
    assert database.rollback_count == 1
