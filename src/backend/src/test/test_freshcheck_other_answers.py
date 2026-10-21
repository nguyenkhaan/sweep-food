"""Behavioral coverage for bounded free-text sensory inference and API writes."""

import json
from datetime import timedelta
from types import SimpleNamespace
from typing import cast

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from AI.llm.openai_client import OpenAIClient
from src.app import app
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import StorageMode, UserRole
from src.module.freshness.freshness_dependency import get_freshness_questions_service
from src.module.freshness.freshness_dto import (
    FreshnessAssessmentRequestDTO,
    FreshnessPreviewRequestDTO,
)
from src.module.freshness.freshness_service import (
    FreshCheckAssessmentInputError,
    FreshnessAssessmentService,
    FreshnessQuestionService,
)
from src.service.freshcheck_engine import (
    FreshCheckArchetype,
    FreshCheckIngredient,
    FreshCheckKnowledgeBase,
)
from src.service.freshcheck_other_answer_service import (
    FreshCheckOtherAnswerClarificationError,
    FreshCheckOtherAnswerService,
)
from src.service.freshcheck_repository import FreshCheckKnowledgeBaseCache
from src.test.test_freshness_assessment import (
    BATCH_ID,
    MASTER_INGREDIENT_ID,
    NOW,
    USER_ID,
    FakeAssessmentSession,
    FakePreviewSession,
    _batch,
)


@pytest.fixture(name="sensory_cache")
def _sensory_cache() -> FreshCheckKnowledgeBaseCache:
    """Use two scored axes with a real gap for interpolation and a safety stop."""
    archetype = FreshCheckArchetype(
        archetype_id="FRESH_MEAT",
        sensory_tiers={
            "tier_1_fresh": {"score_range": [8.5, 10]},
            "tier_2_acceptable": {"score_range": [6, 8.5]},
            "tier_3_warning": {"score_range": [3, 6]},
            "tier_4_spoiled": {"score_range": [0, 3]},
        },
        inspection_rubric=(
            {
                "axis": "color",
                "question_vi": "Màu sắc miếng thịt?",
                "options": [
                    {"value": "red", "label_vi": "Đỏ tươi", "penalty": 0.0},
                    {"value": "pale", "label_vi": "Nhạt", "penalty": 0.4},
                    {
                        "value": "mold",
                        "label_vi": "Xanh mốc",
                        "penalty": 1.0,
                        "hard_stop": True,
                    },
                ],
            },
            {
                "axis": "smell",
                "question_vi": "Miếng thịt có mùi gì?",
                "stop_if": ["rotten"],
                "options": [
                    {"value": "fresh", "label_vi": "Thơm tươi", "penalty": 0.0},
                    {"value": "faint", "label_vi": "Nhạt mùi", "penalty": 0.4},
                    {"value": "rotten", "label_vi": "Hôi thối", "penalty": 1.0},
                ],
            },
        ),
        preservation_protocols={"prep": ["Giữ lạnh"], "bad": ["Không nếm thử"]},
    )
    cache = FreshCheckKnowledgeBaseCache()
    cache.store(
        FreshCheckKnowledgeBase(
            kb_version="0.3.0",
            archetypes={"FRESH_MEAT": archetype},
            ingredients={
                "thit_bo": FreshCheckIngredient(
                    "thit_bo", "FRESH_MEAT", {"fridge_2_4c": 72}
                )
            },
        )
    )
    return cache


def _session(*, preview: bool = False, **kwargs: object) -> FakeAssessmentSession:
    session_type = FakePreviewSession if preview else FakeAssessmentSession
    return session_type(
        batch=kwargs.get("batch"),
        existing=kwargs.get("existing"),
        mapping=SimpleNamespace(freshcheck_ingredient_id="thit_bo"),
    )


def _reply(
    *, score: object = 9.0, status: str = "relevant", hard_stop: bool = False
) -> dict[str, object]:
    return {
        "axes": {
            "color": {
                "status": status,
                "score": score,
                "hard_stop": hard_stop,
                "reason_vi": "Màu nằm giữa đỏ tươi và nhạt.",
            }
        }
    }


