"""Focused unit tests for AI.smart_parser and shared AI.llm.OpenAIClient."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import httpx
import pytest

from AI.catalog.snapshot import load_snapshot_from_bundle
from AI.errors import (
    ExtractionBadResponseError,
    ExtractionTimeoutError,
    ExtractionUnavailableError,
)
from AI.llm.openai_client import OpenAIClient
from AI.smart_parser import PantryParser, get_pantry_parser


@pytest.mark.anyio
async def test_openai_client_request_shape_and_success() -> None:
    """OpenAIClient correctly builds payload with model, json_object, and headers."""
    recorded_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        body = json.loads(request.content.decode("utf-8"))
        assert body["model"] == "gpt-4o-mini"
        assert body["response_format"] == {"type": "json_object"}
        # Reasoning models (e.g. gpt-6.1-sol) reject `max_tokens` and any non-default temperature.
        assert body["max_completion_tokens"] == 4096
        assert "max_tokens" not in body
        assert "temperature" not in body
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"

        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"result": "success", "count": 1})
                        }
                    }
                ]
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = OpenAIClient(
        api_key="sk-test-secret-key-12345",
        model="gpt-4o-mini",
        http_client=mock_client,
    )

    data = await client.create_chat_completion_json(
        messages=[{"role": "user", "content": "Extract items"}],
    )
    assert data == {"result": "success", "count": 1}
    assert len(recorded_requests) == 1
    req = recorded_requests[0]
    assert req.headers["authorization"] == "Bearer sk-test-secret-key-12345"
    assert req.headers["content-type"] == "application/json"
    assert req.url.path.endswith("/chat/completions")


@pytest.mark.anyio
async def test_openai_client_retry_429_with_backoff() -> None:
    """OpenAIClient retries bounded on HTTP 429 and succeeds on subsequent attempt."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(
                429,
                headers={"retry-after": "0.01"},
                json={"error": {"message": "Rate limit exceeded"}},
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"retried": True})
                        }
                    }
                ]
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = OpenAIClient(
        api_key="sk-test-key",
        max_retries=2,
        backoff_factor=0.01,
        http_client=mock_client,
    )

    data = await client.create_chat_completion_json(
        messages=[{"role": "user", "content": "test retry"}]
    )
    assert attempts == 2
    assert data == {"retried": True}


@pytest.mark.anyio
async def test_openai_client_timeout_mapping() -> None:
    """OpenAIClient maps httpx.TimeoutException to ExtractionTimeoutError."""
    def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Read timed out", request=request)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler))
    client = OpenAIClient(
        api_key="sk-test-key",
        max_retries=1,
        backoff_factor=0.01,
        http_client=mock_client,
    )

    with pytest.raises(ExtractionTimeoutError) as exc_info:
        await client.create_chat_completion_json(
            messages=[{"role": "user", "content": "timeout test"}]
        )
    assert "timed out" in str(exc_info.value).lower()


@pytest.mark.anyio
async def test_openai_client_error_mappings() -> None:
    """OpenAIClient maps HTTP 503 to ExtractionUnavailableError and 500 to ExtractionBadResponseError."""
    # 503
    mock_client_503 = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda req: httpx.Response(503, text="Unavailable"))
    )
    client_503 = OpenAIClient(
        api_key="sk-test",
        max_retries=1,
        backoff_factor=0.01,
        http_client=mock_client_503,
    )
    with pytest.raises(ExtractionUnavailableError):
        await client_503.create_chat_completion_json(messages=[{"role": "user", "content": "hi"}])

    # 500
    mock_client_500 = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda req: httpx.Response(500, text="Internal Error"))
    )
    client_500 = OpenAIClient(
        api_key="sk-test",
        max_retries=1,
        backoff_factor=0.01,
        http_client=mock_client_500,
    )
    with pytest.raises(ExtractionBadResponseError):
        await client_500.create_chat_completion_json(messages=[{"role": "user", "content": "hi"}])


