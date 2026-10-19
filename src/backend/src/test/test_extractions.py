"""API contract tests for experimental extraction routes."""

from __future__ import annotations

import json
from collections.abc import Generator
from io import BytesIO
from typing import Any
from uuid import UUID

import httpx
import pytest
from PIL import Image

from AI.extraction.asr.groq_whisper import GroqWhisperClient
from AI.extraction.ocr.image_guard import (
    GuardVerdict,
    ImageCategory,
    OpenAIImageGuard,
)
from AI.extraction.ocr.openai_vision_ocr import OpenAIVisionOCR
from AI.extraction.service import AIExtractionService
from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.extractions.extraction_dependency import get_extraction_service
from src.module.extractions.extraction_service import ExtractionService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a051")
MILK_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a0a1")


class _MasterRows:
    """Rows returned by the fake master-ingredient lookup."""

    def __init__(self, rows: list[tuple[str, UUID]]) -> None:
        self._rows = rows

    def all(self) -> list[tuple[str, UUID]]:
        return self._rows


class FakeMasterSession:
    """Resolve only the Milk catalog code, as the master_ingredients table would."""

    async def execute(self, _statement: object) -> _MasterRows:
        return _MasterRows([("10001", MILK_ID)])


def make_extraction_service(ai_service: Any) -> ExtractionService:
    """Build the service with a fake master lookup and a stubbed AI service."""
    return ExtractionService(FakeMasterSession(), ai_service=ai_service)  # type: ignore[arg-type]


class AcceptingGuard:
    """Image guard stub that accepts every image."""

    async def classify(self, image_bytes: bytes) -> GuardVerdict:
        del image_bytes
        return GuardVerdict(ImageCategory.FOOD_LABEL, 0.99, "")


class RejectingGuard:
    """Image guard stub that rejects every image."""

    async def classify(self, image_bytes: bytes) -> GuardVerdict:
        del image_bytes
        return GuardVerdict(ImageCategory.OTHER, 0.97, "Ảnh chụp phong cảnh.")


class FakeAIExtractionService:
    """Return deterministic extraction results without network access."""

    async def process_receipt_input(
        self,
        image_bytes: bytes,
        filename: str = "receipt.jpg",
    ) -> dict[str, Any]:
        del image_bytes
        if "invoice" in filename:
            return {
                "status": "success",
                "source": "receipt",
                "store_name": "Test Grocery",
                "raw_text": "Milk 500g\nBread",
                "items": [
                    {
                        "name": "Whole Milk",
                        "raw_name": "MILK",
                        "code": "10001",
                        "category": "Dairy",
                        "quantity_g": 500.0,
                        "quantity_source": "extracted",
                        "nutrition": {"energy_kcal": 74.0},
                        "freshness_guide": {"storage_tips": ["Keep cold"]},
                        "is_staple": False,
                    },
                    {
                        "name": "Bread",
                        "raw_name": "BREAD",
                        "code": "20001",
                        "category": "Grains",
                        "quantity_g": 250.0,
                        "quantity_source": "estimated",
                        "is_staple": False,
                    },
                ],
            }
        if "suspicious" in filename:
            return {
                "status": "success",
                "source": "label",
                "raw_text": "KLT: 0.296 kg\nNSX: 01/10/2026\nHSD: 04/10/2026",
                "items": [
                    {
                        "name": "Ground Pork",
                        "raw_name": "THIT HEO XAY",
                        "code": "20002",
                        "category": "Meat",
                        "quantity_g": 296.0,
                        "quantity_source": "extracted",
                        "production_date": "01/10/2026",
                        "expiry_date": "04/10/2026",
                        "expiry_check": "suspicious",
                        "confidence": 0.95,
                        "is_staple": False,
                    }
                ],
            }
        return {
            "status": "success",
            "source": "label",
            "raw_text": "Milk 500g",
            "items": [
                {
                    "name": "Whole Milk",
                    "raw_name": "MILK",
                    "code": "10001",
                    "category": "Dairy",
                    "quantity_g": 500.0,
                    "quantity_source": "extracted",
                    "production_date": "28/08/2026",
                    "expiry_date": "05/09/2026",
                    "confidence": 0.95,
                    "nutrition": {"energy_kcal": 74.0},
                    "freshness_guide": {"storage_tips": ["Keep cold"]},
                    "is_staple": False,
                }
            ],
        }

    async def process_voice_input(
        self,
        audio_bytes: bytes | None = None,
        transcript: str | None = None,
        filename: str = "audio.wav",
    ) -> dict[str, Any]:
        del audio_bytes, transcript, filename
        return {
            "status": "success",
            "engine": "groq_whisper_turbo",
            "transcript": "năm trăm gram sữa tươi",
            "items": [
                {
                    "name": "Milk",
                    "raw_name": "sữa",
                    "code": "10001",
                    "category": "Dairy",
                    "quantity_g": 500.0,
                    "quantity_source": "extracted",
                    "confidence": 0.92,
                    "nutrition": {"energy_kcal": 74.0},
                    "freshness_guide": {"storage_tips": ["Keep cold"]},
                    "is_staple": False,
                }
            ],
        }

    async def process_text_input(self, text: str) -> dict[str, Any]:
        """Resolve typed text to one catalog item plus a second omitted item."""
        return {
            "status": "success",
            "engine": "smart_parser",
            "text": text,
            "items": [
                {
                    "name": "Milk",
                    "raw_name": "sua tuoi",
                    "code": "10001",
                    "quantity_g": 200.0,
                    "quantity_source": "estimated",
                    "confidence": 0.95,
                },
                {"name": "Bread", "raw_name": "banh mi", "code": None},
            ],
        }


