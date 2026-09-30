"""Contract tests for the internal SweepFood AI HTTP client."""

from collections.abc import Callable, Coroutine

import httpx
import pytest

from src.service.sweep_food_ai_client import (
    AIPantryItemDTO,
    AIRecommendationRequestDTO,
    SweepFoodAIBadResponseError,
    SweepFoodAIClient,
    SweepFoodAITimeoutError,
    SweepFoodAIUnavailableError,
)

MockHandler = Callable[[httpx.Request], Coroutine[None, None, httpx.Response]]


def _client(handler: MockHandler) -> SweepFoodAIClient:
    return SweepFoodAIClient(transport=httpx.MockTransport(handler))


@pytest.mark.anyio
async def test_check_health_validates_ready_response() -> None:
    """GET system status returns only the readiness fields the backend uses."""

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/system/status"
        return httpx.Response(
            200,
            json={
                "warmed_up": True,
                "device_name": "CPU",
                "xgb_device": "cpu",
                "ocr_device": "cpu",
                "ignored": "value",
            },
        )

    async with _client(handler) as client:
        response = await client.check_health()

    assert response.warmed_up is True
    assert response.device_name == "CPU"


@pytest.mark.anyio
async def test_ocr_upload_uses_file_multipart_field() -> None:
    """OCR forwards the original filename, MIME type, and bytes."""

    async def handler(request: httpx.Request) -> httpx.Response:
        body = request.content
        assert request.url.path == "/api/smart-input/ocr-upload"
        assert b'name="file"; filename="label.png"' in body
        assert b"Content-Type: image/png" in body
        assert b"image-bytes" in body
        return httpx.Response(
            200,
            json={
                "status": "success",
                "source": "upload",
                "raw_text": "MILK 500G",
                "items": [
                    {
                        "name": "Milk",
                        "quantity_g": 500,
                        "quantity_source": "extracted",
                    }
                ],
            },
        )

    async with _client(handler) as client:
        response = await client.extract_ocr(
            filename="label.png",
            content=b"image-bytes",
            content_type="image/png",
        )

    assert response.items[0].name == "Milk"
    assert response.items[0].quantity_g == 500


@pytest.mark.anyio
async def test_asr_upload_uses_audio_field_and_engine() -> None:
    """ASR adapts the public file upload to AI's audio multipart contract."""

    async def handler(request: httpx.Request) -> httpx.Response:
        body = request.content
        assert request.url.path == "/api/smart-input/asr-upload"
        assert b'name="audio"; filename="voice.mp3"' in body
        assert b'name="engine"' in body
        assert b"groq_whisper" in body
        return httpx.Response(
            200,
            json={
                "status": "success",
                "engine": "groq_whisper_turbo",
                "transcript": "nam tram gram thit bo",
                "items": [
                    {
                        "name": "Thit bo",
                        "quantity_g": 500,
                        "confidence": 0.95,
                        "quantity_source": "spoken",
                    }
                ],
            },
        )

    async with _client(handler) as client:
        response = await client.extract_asr(
            filename="voice.mp3",
            content=b"audio-bytes",
            content_type="audio/mpeg",
        )

    assert response.transcript == "nam tram gram thit bo"
    assert response.items[0].quantity_source == "spoken"


@pytest.mark.anyio
async def test_recommend_posts_structured_json() -> None:
    """Recommendation sends typed pantry data and validates ranked results."""

    async def handler(request: httpx.Request) -> httpx.Response:
        payload = AIRecommendationRequestDTO.model_validate_json(request.content)
        assert request.url.path == "/api/recommend"
        assert payload.items[0].code == "ingredient-id"
        return httpx.Response(
            200,
            json={
                "status": "success",
                "model_version": "xgb-full-v1",
                "catalog_revision": "canonical-v1",
                "recommendations": [
                    {
                        "id": "018f0f90-26e6-7ce7-8f61-8769f9e5b102",
                        "name": "Soup",
                        "score": 0.8,
                        "score_components": {
                            "expiration_utilization": 0.7,
                            "availability": 0.8,
                            "preference_fit": 1.0,
                            "purchase_minimization": 0.9,
                        },
                        "missing_ingredients": [],
                        "rescued_items": ["spinach"],
                    }
                ],
            },
        )

    request = AIRecommendationRequestDTO(
        items=[
            AIPantryItemDTO(
                name="Spinach",
                code="ingredient-id",
                quantity_g=300,
                hours_to_expire=12,
            )
        ]
    )
    async with _client(handler) as client:
        response = await client.recommend(request)

    assert response.recommendations[0].name == "Soup"
    assert response.recommendations[0].score == 0.8


@pytest.mark.anyio
async def test_connection_error_becomes_unavailable() -> None:
    """Network failures are separated from upstream HTTP failures."""

    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAIUnavailableError):
            await client.check_health()


@pytest.mark.anyio
async def test_timeout_becomes_timeout_error() -> None:
    """Operation timeouts retain their own exception type."""

    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAITimeoutError):
            await client.check_health()


@pytest.mark.anyio
async def test_http_error_becomes_bad_response() -> None:
    """Upstream 4xx and 5xx responses are never exposed verbatim."""

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "secret model failure"})

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAIBadResponseError):
            await client.check_health()


@pytest.mark.anyio
async def test_invalid_json_becomes_bad_response() -> None:
    """A successful HTTP response must still contain valid JSON."""

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAIBadResponseError):
            await client.check_health()


@pytest.mark.anyio
async def test_invalid_schema_becomes_bad_response() -> None:
    """Missing required response fields are classified as contract errors."""

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"warmed_up": True})

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAIBadResponseError):
            await client.check_health()


def _recommendation_request() -> AIRecommendationRequestDTO:
    return AIRecommendationRequestDTO(
        items=[AIPantryItemDTO(name="Spinach", quantity_g=100)]
    )


@pytest.mark.anyio
async def test_recommend_accepts_an_empty_result() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "status": "empty",
                "model_version": "xgb-full-v1",
                "catalog_revision": "canonical-v1",
                "recommendations": [],
            },
        )

    async with _client(handler) as client:
        response = await client.recommend(_recommendation_request())

    assert response.status == "empty"
    assert response.recommendations == []


@pytest.mark.anyio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "status": "success",
            "model_version": "xgb-full-v1",
            "catalog_revision": "canonical-v1",
            "recommendations": [
                {
                    "id": "not-a-uuid",
                    "name": "Soup",
                    "score": 0.8,
                    "score_components": {
                        "expiration_utilization": 0.7,
                        "availability": 0.8,
                        "preference_fit": 1.0,
                        "purchase_minimization": 0.9,
                    },
                    "missing_ingredients": [],
                    "rescued_items": [],
                }
            ],
        },
        {
            "status": "success",
            "model_version": "xgb-full-v1",
            "catalog_revision": "canonical-v1",
            "recommendations": [
                {
                    "id": "018f0f90-26e6-7ce7-8f61-8769f9e5b102",
                    "name": "Soup",
                    "score_components": {},
                    "missing_ingredients": [],
                    "rescued_items": [],
                }
            ],
        },
    ],
)
async def test_recommend_rejects_malformed_rankings(
    payload: dict[str, object],
) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAIBadResponseError):
            await client.recommend(_recommendation_request())


@pytest.mark.anyio
async def test_recommend_timeout_uses_recommendation_error_mapping() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAITimeoutError):
            await client.recommend(_recommendation_request())


@pytest.mark.anyio
async def test_recommend_upstream_error_is_bad_response() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "unavailable"})

    async with _client(handler) as client:
        with pytest.raises(SweepFoodAIBadResponseError):
            await client.recommend(_recommendation_request())
