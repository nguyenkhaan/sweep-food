"""Unit tests for pure FreshCheck rule evaluation."""

from datetime import UTC, datetime, timedelta

import pytest

from src.model.enum_model import StorageMode
from src.service.freshcheck_engine import (
    RULE_VERSION,
    FreshCheckAssessmentRequest,
    FreshCheckArchetype,
    FreshCheckEngine,
    FreshCheckIngredient,
    FreshCheckKnowledgeBase,
)

NOW = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)


def _knowledge_base() -> FreshCheckKnowledgeBase:
    """Build one deterministic KB without reading an artifact file."""
    archetype = FreshCheckArchetype(
        archetype_id="LEAFY_VEG",
        sensory_tiers={
            "tier_1_fresh": {"score_range": [8.5, 10.0]},
            "tier_2_acceptable": {"score_range": [6.0, 8.5]},
            "tier_3_warning": {"score_range": [3.0, 6.0]},
            "tier_4_spoiled": {"score_range": [0.0, 3.0]},
        },
        inspection_rubric=(
            {
                "axis": "appearance",
                "options": [
                    {"value": "fresh", "label_vi": "Tươi", "penalty": 0.0},
                    {
                        "value": "acceptable",
                        "label_vi": "Chấp nhận được",
                        "penalty": 0.2,
                        "reason_vi": "Có dấu hiệu giảm chất lượng",
                    },
                    {
                        "value": "warning",
                        "label_vi": "Cảnh báo",
                        "penalty": 0.6,
                        "reason_vi": "Nên nấu ngay",
                    },
                    {
                        "value": "spoiled",
                        "label_vi": "Hỏng",
                        "penalty": 1.0,
                        "reason_vi": "Tình trạng rất kém",
                    },
                    {
                        "value": "mold",
                        "label_vi": "Mốc",
                        "penalty": 1.0,
                        "hard_stop": True,
                        "reason_vi": "Có nấm mốc",
                    },
                ],
            },
        ),
        preservation_protocols={"prep": ["Bảo quản lạnh"], "bad": ["Không nếm thử"]},
    )
    ingredient = FreshCheckIngredient(
        freshcheck_ingredient_id="rau_muong",
        archetype_id=archetype.archetype_id,
        base_shelf_life_hours={"fridge_2_4c": {"value": 72.0, "claim": "C-1"}},
    )
    return FreshCheckKnowledgeBase(
        kb_version="0.3.0",
        archetypes={archetype.archetype_id: archetype},
        ingredients={ingredient.freshcheck_ingredient_id: ingredient},
    )


def _request(
    *,
    freshcheck_ingredient_id: str = "rau_muong",
    storage_mode: StorageMode = StorageMode.REFRIGERATED,
    purchased_at: datetime = NOW,
    answers: dict[str, str] | None = None,
    manufacturer_expires_at: datetime | None = None,
) -> FreshCheckAssessmentRequest:
    """Build one deterministic assessment request."""
    return FreshCheckAssessmentRequest(
        freshcheck_ingredient_id=freshcheck_ingredient_id,
        storage_mode=storage_mode,
        purchased_at=purchased_at,
        answers=answers or {},
        now=NOW,
        manufacturer_expires_at=manufacturer_expires_at,
    )


@pytest.mark.parametrize(
    ("answer", "tier", "remaining_hours_max"),
    [
        ("fresh", "tier_1_fresh", 72.0),
        ("acceptable", "tier_2_acceptable", 48.0),
        ("warning", "tier_3_warning", 24.0),
        ("spoiled", "tier_4_spoiled", None),
    ],
)
def test_assessment_applies_each_sensory_tier(
    answer: str,
    tier: str,
    remaining_hours_max: float | None,
) -> None:
    """Every score tier has the expected safe time-window behavior."""
    result = FreshCheckEngine().assess(_knowledge_base(), _request(answers={"appearance": answer}))

    assert result.kb_version == "0.3.0"
    assert result.rule_version == RULE_VERSION
    assert result.tier == tier
    assert result.remaining_hours_max == remaining_hours_max
    assert result.blocked is (tier == "tier_4_spoiled")


def test_assessment_preserves_manufacturer_expiry() -> None:
    """A printed expiry is reported without applying FreshCheck penalties."""
    manufacturer_expiry = NOW + timedelta(days=2)

    result = FreshCheckEngine().assess(
        _knowledge_base(),
        _request(
            answers={"appearance": "mold"},
            manufacturer_expires_at=manufacturer_expiry,
        ),
    )

    assert result.manufacturer_expires_at == manufacturer_expiry
    assert result.remaining_hours_min == 48.0
    assert result.remaining_hours_max == 48.0
    assert result.blocked is False


def test_hard_stop_blocks_a_numeric_estimate() -> None:
    """A hard-stop answer has priority over shelf-life arithmetic."""
    result = FreshCheckEngine().assess(
        _knowledge_base(), _request(answers={"appearance": "mold"})
    )

    assert result.blocked is True
    assert result.tier == "tier_4_spoiled"
    assert result.remaining_hours_min is None
    assert result.reasons_vi == ("Có nấm mốc",)


@pytest.mark.parametrize(
    ("ingredient_id", "storage_mode", "purchased_at", "reason"),
    [
        ("missing", StorageMode.REFRIGERATED, NOW, "ingredient"),
        ("rau_muong", StorageMode.DRY_SHELF, NOW, "storage"),
        ("rau_muong", StorageMode.REFRIGERATED, NOW.replace(tzinfo=None), "timezone"),
    ],
)
def test_assessment_rejects_unavailable_or_ambiguous_inputs(
    ingredient_id: str,
    storage_mode: StorageMode,
    purchased_at: datetime,
    reason: str,
) -> None:
    """Unknown ingredient/storage and naive timestamps never produce an estimate."""
    result = FreshCheckEngine().assess(
        _knowledge_base(),
        _request(
            freshcheck_ingredient_id=ingredient_id,
            storage_mode=storage_mode,
            purchased_at=purchased_at,
        ),
    )

    assert result.blocked is True
    assert result.reason_code == reason
    assert result.remaining_hours_max is None
