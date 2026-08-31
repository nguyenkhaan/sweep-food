"""Shared fixtures for API, safe database, Redis, and WireMock tests."""

import asyncio
import os
from collections.abc import AsyncGenerator, Iterator
from typing import TypeAlias

import httpx
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.app import app
from src.core.setting import DATABASE_URL
from src.db import build_async_database_url

DatabaseIdentity: TypeAlias = tuple[str, int, str]
_DATABASE_GUARD_ERROR = "Database integration configuration is invalid."
_GUARD_APPLICATION_DATABASE_URL_ENV = "TEST_DATABASE_GUARD_APPLICATION_URL"


class DatabaseTargetGuardError(ValueError):
    """Raised when a database integration target is unsafe or incomplete."""


def _normalized_database_identity(database_url: str) -> DatabaseIdentity:
    """Return a credential-free identity for a PostgreSQL database target."""
    try:
        parsed_url = make_url(database_url)
        port = parsed_url.port
    except (ArgumentError, ValueError):
        raise DatabaseTargetGuardError(_DATABASE_GUARD_ERROR) from None

    hostname = parsed_url.host
    database_name = parsed_url.database
    if (
        parsed_url.get_backend_name() != "postgresql"
        or hostname is None
        or database_name is None
    ):
        raise DatabaseTargetGuardError(_DATABASE_GUARD_ERROR)

    normalized_hostname = hostname.strip().casefold()
    normalized_database_name = database_name.strip().casefold()
    hostname_labels = normalized_hostname.split(".")
    if hostname_labels[0].endswith("-pooler"):
        hostname_labels[0] = hostname_labels[0].removesuffix("-pooler")
    normalized_hostname = ".".join(hostname_labels)
    if not normalized_hostname or not normalized_database_name:
        raise DatabaseTargetGuardError(_DATABASE_GUARD_ERROR)

    return (
        normalized_hostname,
        port if port is not None else 5432,
        normalized_database_name,
    )


def _assert_distinct_database_targets(
    application_database_url: str,
    test_database_url: str,
) -> None:
    """Reject a test URL that identifies the application database target."""
    application_identity = _normalized_database_identity(application_database_url)
    test_identity = _normalized_database_identity(test_database_url)
    if application_identity == test_identity:
        raise DatabaseTargetGuardError(_DATABASE_GUARD_ERROR)


def _get_guard_application_database_url() -> str:
    """Return the original application target preserved by a guarded test child."""
    return os.getenv(_GUARD_APPLICATION_DATABASE_URL_ENV, DATABASE_URL)


@pytest.fixture
def anyio_backend() -> str:
    """Run async HTTP tests with the installed asyncio backend."""
    return "asyncio"


@pytest.fixture
async def api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an API client without entering the database-backed lifespan."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture
def isolated_database_url() -> str:
    """Return an explicitly configured isolated database URL, never DATABASE_URL."""
    return _get_isolated_database_url()


def _get_isolated_database_url() -> str:
    """Read the database URL used only by explicitly opted-in integration tests."""
    database_url = os.getenv("TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("TEST_DATABASE_URL is required for database integration tests.")
    try:
        _assert_distinct_database_targets(
            _get_guard_application_database_url(),
            database_url,
        )
    except DatabaseTargetGuardError as error:
        pytest.fail(str(error))
    return database_url


@pytest.fixture
def database_engine() -> Iterator[AsyncEngine]:
    """Provide an async engine for a disposable database integration test."""
    engine = create_async_engine(build_async_database_url(_get_isolated_database_url()))
    try:
        yield engine
    finally:
        asyncio.run(engine.dispose())


@pytest.fixture
def redis_url() -> str:
    """Return the configured Redis endpoint for tests that opt into Redis."""
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def wiremock_url() -> str:
    """Return the local or Compose-reachable WireMock endpoint."""
    return _get_wiremock_url()


def _get_wiremock_url() -> str:
    """Read the local or Compose-reachable WireMock endpoint."""
    return os.getenv("WIREMOCK_URL", "http://localhost:8000")


@pytest.fixture
def wiremock_http_client() -> Iterator[httpx.Client]:
    """Provide a short-timeout WireMock HTTP client."""
    with httpx.Client(base_url=_get_wiremock_url(), timeout=2.0) as client:
        yield client


@pytest.fixture
def wiremock_is_available() -> bool:
    """Report whether the optional local WireMock container is reachable."""
    with httpx.Client(base_url=_get_wiremock_url(), timeout=2.0) as client:
        try:
            response = client.get("/__admin/health")
        except httpx.RequestError:
            return False
        return response.is_success
