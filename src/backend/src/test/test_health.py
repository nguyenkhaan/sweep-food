"""Smoke tests for the approved health endpoint contract."""

import httpx
import pytest


@pytest.mark.anyio
async def test_liveness_returns_ok(api_client: httpx.AsyncClient) -> None:
    """The liveness endpoint returns the approved JSON payload."""
    response = await api_client.get("/api/health/liveness")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
