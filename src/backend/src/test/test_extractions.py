"""API contract tests for experimental extraction routes."""

from __future__ import annotations

from collections.abc import Generator
from io import BytesIO
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a051")


class FakeExtractionUserService:
    """Provide authenticated user for extraction routes."""


@pytest.fixture()
def _override_extraction_deps() -> Generator[None]:
    """Override authentication dependency for extraction API contract tests."""

    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[require_authentication] = get_user
    yield
    app.dependency_overrides.pop(require_authentication, None)


@pytest.mark.anyio
async def test_ocr_label_route_returns_200_with_mock_data(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/ocr/label returns mock extraction fields."""
    fake_image = BytesIO(b"\x89PNG fake image content")
    response = await api_client.post(
        "/api/extractions/ocr/label",
        files={"file": ("label.png", fake_image, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCEEDED"
    assert body["provider"] == "MOCK_OCR"
    assert body["persisted"] is False
    assert body["fields"]["ingredient_name"] == "Whole Milk"
    assert body["fields"]["quantity"] == 1.0
    assert body["fields"]["unit"] == "LITER"
    assert body["fields"]["expires_at"] == "2026-09-05"


@pytest.mark.anyio
async def test_ocr_label_rejects_invalid_image_type(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/ocr/label rejects non-image MIME types."""
    fake_file = BytesIO(b"not an image")
    response = await api_client.post(
        "/api/extractions/ocr/label",
        files={"file": ("test.exe", fake_file, "application/x-executable")},
    )
    assert response.status_code == 422
    assert "not allowed" in response.json()["detail"]


@pytest.mark.anyio
async def test_ocr_label_rejects_oversized_image(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/ocr/label rejects images exceeding size limit."""
    large_content = b"\x89PNG" + b"\x00" * 6_000_000
    fake_image = BytesIO(large_content)
    response = await api_client.post(
        "/api/extractions/ocr/label",
        files={"file": ("large.png", fake_image, "image/png")},
    )
    assert response.status_code == 422
    assert "exceeds" in response.json()["detail"]


@pytest.mark.anyio
async def test_ocr_invoice_route_returns_200_with_mock_data(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/ocr/invoice returns mock invoice line items."""
    fake_image = BytesIO(b"\x89PNG fake invoice image")
    response = await api_client.post(
        "/api/extractions/ocr/invoice",
        files={"file": ("invoice.png", fake_image, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCEEDED"
    assert body["provider"] == "MOCK_OCR"
    assert body["persisted"] is False
    assert isinstance(body["fields"]["line_items"], list)
    assert len(body["fields"]["line_items"]) == 2
    assert body["fields"]["total_amount"] == 85000.0
    assert body["fields"]["currency"] == "VND"
    assert body["fields"]["vendor_name"] == "Mock Grocery Store"


@pytest.mark.anyio
async def test_ocr_invoice_rejects_invalid_image_type(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/ocr/invoice rejects non-image MIME types."""
    fake_file = BytesIO(b"not an image")
    response = await api_client.post(
        "/api/extractions/ocr/invoice",
        files={"file": ("test.pdf", fake_file, "application/pdf")},
    )
    assert response.status_code == 422
    assert "not allowed" in response.json()["detail"]


@pytest.mark.anyio
async def test_asr_route_returns_200_with_mock_data(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/asr returns mock transcription and parsed fields."""
    fake_audio = BytesIO(b"\xff\xfb\x90\x00 fake audio content")
    response = await api_client.post(
        "/api/extractions/asr",
        files={"file": ("voice.mp3", fake_audio, "audio/mpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCEEDED"
    assert body["provider"] == "MOCK_ASR"
    assert body["persisted"] is False
    assert "milk" in body["raw_text"].lower()
    assert body["fields"]["ingredient_name"] == "Milk"
    assert body["fields"]["quantity"] == 2.0
    assert body["fields"]["unit"] == "LITER"
    assert body["confidence"]["transcript"] == 0.92


@pytest.mark.anyio
async def test_asr_rejects_invalid_audio_type(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/asr rejects non-audio MIME types."""
    fake_file = BytesIO(b"not audio")
    response = await api_client.post(
        "/api/extractions/asr",
        files={"file": ("test.txt", fake_file, "text/plain")},
    )
    assert response.status_code == 422
    assert "not allowed" in response.json()["detail"]


@pytest.mark.anyio
async def test_asr_rejects_oversized_audio(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/asr rejects audio exceeding size limit."""
    large_content = b"\xff\xfb" + b"\x00" * 11_000_000
    fake_audio = BytesIO(large_content)
    response = await api_client.post(
        "/api/extractions/asr",
        files={"file": ("large.mp3", fake_audio, "audio/mpeg")},
    )
    assert response.status_code == 422
    assert "exceeds" in response.json()["detail"]


@pytest.mark.anyio
async def test_barcode_route_returns_200_with_mock_data(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/barcode returns mock product lookup fields."""
    response = await api_client.post(
        "/api/extractions/barcode",
        params={"barcode": "8934608001004"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCEEDED"
    assert body["provider"] == "MOCK_BARCODE"
    assert body["persisted"] is False
    assert body["fields"]["barcode"] == "8934608001004"
    assert body["fields"]["product_name"] == "Whole Milk"
    assert body["fields"]["brand"] == "Dairy Farm"
    assert body["fields"]["ingredient_name"] == "Whole Milk"
    assert body["fields"]["price"] == 35000.0


@pytest.mark.anyio
async def test_barcode_openapi_uses_bearer_security() -> None:
    """Swagger exposes the protected barcode endpoint with bearer auth."""
    schema = app.openapi()
    paths = schema["paths"]
    assert isinstance(paths, dict)
    barcode_path = "/api/extractions/barcode"
    assert barcode_path in paths
    route = paths[barcode_path]
    assert isinstance(route, dict)
    post_op = route["post"]
    assert isinstance(post_op, dict)
    assert post_op["security"] == [{"BearerAuth": []}]


def test_all_extraction_openapi_paths_exist() -> None:
    """All four extraction endpoints are registered in OpenAPI."""
    schema = app.openapi()
    paths = schema["paths"]
    assert isinstance(paths, dict)
    expected_paths = [
        "/api/extractions/ocr/label",
        "/api/extractions/ocr/invoice",
        "/api/extractions/asr",
        "/api/extractions/barcode",
    ]
    for expected_path in expected_paths:
        assert expected_path in paths, f"{expected_path} missing from OpenAPI"