def test_smart_parser_tiers_1_2_4_reference_sentences() -> None:
    """Tiers 1/2/4 correctly parse and enrich reference sentences using bundle data."""
    snapshot = load_snapshot_from_bundle()
    parser = PantryParser(
        master_alias_index=snapshot.master_alias_index,
        master_by_code=snapshot.master_by_code,
    )

    # 1. Complex Vietnamese speech sentence with 2 ingredients and storage intent
    speech = "hôm nay mua nửa cân thịt ba rọi với 3 quả cà chua để ngăn mát"
    items = parser.parse_input_to_pantry(speech, prefer_llm=False)
    assert len(items) == 2

    # Item 1: Thịt ba rọi -> resolved to Thịt ba chỉ
    item_pork = items[0]
    assert "thịt ba chỉ" in item_pork["name"].lower() or "ba chỉ" in item_pork["name"].lower()
    assert item_pork["code"] == "7018"
    assert item_pork["quantity_g"] == 500.0
    assert item_pork["storage_mode"] == "fridge_2_4c"
    assert item_pork["hours_to_expire"] > 0
    assert item_pork["nutrition"] is not None
    assert item_pork["nutrition"]["energy_kcal"] > 0
    assert item_pork["freshness_guide"] is not None
    assert "archetype" in item_pork["freshness_guide"]

    # Item 2: 3 quả cà chua -> estimated weight 3 * 75 = 225g
    item_tomato = items[1]
    assert "cà chua" in item_tomato["name"].lower()
    assert item_tomato["quantity_g"] == 225.0
    assert item_tomato["storage_mode"] == "fridge_2_4c"
    assert item_tomato["hours_to_expire"] > 0

    # 2. Regional aliases test cases from reference demo.py
    aliases_tests = [
        ("ba rọi rút sườn 400g", "7018", 400.0),
        ("cá lóc 1 con", "8022", 700.0),
        ("tàu hũ non 2 bìa", None, 300.0),
        ("ngao sống 1 kg", None, 1000.0),
    ]

    for raw, expected_code, expected_qty in aliases_tests:
        res = parser.parse_input_to_pantry(raw, prefer_llm=False)
        assert len(res) == 1
        it = res[0]
        if expected_code:
            assert it["code"] == expected_code
        assert it["quantity_g"] == expected_qty
        assert it["hours_to_expire"] > 0
        assert "freshness_guide" in it


def test_smart_parser_multiline_receipt_fallback() -> None:
    """Tiers 1/2/4 fallback accurately splits multi-line supermarket receipts."""
    snapshot = load_snapshot_from_bundle()
    parser = PantryParser(
        master_alias_index=snapshot.master_alias_index,
        master_by_code=snapshot.master_by_code,
    )

    ocr_sample = """
    1. THIT HEO XAY CP KHAY 300G     45.000d
    2. CA DIEU HONG LS 0.70 kg       59.500d
    3. BO RAU MUONG NUOC 500G        15.000d
    4. TUI 10 QUA TRUNG GA TA        32.000d
    """
    items = parser.parse_input_to_pantry(ocr_sample, prefer_llm=False)
    assert len(items) == 4

    assert items[0]["quantity_g"] == 300.0
    assert items[1]["quantity_g"] == 700.0
    assert items[2]["quantity_g"] == 500.0
    assert items[3]["quantity_g"] == 600.0

    for it in items:
        assert it["hours_to_expire"] > 0
        assert it["storage_mode"] == "fridge_2_4c"


@pytest.mark.anyio
async def test_smart_parser_llm_tier_success_with_mock_transport() -> None:
    """LLM tier extracts items and enriches them when OpenAI mock returns structured JSON."""
    snapshot = load_snapshot_from_bundle()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "items": [
                                        {
                                            "name": "thịt ba chỉ",
                                            "quantity_g": 500.0,
                                            "storage_mode": "freezer_-18c",
                                        },
                                        {
                                            "name": "cà chua",
                                            "quantity_g": 225.0,
                                            "storage_mode": "fridge_2_4c",
                                        },
                                    ]
                                }
                            )
                        }
                    }
                ]
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    openai_client = OpenAIClient(api_key="sk-test", http_client=mock_client)

    parser = PantryParser(
        master_alias_index=snapshot.master_alias_index,
        master_by_code=snapshot.master_by_code,
        openai_client=openai_client,
    )

    items = await parser.aparse_input_to_pantry(
        "mua nửa cân thịt ba rọi và 3 quả cà chua", prefer_llm=True
    )
    assert len(items) == 2
    assert items[0]["code"] == "7018"
    assert items[0]["storage_mode"] == "freezer_-18c"
    # Freezer shelf life is longer than fridge
    assert items[0]["hours_to_expire"] > 72.0
    assert items[1]["quantity_g"] == 225.0


