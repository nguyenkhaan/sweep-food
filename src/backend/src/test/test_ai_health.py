"""Integration tests for the public AI readiness endpoint."""

from types import SimpleNamespace
from typing import cast

import httpx
import pytest

from AI.catalog.errors import CatalogNotLoadedError
from AI.recommendation.engine import RecommendationEngine
from src.app import app
from src.module.recommendations.recommendation_dependency import (
    get_recommendation_engine,
)


def _fake_engine() -> RecommendationEngine:
    """Build the minimal engine surface read by the readiness endpoint."""
    engine = SimpleNamespace(
        snapshot=SimpleNamespace(revision="catalog-test", recipes=[{}, {}]),
        ranker=SimpleNamespace(
            ranker_model_name="LightGBM LambdaMART",
            model_version_string="lgbm-contextual-v3.1.0",
        ),
    )
    return cast(RecommendationEngine, engine)


@pytest.mark.anyio
async def test_ai_health_reports_loaded_catalog_without_authentication(
    api_client: httpx.AsyncClient,
) -> None:
    async def provide_engine() -> RecommendationEngine:
        return _fake_engine()

    app.dependency_overrides[get_recommendation_engine] = provide_engine
    try:
        response = await api_client.get("/api/health/ai")
    finally:
        app.dependency_overrides.pop(get_recommendation_engine, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["catalog_revision"] == "catalog-test"
    assert payload["recipe_count"] == 2
    assert payload["ranker_model"] == "LightGBM LambdaMART"
    assert payload["model_version"] == "lgbm-contextual-v3.1.0"
    assert payload["latency_ms"] >= 0


@pytest.mark.anyio
async def test_ai_health_is_unavailable_until_catalog_is_imported(
    api_client: httpx.AsyncClient,
) -> None:
    async def fail_to_load() -> RecommendationEngine:
        raise CatalogNotLoadedError()

    app.dependency_overrides[get_recommendation_engine] = fail_to_load
    try:
        response = await api_client.get("/api/health/ai")
    finally:
        app.dependency_overrides.pop(get_recommendation_engine, None)

    assert response.status_code == 503
    assert response.json()["detail"] == "AI catalog is not loaded."
    assert response.json()["path"] == "/api/health/ai"
