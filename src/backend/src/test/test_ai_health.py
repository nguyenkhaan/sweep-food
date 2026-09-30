"""Integration tests for the public AI readiness endpoint."""

from collections.abc import AsyncIterator
from typing import cast

import httpx
import pytest

from src.app import app
from src.service.sweep_food_ai_client import (
    AIHealthResponseDTO,
    SweepFoodAIBadResponseError,
    SweepFoodAIClient,
    SweepFoodAIError,
    SweepFoodAITimeoutError,
    SweepFoodAIUnavailableError,
    get_sweep_food_ai_client,
)


class _FakeAIClient:
    def __init__(self, result: AIHealthResponseDTO | SweepFoodAIError) -> None:
        self._result = result

    async def check_health(self) -> AIHealthResponseDTO:
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def _override_ai_client(
    result: AIHealthResponseDTO | SweepFoodAIError,
) -> None:
    async def get_fake_ai_client() -> AsyncIterator[SweepFoodAIClient]:
        yield cast(SweepFoodAIClient, _FakeAIClient(result))

    app.dependency_overrides[get_sweep_food_ai_client] = get_fake_ai_client


@pytest.mark.anyio
async def test_ai_health_returns_ready_without_authentication(
    api_client: httpx.AsyncClient,
) -> None:
    _override_ai_client(
        AIHealthResponseDTO(
            warmed_up=True,
            device_name="cpu",
            xgb_device="cpu",
            ocr_device="cpu",
        )
    )
    try:
        response = await api_client.get("/api/health/ai")
    finally:
        app.dependency_overrides.pop(get_sweep_food_ai_client, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "sweep-food-ai"
    assert payload["status"] == "ready"
    assert payload["provider"] == "SWEEP_FOOD_AI"
    assert payload["latency_ms"] >= 0


@pytest.mark.anyio
async def test_ai_health_rejects_service_that_is_still_warming_up(
    api_client: httpx.AsyncClient,
) -> None:
    _override_ai_client(
        AIHealthResponseDTO(
            warmed_up=False,
            device_name="cpu",
            xgb_device="cpu",
            ocr_device="cpu",
        )
    )
    try:
        response = await api_client.get("/api/health/ai")
    finally:
        app.dependency_overrides.pop(get_sweep_food_ai_client, None)

    assert response.status_code == 503
    assert response.json()["detail"] == "AI service is unavailable."


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (SweepFoodAIUnavailableError("offline"), 503),
        (SweepFoodAITimeoutError("slow"), 504),
        (SweepFoodAIBadResponseError("invalid"), 502),
    ],
)
async def test_ai_health_maps_client_failures(
    api_client: httpx.AsyncClient,
    error: SweepFoodAIError,
    expected_status: int,
) -> None:
    _override_ai_client(error)
    try:
        response = await api_client.get("/api/health/ai")
    finally:
        app.dependency_overrides.pop(get_sweep_food_ai_client, None)

    assert response.status_code == expected_status
    assert response.json()["path"] == "/api/health/ai"