@pytest.mark.anyio
@pytest.mark.parametrize(
    "error_mode",
    ["429", "timeout", "malformed_json", "missing_key"],
)
async def test_smart_parser_llm_tier_graceful_degradation(error_mode: str) -> None:
    """LLM tier degrades gracefully to Tier 4 on 429, timeout, malformed JSON, and missing keys."""
    snapshot = load_snapshot_from_bundle()

    def handler(request: httpx.Request) -> httpx.Response:
        if error_mode == "429":
            return httpx.Response(429, json={"error": "rate limit"})
        elif error_mode == "timeout":
            raise httpx.ReadTimeout("Timeout", request=request)
        elif error_mode == "malformed_json":
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "not valid json {["}}]},
            )
        else:  # missing_key
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": json.dumps({"unexpected": "structure"})}}]},
            )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    openai_client = OpenAIClient(
        api_key="sk-test",
        max_retries=0,  # Fast fail to trigger degradation
        http_client=mock_client,
    )

    parser = PantryParser(
        master_alias_index=snapshot.master_alias_index,
        master_by_code=snapshot.master_by_code,
        openai_client=openai_client,
    )

    # Input has complex indicators that trigger prefer_llm
    input_text = "hôm nay mua nửa cân thịt ba rọi với 3 quả cà chua để ngăn mát"
    items = await parser.aparse_input_to_pantry(input_text, prefer_llm=True)

    # Fallback to Tier 4 produces valid, sane extracted items without raising
    assert len(items) == 2
    assert "thịt ba chỉ" in items[0]["name"].lower() or "ba chỉ" in items[0]["name"].lower()
    assert items[0]["quantity_g"] == 500.0
    assert items[0]["hours_to_expire"] > 0
    assert "cà chua" in items[1]["name"].lower()
    assert items[1]["quantity_g"] == 225.0


def test_get_pantry_parser_factory() -> None:
    """get_pantry_parser returns initialized singleton parser."""
    parser = get_pantry_parser()
    assert isinstance(parser, PantryParser)
    assert len(parser.matcher.master_by_code) > 0
    resolved = parser.resolve_master_ingredient("thịt ba chỉ")
    assert resolved is not None
    assert resolved["code"] == "7018"


@pytest.mark.parametrize(
    "module_name",
    [
        "AI.smart_parser",
        "AI.extraction",
        "AI.llm",
        "AI.recommendation.engine",
        "AI.catalog.snapshot",
    ],
)
def test_ai_modules_fresh_interpreter_import_no_cycles(module_name: str) -> None:
    """Each central AI module must import cleanly on its own in a fresh Python process."""
    env = dict(os.environ)
    env.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://dummy:dummy@localhost:5432/dummy_db",
    )
    env.setdefault("REDIS_URL", "redis://localhost:6379/0")

    result = subprocess.run(
        [sys.executable, "-c", f"import {module_name}"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Fresh interpreter import failed for {module_name}:\n"
        f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )


@pytest.mark.parametrize(
    ("label", "expected_name"),
    [
        # Unaccented print must not collapse onto a homograph (dúi vs đùi) and a brand
        # suffix ("C.P") must not break the match.
        ("THIT DUI HEO C.P", "Thịt nạc đùi heo"),
        # Extra words ("nhập khẩu") must not let a one-word alias (canh) win.
        ("CANH GIUA GA NHAP KHAU", "Cánh gà"),
        ("CÁNH GÀ - 500G", "Cánh gà"),
        ("MÁ ĐÙI GÀ - 500G", "Đùi gà"),
        # Tone-only and d/đ spelling variants still resolve to the right word.
        ("Đậu hủ trắng", "Đậu phụ (đậu hũ)"),
        ("CÁ DIÊU HỒNG LÀM SẠCH 450G", "Cá điêu hồng"),
        # Preparation words and the head noun order.
        ("CÁ TRỨNG NGUYÊN CON", "Cá trứng"),
        ("Cá Bống Biển Làm Sạch", "Cá bống"),
        # "nhỏ" is not the grape ("nho").
        ("BÚN NHỎ", "Bún tươi"),
        # A recipe-style alias that lacks the species word must not beat the plain name.
        ("CÁ ĐÙ MỘT NẮNG", "Cá đù"),
    ],
)
def test_pantry_matcher_resolves_ocr_labels_to_the_right_master(
    label: str, expected_name: str
) -> None:
    """Real OCR label spellings resolve to the intended catalog ingredient."""
    resolved = get_pantry_parser().resolve_master_ingredient(label)
    assert resolved is not None
    assert resolved["name"] == expected_name
    assert 0.5 <= resolved["match_score"] <= 1.0


@pytest.mark.parametrize(
    "label",
    [
        "XƯƠNG GÀ - 500G",  # no chicken-bone master: 'xương' and 'gà' are rival partial matches
        "TÁO CHERRY HỘP 500G",  # no cherry-apple master: must not fall back to a juice
        "HÀNH LÁ NGÒ RÍ (GÓI)",  # a bundle of two ingredients
    ],
)
def test_pantry_matcher_prefers_no_match_over_a_wrong_one(label: str) -> None:
    """A label the catalog cannot name returns None instead of a confident guess."""
    assert get_pantry_parser().resolve_master_ingredient(label) is None