def _inference(
    payload: object, *, status_code: int = 200
) -> tuple[FreshCheckOtherAnswerService, httpx.AsyncClient, list[httpx.Request]]:
    calls: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            status_code,
            json={"choices": [{"message": {"content": json.dumps(payload)}}]},
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    return (
        FreshCheckOtherAnswerService(
            OpenAIClient(
                api_key="test-key",
                model="test-sensory-model",
                max_retries=0,
                http_client=http_client,
            )
        ),
        http_client,
        calls,
    )


def _preview(**overrides: object) -> FreshnessPreviewRequestDTO:
    return FreshnessPreviewRequestDTO.model_validate(
        {
            "master_ingredient_id": MASTER_INGREDIENT_ID,
            "storage_mode": StorageMode.REFRIGERATED,
            "purchased_at": NOW - timedelta(days=1),
            "other_answers": {"color": "Hồng, nhạt hơn đỏ tươi một chút"},
            **overrides,
        }
    )


@pytest.mark.anyio
async def test_inferred_axis_combines_with_selected_axis_and_persists_replay(
    sensory_cache: FreshCheckKnowledgeBaseCache,
) -> None:
    """Interpolation changes the total and expiry, while retries reuse the decision."""
    inference, http_client, calls = _inference(_reply())
    async with http_client:
        preview_session = _session(preview=True)
        preview = await FreshnessQuestionService(
            cast(AsyncSession, preview_session), sensory_cache,
            other_answer_service=inference,
        ).preview(_preview(answers={"smell": "faint"}), now=NOW)
        assert preview.other_answer_scores["color"].score == 9.0
        assert preview.score == pytest.approx(5.4)
        assert preview.expires_at == NOW + timedelta(hours=14.4)
        assert preview_session.added == []

        batch = _batch()
        session = _session(batch=batch)
        body = FreshnessAssessmentRequestDTO(
            answers={"smell": "faint"}, other_answers={"color": "Hồng hơi nhạt"}
        )
        result = await FreshnessAssessmentService(
            cast(AsyncSession, session), sensory_cache, other_answer_service=inference
        ).assess_batch(USER_ID, BATCH_ID, body, "other-answer", now=NOW)
        assert result.score == preview.score
        assert batch.expires_at == preview.expires_at
        assert batch.current_quantity == 1.0
        assessment = session.added[0]
        assert assessment.outcome["other_answers"] == body.other_answers
        assert assessment.outcome["other_answer_model"] == "test-sensory-model"

        retry_session = _session(batch=batch, existing=assessment)
        replay = await FreshnessAssessmentService(
            cast(AsyncSession, retry_session), sensory_cache,
            other_answer_service=inference,
        ).assess_batch(USER_ID, BATCH_ID, body, "other-answer", now=NOW)
        assert replay == result
        assert len(calls) == 2  # One preview, one write; no repeat inference on replay.
        assert retry_session.added == []


@pytest.mark.anyio
@pytest.mark.parametrize("status", ["irrelevant", "unclear"])
async def test_unusable_description_requests_clarification_without_mutating_batch(
    sensory_cache: FreshCheckKnowledgeBaseCache, status: str
) -> None:
    """Unusable text gets actionable axis-specific feedback, not a numeric fallback."""
    inference, http_client, _ = _inference(_reply(score=None, status=status))
    batch = _batch()
    session = _session(batch=batch)
    async with http_client:
        with pytest.raises(FreshCheckOtherAnswerClarificationError) as caught:
            await FreshnessAssessmentService(
                cast(AsyncSession, session), sensory_cache, other_answer_service=inference
            ).assess_batch(
                USER_ID, BATCH_ID,
                FreshnessAssessmentRequestDTO(other_answers={"color": "Tôi muốn nghe nhạc"}),
                "irrelevant", now=NOW,
            )
    assert caught.value.status_code == 422
    assert caught.value.axes[0]["axis"] == "color"
    assert batch.expires_at is None
    assert session.added == []
    assert session.committed is False


