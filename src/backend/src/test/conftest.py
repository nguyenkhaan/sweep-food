"""Shared fixtures for API, safe database, Redis, and WireMock tests."""

import asyncio
import os
from collections.abc import AsyncGenerator, Iterator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.app import app
from src.core.setting import DATABASE_URL
from src.db import build_async_database_url


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
    if database_url == DATABASE_URL:
        pytest.fail("TEST_DATABASE_URL must not point to the application database.")
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
