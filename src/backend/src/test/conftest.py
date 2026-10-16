"""Shared fixtures for API, safe database, Redis, and WireMock tests."""

import os
from collections.abc import AsyncGenerator, Iterator

import httpx
import pytest

from src.app import app


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