@pytest.fixture()
def _override_extraction_deps() -> Generator[None]:
    """Override authentication and extraction service dependency for contract tests."""

    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def get_fake_service() -> ExtractionService:
        return make_extraction_service(FakeAIExtractionService())

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = get_fake_service
    yield
    app.dependency_overrides.pop(require_authentication, None)
    app.dependency_overrides.pop(get_extraction_service, None)


@pytest.mark.anyio
async def test_ocr_label_route_returns_200_with_mock_data(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/ocr/label maps a typed AI response."""
    fake_image = BytesIO(b"\x89PNG fake image content")
    response = await api_client.post(
        "/api/extractions/ocr/label",
        files={"file": ("label.png", fake_image, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCEEDED"
    assert body["provider"] == "SWEEP_FOOD_AI"
    assert body["persisted"] is False
    assert body["fields"]["ingredient_name"] == "Whole Milk"
    assert body["fields"]["raw_name"] == "MILK"
    assert body["fields"]["master_ingredient_id"] == str(MILK_ID)
    assert set(body["fields"]) == {
        "ingredient_name",
        "raw_name",
        "master_ingredient_id",
        "quantity",
        "unit",
        "packaged_at",
        "expires_at",
    }
    assert body["fields"]["quantity"] == 500.0
    assert body["fields"]["unit"] == "GRAM"
    assert body["fields"]["packaged_at"] == "2026-08-28"
    assert body["fields"]["expires_at"] == "2026-09-05"
    assert body["confidence"]["ingredient_name"] == 0.95
    assert body["warnings"] == []


@pytest.mark.anyio
async def test_ocr_label_warns_when_ai_flags_suspicious_expiry(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """A flagged HSD is kept as read but surfaced as a warning."""
    fake_image = BytesIO(b"\x89PNG fake image content")
    response = await api_client.post(
        "/api/extractions/ocr/label",
        files={"file": ("suspicious.png", fake_image, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIAL"
    assert body["fields"]["expires_at"] == "2026-10-04"
    assert body["warnings"] == ["EXPIRY_DATE_SUSPICIOUS"]


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
    """POST /extractions/ocr/invoice returns an honest partial result."""
    fake_image = BytesIO(b"\x89PNG fake invoice image")
    response = await api_client.post(
        "/api/extractions/ocr/invoice",
        files={"file": ("invoice.png", fake_image, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIAL"
    assert body["provider"] == "SWEEP_FOOD_AI"
    assert body["persisted"] is False
    assert isinstance(body["fields"]["line_items"], list)
    assert len(body["fields"]["line_items"]) == 2
    assert body["fields"]["line_items"][0]["master_ingredient_id"] == str(MILK_ID)
    assert body["fields"]["line_items"][1]["master_ingredient_id"] is None
    assert set(body["fields"]["line_items"][0]) == {
        "name",
        "raw_name",
        "master_ingredient_id",
        "quantity",
        "unit",
        "unit_price",
        "total_price",
    }
    assert body["fields"]["line_items"][0]["name"] == "Whole Milk"
    assert body["fields"]["line_items"][0]["raw_name"] == "MILK"
    assert body["fields"]["line_items"][0]["quantity"] == 500.0
    assert body["fields"]["line_items"][1]["quantity"] is None
    assert body["fields"]["total_amount"] is None
    assert body["fields"]["currency"] is None
    assert body["fields"]["vendor_name"] == "Test Grocery"
    assert "INVOICE_FINANCIAL_FIELDS_NOT_AVAILABLE" in body["warnings"]


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
    """POST /extractions/asr maps the first typed AI item."""
    fake_audio = BytesIO(b"\xff\xfb\x90\x00 fake audio content")
    response = await api_client.post(
        "/api/extractions/asr",
        files={"file": ("voice.mp3", fake_audio, "audio/mpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCEEDED"
    assert body["provider"] == "SWEEP_FOOD_AI"
    assert body["persisted"] is False
    assert "sữa" in body["raw_text"].lower()
    assert body["fields"]["ingredient_name"] == "Milk"
    assert body["fields"]["raw_name"] == "sữa"
    assert body["fields"]["master_ingredient_id"] == str(MILK_ID)
    assert set(body["fields"]) == {
        "ingredient_name",
        "raw_name",
        "master_ingredient_id",
        "quantity",
        "unit",
        "packaged_at",
        "expires_at",
    }
    assert body["fields"]["quantity"] == 500.0
    assert body["fields"]["unit"] == "GRAM"
    assert body["confidence"]["ingredient_name"] == 0.92


@pytest.mark.anyio
async def test_text_route_returns_matched_ingredient_without_estimated_quantity(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
) -> None:
    """POST /extractions/text keeps the catalog match but never reports a guessed quantity."""
    response = await api_client.post(
        "/api/extractions/text", json={"text": "  sua tuoi  "}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIAL"
    assert body["raw_text"] == "sua tuoi"
    assert body["fields"]["ingredient_name"] == "Milk"
    assert body["fields"]["master_ingredient_id"] == str(MILK_ID)
    assert body["fields"]["quantity"] is None
    assert body["fields"]["unit"] is None
    assert body["warnings"] == ["ADDITIONAL_ITEMS_OMITTED", "QUANTITY_NOT_EXTRACTED"]


@pytest.mark.anyio
@pytest.mark.parametrize("payload", [{"text": "   "}, {"text": "x" * 501}, {}])
async def test_text_route_rejects_blank_oversized_or_missing_text(
    api_client: httpx.AsyncClient,
    _override_extraction_deps: None,
    payload: dict[str, str],
) -> None:
    """The text endpoint bounds its input before reaching the smart parser."""
    response = await api_client.post("/api/extractions/text", json=payload)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_text_route_runs_the_real_smart_parser(
    api_client: httpx.AsyncClient,
) -> None:
    """Typed text with a quantity resolves through the bundled catalog parser."""
    from AI.catalog.snapshot import load_snapshot_from_bundle
    from AI.extraction.pantry_parser import CatalogPantryParser

    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    snapshot = load_snapshot_from_bundle()
    ai_service = AIExtractionService(
        pantry_parser=CatalogPantryParser(
            master_alias_index=snapshot.master_alias_index,
            master_by_code=snapshot.master_by_code,
        )
    )
    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )
    try:
        response = await api_client.post(
            "/api/extractions/text", json={"text": "thịt ba rọi 500g"}
        )
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)

    assert response.status_code == 200
    fields = response.json()["fields"]
    assert "ba chỉ" in fields["ingredient_name"].lower()
    assert fields["raw_name"]
    assert fields["quantity"] == 500.0
    assert fields["unit"] == "GRAM"


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


# =========================================================================
# MockTransport-backed Route Tests (OpenAI OCR & Groq Whisper Error Mapping)
# =========================================================================


@pytest.mark.anyio
async def test_ocr_label_route_openai_success(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/ocr/label returns 200 with MockTransport OpenAI response."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    mock_resp = {
        "choices": [
            {
                "message": {
                    "content": (
                        '{"store_name": "Bách Hóa Xanh", "raw_text": "Cải thìa 500g", '
                        '"items": [{"name": "Cải thìa", "quantity_g": 500.0, "expiry_date": "20/12/2026"}]}'
                    )
                }
            }
        ]
    }

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=mock_resp)
    )
    mock_client = httpx.AsyncClient(transport=mock_transport)
    ocr_client = OpenAIVisionOCR(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(ocr_client=ocr_client, image_guard=AcceptingGuard())  # type: ignore[arg-type]
    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_img = BytesIO(b"\x89PNG test image")
        resp = await api_client.post(
            "/api/extractions/ocr/label",
            files={"file": ("label.png", fake_img, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("SUCCEEDED", "PARTIAL")
        assert data["fields"]["ingredient_name"] == "Cải thìa"
        assert data["fields"]["quantity"] == 500.0
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


def _png_bytes() -> bytes:
    """Return a tiny valid PNG so image preprocessing succeeds."""
    buffer = BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("effort", "expected"),
    [(None, "medium"), ("high", "high"), ("", None)],
)
async def test_ocr_sends_reasoning_effort_only_when_configured(
    effort: str | None,
    expected: str | None,
) -> None:
    """OCR defaults to medium reasoning; an empty value omits it for non-reasoning models."""
    bodies: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"raw_text": "x", "items": []}'}}]},
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    ocr = OpenAIVisionOCR(
        api_key="test-key",
        model="gpt-6.1-sol",
        reasoning_effort=effort,
        http_client=http_client,
    )
    try:
        await ocr.recognize_image_bytes(_png_bytes())
    finally:
        await http_client.aclose()

    assert bodies[0]["model"] == "gpt-6.1-sol"
    assert bodies[0].get("reasoning_effort") == expected
    assert "max_tokens" not in bodies[0]
    assert "temperature" not in bodies[0]

@pytest.mark.anyio
async def test_ocr_label_route_openai_timeout_maps_to_504(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/ocr/label maps OpenAI timeout to HTTP 504."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def timeout_handler(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Request timed out", request=req)

    mock_transport = httpx.MockTransport(timeout_handler)
    mock_client = httpx.AsyncClient(transport=mock_transport)
    ocr_client = OpenAIVisionOCR(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(ocr_client=ocr_client, image_guard=AcceptingGuard())  # type: ignore[arg-type]

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_img = BytesIO(b"\x89PNG test image")
        resp = await api_client.post(
            "/api/extractions/ocr/label",
            files={"file": ("label.png", fake_img, "image/png")},
        )
        assert resp.status_code == 504
        assert "timed out" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


@pytest.mark.anyio
async def test_ocr_label_route_openai_service_unavailable_maps_to_503(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/ocr/label maps 503 or connect error to HTTP 503."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def error_handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="Service Unavailable", request=req)

    mock_transport = httpx.MockTransport(error_handler)
    mock_client = httpx.AsyncClient(transport=mock_transport)
    ocr_client = OpenAIVisionOCR(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(ocr_client=ocr_client, image_guard=AcceptingGuard())  # type: ignore[arg-type]

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_img = BytesIO(b"\x89PNG test image")
        resp = await api_client.post(
            "/api/extractions/ocr/label",
            files={"file": ("label.png", fake_img, "image/png")},
        )
        assert resp.status_code == 503
        assert "unavailable" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


@pytest.mark.anyio
async def test_ocr_label_route_openai_bad_response_maps_to_502(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/ocr/label maps malformed response to HTTP 502."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def bad_response_handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Server Error", request=req)

    mock_transport = httpx.MockTransport(bad_response_handler)
    mock_client = httpx.AsyncClient(transport=mock_transport)
    ocr_client = OpenAIVisionOCR(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(ocr_client=ocr_client, image_guard=AcceptingGuard())  # type: ignore[arg-type]

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_img = BytesIO(b"\x89PNG test image")
        resp = await api_client.post(
            "/api/extractions/ocr/label",
            files={"file": ("label.png", fake_img, "image/png")},
        )
        assert resp.status_code == 502
        assert "invalid" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


@pytest.mark.anyio
async def test_asr_route_whisper_success(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/asr returns 200 with MockTransport Whisper response."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(
            200, json={"text": "Tôi vừa mua nửa cân thịt bò tươi"}
        )
    )
    mock_client = httpx.AsyncClient(transport=mock_transport)
    whisper_client = GroqWhisperClient(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(whisper_client=whisper_client)

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_audio = BytesIO(b"\xff\xfb\x90 audio bytes")
        resp = await api_client.post(
            "/api/extractions/asr",
            files={"file": ("voice.mp3", fake_audio, "audio/mpeg")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in ("SUCCEEDED", "PARTIAL")
        assert body["fields"]["ingredient_name"] == "Thịt bò"
        assert body["fields"]["quantity"] == 500.0
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


@pytest.mark.anyio
async def test_asr_route_whisper_timeout_maps_to_504(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/asr maps Groq Whisper timeout to HTTP 504."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def timeout_handler(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Whisper timed out", request=req)

    mock_transport = httpx.MockTransport(timeout_handler)
    mock_client = httpx.AsyncClient(transport=mock_transport)
    whisper_client = GroqWhisperClient(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(whisper_client=whisper_client)

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_audio = BytesIO(b"\xff\xfb\x90 audio bytes")
        resp = await api_client.post(
            "/api/extractions/asr",
            files={"file": ("voice.mp3", fake_audio, "audio/mpeg")},
        )
        assert resp.status_code == 504
        assert "timed out" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


@pytest.mark.anyio
async def test_asr_route_whisper_unavailable_maps_to_503(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/asr maps Groq 503 or connect failure to HTTP 503."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(503, text="Groq Unavailable", request=req)
    )
    mock_client = httpx.AsyncClient(transport=mock_transport)
    whisper_client = GroqWhisperClient(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(whisper_client=whisper_client)

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_audio = BytesIO(b"\xff\xfb\x90 audio bytes")
        resp = await api_client.post(
            "/api/extractions/asr",
            files={"file": ("voice.mp3", fake_audio, "audio/mpeg")},
        )
        assert resp.status_code == 503
        assert "unavailable" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


@pytest.mark.anyio
async def test_asr_route_whisper_bad_response_maps_to_502(
    api_client: httpx.AsyncClient,
) -> None:
    """POST /extractions/asr maps malformed Whisper JSON to HTTP 502."""
    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, text="not valid json", request=req)
    )
    mock_client = httpx.AsyncClient(transport=mock_transport)
    whisper_client = GroqWhisperClient(
        api_key="test-key", http_client=mock_client
    )
    ai_service = AIExtractionService(whisper_client=whisper_client)

    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )

    try:
        fake_audio = BytesIO(b"\xff\xfb\x90 audio bytes")
        resp = await api_client.post(
            "/api/extractions/asr",
            files={"file": ("voice.mp3", fake_audio, "audio/mpeg")},
        )
        assert resp.status_code == 502
        assert "invalid" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await mock_client.aclose()


# =========================================================================
# Parser Tests on Reference Sample Strings (Receipt, Label, Speech, Pantry)
# =========================================================================


def test_receipt_parser_on_sample_receipt() -> None:
    """Receipt parser extracts items, weights, and filters out non-food lines."""
    from AI.extraction.ocr.receipt_parser import parse_receipt_text

    sample_receipt = (
        "WINMART+ 124 NGUYEN THI THAP\n"
        "1. THIT BO UC NHAP   0.45 kg 280,000 126,000\n"
        "2. CA DIEU HONG LAM SACH 0.70 kg 85,000 59,500\n"
        "3. RAU MUONG NUOC 500G 1.00 go 15,000  15,000\n"
        "4. CA CHUA DA LAT    0.35 kg  32,000  11,200\n"
        "5. TOI CO DON VIET   0.15 kg  90,000  13,500\n"
        "6. NUOC RUA CHEN SUNLIGHT 1.00 chai 35,000 35,000\n"
    )
    items = parse_receipt_text(sample_receipt)
    assert len(items) == 5
    names = [it["name"] for it in items]
    assert "Thịt bò" in names
    assert "Cá điêu hồng" in names
    assert "Rau muống" in names
    assert "Cà chua" in names
    assert "Tỏi" in names
    # Check weight extraction
    beef = next(it for it in items if it["name"] == "Thịt bò")
    assert beef["quantity_g"] == 450.0
    assert beef["quantity_source"] == "extracted"


def test_label_parser_on_sample_label() -> None:
    """Label parser extracts product name, weight, and expiry date."""
    from AI.extraction.ocr.label_parser import FoodLabelParser

    sample_label = (
        "SIEU THI BACH HOA XANH\n"
        "CAI THIA SACH DA LAT VIETGAP\n"
        "KLT: 500g\n"
        "NSX: 05/09/2026\n"
        "HSD: 09/09/2026\n"
        "DON GIA: 26,000 D/KG\n"
    )
    parser = FoodLabelParser()
    res = parser.parse_label_text(sample_label)
    assert "CAI THIA SACH" in res["name"]
    assert res["quantity_g"] == 500.0
    assert res["quantity_source"] == "extracted"
    assert res["expiry_date"] == "09/09/2026"
    assert res["production_date"] == "05/09/2026"


def test_speech_parser_on_sample_voice() -> None:
    """Speech parser extracts culinary items with quantities from spoken Vietnamese."""
    from AI.extraction.asr.speech_parser import parse_vietnamese_speech

    transcript = "Hôm nay tôi vừa đi chợ mua nửa cân thịt bò và hai lạng tỏi với một bó hành lá."
    items = parse_vietnamese_speech(transcript)
    assert len(items) == 3
    names = [it["name"] for it in items]
    assert "Thịt bò" in names
    assert "Tỏi" in names
    assert "Hành lá" in names
    beef = next(it for it in items if it["name"] == "Thịt bò")
    assert beef["quantity_g"] == 500.0
    assert beef["quantity_source"] == "extracted"
    garlic = next(it for it in items if it["name"] == "Tỏi")
    assert garlic["quantity_g"] == 200.0
    assert garlic["quantity_source"] == "extracted"


def test_pantry_parser_master_code_matching_and_enrichment() -> None:
    """CatalogPantryParser matches items against bundle catalog and enriches nutrition."""
    from AI.catalog.snapshot import load_snapshot_from_bundle
    from AI.extraction.pantry_parser import CatalogPantryParser

    snapshot = load_snapshot_from_bundle()
    parser = CatalogPantryParser(
        master_alias_index=snapshot.master_alias_index,
        master_by_code=snapshot.master_by_code,
    )
    matched = parser.resolve_master_ingredient("Thịt bò")
    assert matched is not None
    assert matched["code"] == "20362"
    assert matched["category"] == "Thịt và sản phẩm chế biến"
    assert matched["nutrition"] is not None
    assert matched["nutrition"]["energy_kcal"] > 0

    enriched = parser.enrich_item(
        {"name": "0.5kg thịt bò tươi", "quantity_g": 500.0, "quantity_source": "extracted"}
    )
    assert enriched["code"] == "20362"
    assert enriched["quantity_g"] == 500.0
    assert enriched["quantity_source"] == "extracted"
    assert enriched["nutrition"] is not None


# =========================================================================
# Pre-OCR image guard
# =========================================================================


def _guard_with_reply(content: str) -> tuple[OpenAIImageGuard, httpx.AsyncClient]:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(
            200, json={"choices": [{"message": {"content": content}}]}
        )
    )
    client = httpx.AsyncClient(transport=transport)
    return OpenAIImageGuard(api_key="test-key", http_client=client), client


def _png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("category", "accepted"),
    [("food_label", True), ("invoice", True), ("other", False)],
)
async def test_image_guard_accepts_only_labels_and_invoices(
    category: str, accepted: bool
) -> None:
    """Only food labels and invoices pass; everything else is rejected."""
    guard, client = _guard_with_reply(
        json.dumps({"category": category, "confidence": 0.9, "reason": "r"})
    )
    try:
        verdict = await guard.classify(_png_bytes())
    finally:
        await client.aclose()
    assert verdict.accepted is accepted


@pytest.mark.anyio
async def test_image_guard_unknown_category_is_a_provider_error() -> None:
    """An unparseable verdict never silently lets an image through."""
    from AI.errors import ExtractionBadResponseError

    guard, client = _guard_with_reply('{"category": "maybe"}')
    try:
        with pytest.raises(ExtractionBadResponseError):
            await guard.classify(_png_bytes())
    finally:
        await client.aclose()


@pytest.mark.anyio
@pytest.mark.parametrize("path", ["label", "invoice"])
async def test_rejected_image_returns_422_and_never_calls_ocr(
    api_client: httpx.AsyncClient, path: str
) -> None:
    """A non-food, non-invoice image gets 422 and the OCR model is not called."""
    ocr_calls: list[httpx.Request] = []

    def ocr_handler(request: httpx.Request) -> httpx.Response:
        ocr_calls.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    async def get_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    ocr_http = httpx.AsyncClient(transport=httpx.MockTransport(ocr_handler))
    ai_service = AIExtractionService(
        ocr_client=OpenAIVisionOCR(api_key="test-key", http_client=ocr_http),
        image_guard=RejectingGuard(),  # type: ignore[arg-type]
    )
    app.dependency_overrides[require_authentication] = get_user
    app.dependency_overrides[get_extraction_service] = lambda: (
        make_extraction_service(ai_service)
    )
    try:
        resp = await api_client.post(
            f"/api/extractions/ocr/{path}",
            files={"file": ("photo.png", BytesIO(_png_bytes()), "image/png")},
        )
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_extraction_service, None)
        await ocr_http.aclose()
    assert resp.status_code == 422
    assert "phong cảnh" in resp.json()["detail"]
    assert ocr_calls == []