@pytest.mark.anyio
@pytest.mark.parametrize("manufacturer_expiry", [False, True])
async def test_predicted_spoilage_blocks_even_with_printed_expiry(
    sensory_cache: FreshCheckKnowledgeBaseCache, manufacturer_expiry: bool
) -> None:
    """A custom spoilage report cannot be outweighed by good axes or a printed date."""
    inference, http_client, _ = _inference(_reply(score=0.0, hard_stop=True))
    batch = _batch(manufacturer_expiry=manufacturer_expiry)
    printed_expiry = batch.expires_at
    session = _session(batch=batch)
    async with http_client:
        response = await FreshnessAssessmentService(
            cast(AsyncSession, session), sensory_cache, other_answer_service=inference
        ).assess_batch(
            USER_ID, BATCH_ID,
            FreshnessAssessmentRequestDTO(
                answers={"smell": "fresh"}, other_answers={"color": "Có mốc xanh"}
            ),
            "spoiled", now=NOW,
        )
    assert response.blocked is True
    assert response.score == 0.0
    assert response.reason_code == "hard_stop"
    assert batch.expires_at == (printed_expiry if manufacturer_expiry else NOW)
    assert batch.current_quantity == 1.0


@pytest.mark.anyio
async def test_selected_hard_stop_cannot_be_overridden_by_inferred_color(
    sensory_cache: FreshCheckKnowledgeBaseCache,
) -> None:
    inference, http_client, _ = _inference(_reply(score=10.0))
    session = _session(batch=_batch(manufacturer_expiry=True))
    async with http_client:
        response = await FreshnessAssessmentService(
            cast(AsyncSession, session), sensory_cache, other_answer_service=inference
        ).assess_batch(
            USER_ID, BATCH_ID,
            FreshnessAssessmentRequestDTO(
                answers={"smell": "rotten"}, other_answers={"color": "Đỏ tươi"}
            ),
            "selected-spoilage", now=NOW,
        )
    assert response.blocked is True
    assert response.score == 0.0


@pytest.mark.anyio
@pytest.mark.parametrize("payload", [
    _reply(score=11.0), _reply(score=5.0), _reply(score=float("nan")),
    _reply(score="9"), _reply(score=True), _reply(score=None),
    _reply(score=9.0, hard_stop=True), {"axes": {}},
    {"axes": {"smell": _reply()["axes"]["color"]}},
])
async def test_invalid_model_scores_never_update_expiry(
    sensory_cache: FreshCheckKnowledgeBaseCache, payload: object
) -> None:
    inference, http_client, _ = _inference(payload)
    batch = _batch()
    session = _session(batch=batch)
    async with http_client:
        with pytest.raises(HTTPException) as caught:
            await FreshnessAssessmentService(
                cast(AsyncSession, session), sensory_cache, other_answer_service=inference
            ).assess_batch(
                USER_ID, BATCH_ID,
                FreshnessAssessmentRequestDTO(other_answers={"color": "Hồng"}),
                "bad-model", now=NOW,
            )
    assert caught.value.status_code == 502
    assert caught.value.detail == "FRESHCHECK_LLM_RESPONSE_INVALID"
    assert batch.expires_at is None
    assert session.added == []


@pytest.mark.anyio
@pytest.mark.parametrize("reason", [None, "", "   "])
async def test_a_missing_reason_does_not_fail_a_valid_score(
    sensory_cache: FreshCheckKnowledgeBaseCache, reason: object
) -> None:
    """Models may leave the reason empty; the score is still valid and usable."""
    payload = _reply(score=9.0)
    payload["axes"]["color"]["reason_vi"] = reason
    inference, http_client, _ = _inference(payload)
    async with http_client:
        preview = await FreshnessQuestionService(
            cast(AsyncSession, _session(preview=True)), sensory_cache,
            other_answer_service=inference,
        ).preview(_preview(answers={"smell": "fresh"}), now=NOW)
    color = preview.other_answer_scores["color"]
    assert color.score == 9.0
    assert color.reason_vi.strip()  # a generic Vietnamese note replaces the gap
    assert preview.score == pytest.approx(9.0)

