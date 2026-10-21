"""Pure FreshCheck inference over a versioned knowledge-base snapshot."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from math import floor

from src.model.enum_model import StorageMode

RULE_VERSION = "freshcheck-infer-v1.1"
_LOWER_BOUND_FACTOR = 0.6
_TIER_MAX_HOURS = {
    "tier_2_acceptable": 48.0,
    "tier_3_warning": 24.0,
}
_STORAGE_KEYS = {
    StorageMode.ROOM_TEMPERATURE: "room_temp_25_30c",
    StorageMode.REFRIGERATED: "fridge_2_4c",
    StorageMode.FROZEN: "freezer_-18c",
    StorageMode.DRY_SHELF: "room_temp_25_30c",
}
_TIER_ORDER = (
    "tier_1_fresh",
    "tier_2_acceptable",
    "tier_3_warning",
    "tier_4_spoiled",
)

JsonRecord = Mapping[str, object]


@dataclass(frozen=True)
class FreshCheckArchetype:
    """The sensory rules needed to assess ingredients of one archetype."""

    archetype_id: str
    sensory_tiers: Mapping[str, JsonRecord]
    inspection_rubric: tuple[JsonRecord, ...]
    preservation_protocols: JsonRecord


@dataclass(frozen=True)
class FreshCheckIngredient:
    """The shelf-life reference for one FreshCheck ingredient."""

    freshcheck_ingredient_id: str
    archetype_id: str
    base_shelf_life_hours: JsonRecord


@dataclass(frozen=True)
class FreshCheckKnowledgeBase:
    """An immutable, already-validated knowledge-base release."""

    kb_version: str
    archetypes: Mapping[str, FreshCheckArchetype]
    ingredients: Mapping[str, FreshCheckIngredient]


@dataclass(frozen=True)
class FreshCheckAxisScore:
    """A validated free-text axis score; only server-side inference supplies it."""

    score: float
    hard_stop: bool
    reason_vi: str


@dataclass(frozen=True)
class FreshCheckAssessmentRequest:
    """All inputs required for one deterministic FreshCheck assessment."""

    freshcheck_ingredient_id: str
    storage_mode: StorageMode | None
    purchased_at: datetime | None
    answers: Mapping[str, str]
    now: datetime
    manufacturer_expires_at: datetime | None = None
    other_scores: Mapping[str, FreshCheckAxisScore] = field(default_factory=dict)


@dataclass(frozen=True)
class FreshCheckAssessmentResult:
    """A safe assessment result with the KB and rule versions used."""

    kb_version: str
    rule_version: str
    freshcheck_ingredient_id: str | None
    archetype_id: str | None
    storage_key: str | None
    blocked: bool
    tier: str | None
    score: float | None
    remaining_hours_min: float | None
    remaining_hours_max: float | None
    remaining_days_min: int | None
    remaining_days_max: int | None
    manufacturer_expires_at: datetime | None
    reason_code: str | None
    reasons_vi: tuple[str, ...]
    storage_tips_vi: tuple[str, ...]
    claims: tuple[str, ...]


@dataclass(frozen=True)
class _HourWindow:
    """One already-capped lower and upper bound for a safe estimate."""

    minimum: float
    maximum: float


class FreshCheckEngine:
    """Apply FreshCheck rules without file or database access."""

    def assess(
        self,
        knowledge_base: FreshCheckKnowledgeBase,
        request: FreshCheckAssessmentRequest,
    ) -> FreshCheckAssessmentResult:
        """Return a conservative expiry window for one validated KB snapshot."""
        if not _has_timezone(request.now) or not _has_timezone(request.manufacturer_expires_at):
            return _blocked_result(knowledge_base, request, "timezone")
        ingredient = knowledge_base.ingredients.get(request.freshcheck_ingredient_id)
        if ingredient is None:
            return _blocked_result(knowledge_base, request, "ingredient")
        archetype = knowledge_base.archetypes.get(ingredient.archetype_id)
        if archetype is None:
            return _blocked_result(knowledge_base, request, "ingredient")
        hard_stop = _sensory_hard_stop(knowledge_base, request, archetype)
        if hard_stop is not None:
            return hard_stop
        if request.manufacturer_expires_at is not None:
            return _manufacturer_result(knowledge_base, request)
        if not _has_timezone(request.purchased_at):
            return _blocked_result(knowledge_base, request, "timezone")
        if request.purchased_at is None:
            return _blocked_result(knowledge_base, request, "timing")
        storage_key = _STORAGE_KEYS.get(request.storage_mode)
        if storage_key is None:
            return _blocked_result(knowledge_base, request, "storage", archetype.archetype_id)

        shelf_life = ingredient.base_shelf_life_hours.get(storage_key)
        shelf_life_hours, shelf_life_claim = _shelf_life_value(shelf_life)
        if shelf_life_hours is None:
            return _blocked_result(
                knowledge_base,
                request,
                "storage",
                archetype.archetype_id,
                storage_key,
            )
        return self._assess_sensory_state(
            knowledge_base,
            request,
            archetype,
            storage_key,
            shelf_life_hours,
            shelf_life_claim,
        )

    def _assess_sensory_state(
        self,
        knowledge_base: FreshCheckKnowledgeBase,
        request: FreshCheckAssessmentRequest,
        archetype: FreshCheckArchetype,
        storage_key: str,
        shelf_life_hours: float,
        shelf_life_claim: str | None,
    ) -> FreshCheckAssessmentResult:
        score = 10.0
        reasons: list[str] = []
        claims = [shelf_life_claim] if shelf_life_claim is not None else []
        for axis in archetype.inspection_rubric:
            axis_name = _string_value(axis.get("axis"))
            inferred = request.other_scores.get(axis_name) if axis_name else None
            if inferred is not None:
                score *= inferred.score / 10.0
                if inferred.score < 10.0:
                    reasons.append(inferred.reason_vi)
                continue
            option = _selected_option(axis, request.answers)
            if option is None:
                continue
            claim = _string_value(option.get("claim"))
            if claim is not None:
                claims.append(claim)
            penalty = _number_value(option.get("penalty")) or 0.0
            score *= 1.0 - penalty
            if penalty > 0:
                reasons.append(_option_reason(option))

        tier = _tier_for_score(archetype, score)
        if tier == "tier_4_spoiled":
            return _blocked_result(
                knowledge_base,
                request,
                "tier_4",
                archetype.archetype_id,
                storage_key,
                tier,
                score,
                tuple(reasons),
                _protocol_tips(archetype, "bad"),
                claims,
            )

        elapsed_hours = max(
            0.0,
            (request.now.astimezone(UTC) - request.purchased_at.astimezone(UTC)).total_seconds()
            / 3600,
        )
        remaining_hours = shelf_life_hours - elapsed_hours
        if remaining_hours <= 0:
            return _blocked_result(
                knowledge_base,
                request,
                "elapsed",
                archetype.archetype_id,
                storage_key,
                tier,
                score,
                tuple(reasons),
                _protocol_tips(archetype, "prep"),
                claims,
            )
        maximum_hours = remaining_hours * score / 10
        maximum_hours = min(maximum_hours, _TIER_MAX_HOURS.get(tier, maximum_hours))
        if tier == "tier_3_warning":
            reasons.append("Dấu hiệu cảnh báo: nên nấu ngay hôm nay")
        return _numeric_result(
            knowledge_base,
            request,
            archetype.archetype_id,
            storage_key,
            tier,
            score,
            _estimated_window(maximum_hours),
            tuple(reasons),
            _protocol_tips(archetype, "prep"),
            claims,
        )


def _manufacturer_result(
    knowledge_base: FreshCheckKnowledgeBase,
    request: FreshCheckAssessmentRequest,
) -> FreshCheckAssessmentResult:
    """Return the printed expiry without interpreting FreshCheck sensory answers."""
    assert request.manufacturer_expires_at is not None
    remaining_hours = max(
        0.0,
        (request.manufacturer_expires_at.astimezone(UTC) - request.now.astimezone(UTC)).total_seconds()
        / 3600,
    )
    return _numeric_result(
        knowledge_base,
        request,
        None,
        _STORAGE_KEYS.get(request.storage_mode),
        None,
        None,
        _exact_window(remaining_hours),
        ("Dùng hạn in sẵn của nhà sản xuất",),
        (),
        (),
    )


def _numeric_result(
    knowledge_base: FreshCheckKnowledgeBase,
    request: FreshCheckAssessmentRequest,
    archetype_id: str | None,
    storage_key: str | None,
    tier: str | None,
    score: float | None,
    hour_window: _HourWindow,
    reasons: tuple[str, ...],
    storage_tips: tuple[str, ...],
    claims: list[str],
) -> FreshCheckAssessmentResult:
    minimum_hours = round(hour_window.minimum, 1)
    maximum_hours = round(hour_window.maximum, 1)
    return FreshCheckAssessmentResult(
        kb_version=knowledge_base.kb_version,
        rule_version=RULE_VERSION,
        freshcheck_ingredient_id=request.freshcheck_ingredient_id,
        archetype_id=archetype_id,
        storage_key=storage_key,
        blocked=False,
        tier=tier,
        score=score,
        remaining_hours_min=minimum_hours,
        remaining_hours_max=maximum_hours,
        remaining_days_min=floor(minimum_hours / 24),
        remaining_days_max=floor(maximum_hours / 24),
        manufacturer_expires_at=request.manufacturer_expires_at,
        reason_code=None,
        reasons_vi=reasons,
        storage_tips_vi=storage_tips,
        claims=tuple(sorted(set(claims))),
    )


def _blocked_result(
    knowledge_base: FreshCheckKnowledgeBase,
    request: FreshCheckAssessmentRequest,
    reason_code: str,
    archetype_id: str | None = None,
    storage_key: str | None = None,
    tier: str | None = None,
    score: float | None = None,
    reasons: tuple[str, ...] = (),
    storage_tips: tuple[str, ...] = (),
    claims: list[str] | None = None,
) -> FreshCheckAssessmentResult:
    """Build one result that deliberately withholds an unsafe estimate."""
    return FreshCheckAssessmentResult(
        kb_version=knowledge_base.kb_version,
        rule_version=RULE_VERSION,
        freshcheck_ingredient_id=request.freshcheck_ingredient_id,
        archetype_id=archetype_id,
        storage_key=storage_key,
        blocked=True,
        tier=tier,
        score=score,
        remaining_hours_min=None,
        remaining_hours_max=None,
        remaining_days_min=None,
        remaining_days_max=None,
        manufacturer_expires_at=request.manufacturer_expires_at,
        reason_code=reason_code,
        reasons_vi=reasons,
        storage_tips_vi=storage_tips,
        claims=tuple(sorted(set(claims or []))),
    )


def _estimated_window(maximum_hours: float) -> _HourWindow:
    return _HourWindow(_LOWER_BOUND_FACTOR * maximum_hours, maximum_hours)


def _exact_window(hours: float) -> _HourWindow:
    return _HourWindow(hours, hours)


def _has_timezone(value: datetime | None) -> bool:
    return value is None or (value.tzinfo is not None and value.utcoffset() is not None)


def _shelf_life_value(value: object) -> tuple[float | None, str | None]:
    if isinstance(value, Mapping):
        return _number_value(value.get("value")), _string_value(value.get("claim"))
    return _number_value(value), None


def _selected_option(
    axis: JsonRecord,
    answers: Mapping[str, str],
) -> JsonRecord | None:
    axis_name = _string_value(axis.get("axis"))
    selected_value = answers.get(axis_name) if axis_name is not None else None
    options = axis.get("options")
    if selected_value is None or not isinstance(options, list):
        return None
    for option in options:
        if isinstance(option, Mapping) and option.get("value") == selected_value:
            return option
    return None


def _sensory_hard_stop(
    knowledge_base: FreshCheckKnowledgeBase,
    request: FreshCheckAssessmentRequest,
    archetype: FreshCheckArchetype,
) -> FreshCheckAssessmentResult | None:
    """Spoilage wins even when the batch has a printed manufacturer expiry."""
    for axis in archetype.inspection_rubric:
        axis_name = _string_value(axis.get("axis"))
        inferred = request.other_scores.get(axis_name) if axis_name else None
        option = _selected_option(axis, request.answers)
        if inferred is not None and inferred.hard_stop:
            reason, claim = inferred.reason_vi, None
        elif option is not None and _is_hard_stop(axis, option):
            reason, claim = _option_reason(option), _string_value(option.get("claim"))
        else:
            continue
        return _blocked_result(
            knowledge_base,
            request,
            "hard_stop",
            archetype.archetype_id,
            _STORAGE_KEYS.get(request.storage_mode),
            "tier_4_spoiled",
            0.0,
            (reason,),
            _protocol_tips(archetype, "bad"),
            [claim] if claim is not None else [],
        )
    return None


def _is_hard_stop(axis: JsonRecord, option: JsonRecord) -> bool:
    if option.get("hard_stop") is True:
        return True
    stop_if = axis.get("stop_if")
    return isinstance(stop_if, list) and option.get("value") in stop_if


def _option_reason(option: JsonRecord) -> str:
    return _string_value(option.get("reason_vi")) or _string_value(
        option.get("label_vi")
    ) or "Có dấu hiệu cần kiểm tra ngay"


def _tier_for_score(archetype: FreshCheckArchetype, score: float) -> str:
    for tier in _TIER_ORDER:
        tier_rules = archetype.sensory_tiers.get(tier)
        if tier_rules is None:
            continue
        score_range = tier_rules.get("score_range")
        if (
            isinstance(score_range, list)
            and len(score_range) == 2
            and (minimum := _number_value(score_range[0])) is not None
            and (maximum := _number_value(score_range[1])) is not None
            and minimum <= score <= maximum
        ):
            return tier
    return "tier_4_spoiled"


def _protocol_tips(archetype: FreshCheckArchetype, key: str) -> tuple[str, ...]:
    values = archetype.preservation_protocols.get(key)
    if not isinstance(values, list):
        return ()
    return tuple(value for value in values if isinstance(value, str))


def _string_value(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _number_value(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