@pytest.mark.anyio
async def test_provider_unavailable_does_not_guess_a_fresh_score(
    sensory_cache: FreshCheckKnowledgeBaseCache,
) -> None:
    inference, http_client, _ = _inference({}, status_code=503)
    async with http_client:
        with pytest.raises(HTTPException) as caught:
            await FreshnessQuestionService(
                cast(AsyncSession, _session(preview=True)), sensory_cache,
                other_answer_service=inference,
            ).preview(_preview(), now=NOW)
    assert caught.value.status_code == 503
    assert caught.value.detail == "FRESHCHECK_LLM_UNAVAILABLE"


@pytest.mark.anyio
async def test_unknown_axis_is_rejected_before_llm_and_selected_answers_need_no_llm(
    sensory_cache: FreshCheckKnowledgeBaseCache,
) -> None:
    inference, http_client, calls = _inference({}, status_code=503)
    async with http_client:
        service = FreshnessQuestionService(
            cast(AsyncSession, _session(preview=True)), sensory_cache,
            other_answer_service=inference,
        )
        with pytest.raises(FreshCheckAssessmentInputError):
            await service.preview(_preview(other_answers={"unknown": "Hồng"}), now=NOW)
        service = FreshnessQuestionService(
            cast(AsyncSession, _session(preview=True)), sensory_cache,
            other_answer_service=inference,
        )
        response = await service.preview(
            _preview(answers={"color": "red"}, other_answers={}), now=NOW
        )
    assert response.score == 10.0
    assert response.other_answer_scores == {}
    assert calls == []


@pytest.mark.parametrize("body", [
    {"other_answers": {"color": "   "}},
    {"other_answers": {"color": "a" * 501}},
    {"other_answers": {"": "Hồng"}},
    {"other_answers": {"color": 9}},
    {"answers": {"color": "red"}, "other_answers": {"color": "Hồng"}},
    {"other_answers": {str(i): "Hồng" for i in range(21)}},
    {"answers": {str(i): "fresh" for i in range(20)}, "other_answers": {"color": "Hồng"}},
    {"other_answer_scores": {"color": 10}},
])
def test_unusable_request_shapes_cannot_reach_paid_inference(body: dict) -> None:
    with pytest.raises(ValidationError):
        FreshnessAssessmentRequestDTO.model_validate(body)


@pytest.mark.anyio
async def test_preview_route_exposes_actionable_other_answer_feedback(
    sensory_cache: FreshCheckKnowledgeBaseCache,
    api_client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inference, http_client, _ = _inference(_reply(score=None, status="irrelevant"))
    service = FreshnessQuestionService(
        cast(AsyncSession, _session(preview=True)), sensory_cache,
        other_answer_service=inference,
    )

    async def user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def questions_service() -> FreshnessQuestionService:
        return service

    monkeypatch.setitem(app.dependency_overrides, require_authentication, user)
    monkeypatch.setitem(
        app.dependency_overrides, get_freshness_questions_service, questions_service
    )
    async with http_client:
        response = await api_client.post(
            "/api/freshness/previews",
            json={
                "master_ingredient_id": str(MASTER_INGREDIENT_ID),
                "storage_mode": "REFRIGERATED",
                "other_answers": {"color": "Hôm nay trời đẹp"},
            },
        )
    assert response.status_code == 422
    error = response.json()
    assert isinstance(error["detail"], str)
    assert error["code"] == "FRESHCHECK_OTHER_ANSWER_NEEDS_CLARIFICATION"
    assert error["axes"][0]["reason"] == "irrelevant"
    assert error["axes"][0]["axis"] == "color"
