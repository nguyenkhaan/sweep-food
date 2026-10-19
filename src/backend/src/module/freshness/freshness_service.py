"""Read and persist mapped FreshCheck decisions from the active PostgreSQL KB."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.base import generate_uuid7
from src.model.enum_model import ExpirationSource, InventoryLedgerEventType
from src.model.freshcheck_assessment_model import FreshCheckAssessmentModel
from src.model.freshcheck_mapping_model import MasterIngredientFreshCheckMappingModel
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.inventory_ledger_entry_model import InventoryLedgerEntryModel
from src.module.freshness.freshness_dto import (
    FreshnessAssessmentRequestDTO,
    FreshnessAssessmentResponseDTO,
    FreshnessPreviewRequestDTO,
    FreshnessPreviewResponseDTO,
    FreshnessQuestionDTO,
    FreshnessQuestionOptionDTO,
    FreshnessQuestionsResponseDTO,
)
from src.module.inventory.inventory_service import InventoryBatchNotFoundError
from src.service.freshcheck_engine import (
    FreshCheckAssessmentRequest,
    FreshCheckAssessmentResult,
    FreshCheckEngine,
    FreshCheckKnowledgeBase,
)
from src.service.freshcheck_repository import (
    FreshCheckKBUnavailableError,
    FreshCheckKnowledgeBaseCache,
    FreshCheckKnowledgeBaseRepository,
)


class FreshCheckMappingUnavailableError(HTTPException):
    """The catalog ingredient has no reviewed mapping in the active KB release."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="MAPPING_UNAVAILABLE",
        )


class FreshCheckKBUnavailableHTTPError(HTTPException):
    """FreshCheck cannot serve a request until a KB release is activated."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="FRESHCHECK_KB_UNAVAILABLE",
        )


class FreshCheckAssessmentInputError(HTTPException):
    """The batch has insufficient safe inputs for a calculated estimate."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="FRESHCHECK_ASSESSMENT_INPUT_INVALID",
        )


class FreshnessQuestionService:
    """Resolve a reviewed catalog mapping into questions from the active KB snapshot."""

    def __init__(
        self,
        session: AsyncSession,
        cache: FreshCheckKnowledgeBaseCache | None = None,
        engine: FreshCheckEngine | None = None,
    ) -> None:
        self._session = session
        self._repository = FreshCheckKnowledgeBaseRepository(
            session,
            cache or FreshCheckKnowledgeBaseCache(),
        )
        self._engine = engine or FreshCheckEngine()

    async def questions(
        self, master_ingredient_id: UUID
    ) -> FreshnessQuestionsResponseDTO:
        """Return the active rubric for exactly one reviewed catalog mapping."""
        knowledge_base, freshcheck_ingredient_id = await _resolve_active_mapping(
            self._session,
            self._repository,
            master_ingredient_id,
        )
        ingredient = knowledge_base.ingredients.get(freshcheck_ingredient_id)
        if ingredient is None:
            raise FreshCheckMappingUnavailableError()
        archetype = knowledge_base.archetypes.get(ingredient.archetype_id)
        if archetype is None:
            raise FreshCheckMappingUnavailableError()

        return FreshnessQuestionsResponseDTO(
            kb_version=knowledge_base.kb_version,
            freshcheck_ingredient_id=ingredient.freshcheck_ingredient_id,
            archetype_id=archetype.archetype_id,
            questions=tuple(
                _question_from_rubric_axis(axis) for axis in archetype.inspection_rubric
            ),
        )

    async def preview(
        self,
        body: FreshnessPreviewRequestDTO,
        *,
        now: datetime | None = None,
    ) -> FreshnessPreviewResponseDTO:
        """Estimate an expiry for an unsaved ingredient without persisting anything."""
        assessed_at = now or datetime.now(UTC)
        knowledge_base, freshcheck_ingredient_id = await _resolve_active_mapping(
            self._session,
            self._repository,
            body.master_ingredient_id,
        )
        _validate_answers(knowledge_base, freshcheck_ingredient_id, body.answers)
        result = self._engine.assess(
            knowledge_base,
            FreshCheckAssessmentRequest(
                freshcheck_ingredient_id=freshcheck_ingredient_id,
                storage_mode=body.storage_mode,
                purchased_at=body.purchased_at or assessed_at,
                answers=body.answers,
                now=assessed_at,
            ),
        )
        return FreshnessPreviewResponseDTO(
            kb_version=result.kb_version,
            freshcheck_ingredient_id=freshcheck_ingredient_id,
            archetype_id=result.archetype_id,
            blocked=result.blocked,
            tier=result.tier,
            score=result.score,
            remaining_hours_min=result.remaining_hours_min,
            remaining_hours_max=result.remaining_hours_max,
            remaining_days_min=result.remaining_days_min,
            remaining_days_max=result.remaining_days_max,
            reason_code=result.reason_code,
            reasons_vi=result.reasons_vi,
            storage_tips_vi=result.storage_tips_vi,
            claims=result.claims,
            rule_version=result.rule_version,
            expires_at=_estimated_expiry(result, assessed_at),
        )


class FreshnessAssessmentService:
    """Persist one idempotent FreshCheck assessment with its batch audit."""

    def __init__(
        self,
        session: AsyncSession,
        cache: FreshCheckKnowledgeBaseCache | None = None,
        engine: FreshCheckEngine | None = None,
    ) -> None:
        self._session = session
        self._repository = FreshCheckKnowledgeBaseRepository(
            session,
            cache or FreshCheckKnowledgeBaseCache(),
        )
        self._engine = engine or FreshCheckEngine()

    async def assess_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
        body: FreshnessAssessmentRequestDTO,
        idempotency_key: str,
        *,
        now: datetime | None = None,
    ) -> FreshnessAssessmentResponseDTO:
        """Assess one owned batch and atomically record the resulting safe expiry."""
        assessed_at = now or datetime.now(UTC)
        async with self._session.begin():
            batch = await self._find_owned_batch(user_id, batch_id)
            existing = await self._find_existing_assessment(
                user_id,
                batch_id,
                idempotency_key,
            )
            if existing is not None:
                return _assessment_response(existing, batch.expires_at)

            knowledge_base, freshcheck_ingredient_id = await _resolve_active_mapping(
                self._session,
                self._repository,
                batch.master_ingredient_id,
            )
            request = self._assessment_request(
                batch,
                freshcheck_ingredient_id,
                body,
                assessed_at,
            )
            _validate_answers(knowledge_base, freshcheck_ingredient_id, body.answers)
            result = self._engine.assess(knowledge_base, request)
            applied_expires_at = _apply_safe_expiry(batch, result, assessed_at)
            assessment = FreshCheckAssessmentModel(
                id=generate_uuid7(),
                user_id=user_id,
                inventory_batch_id=batch.id,
                idempotency_key=idempotency_key,
                kb_version=result.kb_version,
                freshcheck_ingredient_id=freshcheck_ingredient_id,
                rule_version=result.rule_version,
                answers=dict(body.answers),
                outcome=_assessment_outcome(result, batch.expires_at),
                claims=list(result.claims),
                applied_expires_at=applied_expires_at,
            )
            self._session.add(assessment)
            self._add_metadata_audit(batch, user_id, idempotency_key)
            await self._session.flush()
            return _assessment_response(assessment, batch.expires_at)

    async def _find_owned_batch(
        self,
        user_id: UUID,
        batch_id: UUID,
    ) -> InventoryBatchModel:
        """Lock exactly one batch without disclosing another user's ownership."""
        result = await self._session.execute(
            select(InventoryBatchModel)
            .where(
                InventoryBatchModel.id == batch_id,
                InventoryBatchModel.user_id == user_id,
            )
            .with_for_update()
        )
        batch = result.scalar_one_or_none()
        if batch is None:
            raise InventoryBatchNotFoundError()
        return batch

    async def _find_existing_assessment(
        self,
        user_id: UUID,
        batch_id: UUID,
        idempotency_key: str,
    ) -> FreshCheckAssessmentModel | None:
        """Find a prior immutable result after the batch lock serializes retries."""
        return await self._session.scalar(
            select(FreshCheckAssessmentModel).where(
                FreshCheckAssessmentModel.user_id == user_id,
                FreshCheckAssessmentModel.inventory_batch_id == batch_id,
                FreshCheckAssessmentModel.idempotency_key == idempotency_key,
            )
        )

    def _assessment_request(
        self,
        batch: InventoryBatchModel,
        freshcheck_ingredient_id: str,
        body: FreshnessAssessmentRequestDTO,
        assessed_at: datetime,
    ) -> FreshCheckAssessmentRequest:
        """Resolve request overrides only after owner-scoped batch lookup succeeds."""
        manufacturer_expires_at = (
            batch.expires_at
            if batch.expiration_source is ExpirationSource.MANUFACTURER
            else None
        )
        storage_mode = body.storage_mode or batch.storage_mode
        purchased_at = body.purchased_at or batch.purchased_at or batch.stored_at
        if manufacturer_expires_at is None and (
            storage_mode is None or purchased_at is None
        ):
            raise FreshCheckAssessmentInputError()
        return FreshCheckAssessmentRequest(
            freshcheck_ingredient_id=freshcheck_ingredient_id,
            storage_mode=storage_mode,
            purchased_at=purchased_at,
            answers=body.answers,
            now=assessed_at,
            manufacturer_expires_at=manufacturer_expires_at,
        )

    def _add_metadata_audit(
        self,
        batch: InventoryBatchModel,
        user_id: UUID,
        idempotency_key: str,
    ) -> None:
        """Append the required zero-delta audit for an expiry metadata mutation."""
        self._session.add(
            InventoryLedgerEntryModel(
                user_id=user_id,
                inventory_batch_id=batch.id,
                event_type=InventoryLedgerEventType.METADATA_UPDATED,
                quantity_before=batch.current_quantity,
                quantity_delta=0.0,
                quantity_after=batch.current_quantity,
                unit=batch.unit,
                idempotency_key=idempotency_key,
                reason="FreshCheck assessment",
            )
        )


async def _resolve_active_mapping(
    session: AsyncSession,
    repository: FreshCheckKnowledgeBaseRepository,
    master_ingredient_id: UUID | None,
) -> tuple[FreshCheckKnowledgeBase, str]:
    """Resolve a reviewed mapping in the current active knowledge-base release."""
    if master_ingredient_id is None:
        raise FreshCheckMappingUnavailableError()
    try:
        knowledge_base = await repository.get_active()
    except FreshCheckKBUnavailableError as error:
        raise FreshCheckKBUnavailableHTTPError() from error
    mapping = await session.scalar(
        select(MasterIngredientFreshCheckMappingModel).where(
            MasterIngredientFreshCheckMappingModel.master_ingredient_id
            == master_ingredient_id,
            MasterIngredientFreshCheckMappingModel.kb_version
            == knowledge_base.kb_version,
        )
    )
    if mapping is None or (
        mapping.freshcheck_ingredient_id not in knowledge_base.ingredients
    ):
        raise FreshCheckMappingUnavailableError()
    return knowledge_base, mapping.freshcheck_ingredient_id


def _estimated_expiry(
    result: FreshCheckAssessmentResult,
    assessed_at: datetime,
) -> datetime | None:
    """Return the conservative expiry implied by a FreshCheck result, if any."""
    if result.blocked and result.tier == "tier_4_spoiled":
        return assessed_at
    if not result.blocked and result.remaining_hours_min is not None:
        return assessed_at + timedelta(hours=result.remaining_hours_min)
    return None


def _apply_safe_expiry(
    batch: InventoryBatchModel,
    result: FreshCheckAssessmentResult,
    assessed_at: datetime,
) -> datetime | None:
    """Apply only a conservative FreshCheck expiry, never a printed expiry."""
    if batch.expiration_source is ExpirationSource.MANUFACTURER:
        return None
    expires_at = _estimated_expiry(result, assessed_at)
    if expires_at is None:
        return None
    batch.expires_at = expires_at
    batch.expiration_source = ExpirationSource.ESTIMATED
    return expires_at


def _validate_answers(
    knowledge_base: FreshCheckKnowledgeBase,
    freshcheck_ingredient_id: str,
    answers: dict[str, str],
) -> None:
    """Reject submitted sensory values that are not in the reviewed active rubric."""
    ingredient = knowledge_base.ingredients.get(freshcheck_ingredient_id)
    archetype = (
        knowledge_base.archetypes.get(ingredient.archetype_id)
        if ingredient is not None
        else None
    )
    if archetype is None:
        raise FreshCheckMappingUnavailableError()
    allowed = {
        axis_name: {
            option["value"]
            for option in options
            if isinstance(option, dict) and isinstance(option.get("value"), str)
        }
        for axis in archetype.inspection_rubric
        if isinstance(axis, dict)
        and isinstance((axis_name := axis.get("axis")), str)
        and isinstance((options := axis.get("options")), list)
    }
    if any(answer not in allowed.get(axis, set()) for axis, answer in answers.items()):
        raise FreshCheckAssessmentInputError()


def _assessment_outcome(
    result: FreshCheckAssessmentResult,
    expires_at: datetime | None,
) -> dict[str, object]:
    """Serialize every decision input needed to reproduce the public response."""
    return {
        "archetype_id": result.archetype_id,
        "blocked": result.blocked,
        "tier": result.tier,
        "score": result.score,
        "remaining_hours_min": result.remaining_hours_min,
        "remaining_hours_max": result.remaining_hours_max,
        "remaining_days_min": result.remaining_days_min,
        "remaining_days_max": result.remaining_days_max,
        "reason_code": result.reason_code,
        "reasons_vi": list(result.reasons_vi),
        "storage_tips_vi": list(result.storage_tips_vi),
        "manufacturer_expires_at": _datetime_value(result.manufacturer_expires_at),
        "expires_at": _datetime_value(expires_at),
    }


def _assessment_response(
    assessment: FreshCheckAssessmentModel,
    expires_at: datetime | None,
) -> FreshnessAssessmentResponseDTO:
    """Rehydrate a current or idempotently replayed response from immutable history."""
    outcome = assessment.outcome
    return FreshnessAssessmentResponseDTO(
        assessment_id=assessment.id,
        batch_id=assessment.inventory_batch_id,
        kb_version=assessment.kb_version,
        freshcheck_ingredient_id=assessment.freshcheck_ingredient_id,
        archetype_id=_optional_text(outcome, "archetype_id"),
        blocked=_required_bool(outcome, "blocked"),
        tier=_optional_text(outcome, "tier"),
        score=_optional_float(outcome, "score"),
        remaining_hours_min=_optional_float(outcome, "remaining_hours_min"),
        remaining_hours_max=_optional_float(outcome, "remaining_hours_max"),
        remaining_days_min=_optional_int(outcome, "remaining_days_min"),
        remaining_days_max=_optional_int(outcome, "remaining_days_max"),
        reason_code=_optional_text(outcome, "reason_code"),
        reasons_vi=_text_tuple(outcome.get("reasons_vi")),
        storage_tips_vi=_text_tuple(outcome.get("storage_tips_vi")),
        claims=tuple(assessment.claims),
        rule_version=assessment.rule_version,
        expires_at=_outcome_expires_at(outcome, expires_at),
    )


def _datetime_value(value: datetime | None) -> str | None:
    """Keep JSON outcomes portable while retaining an RFC 3339 timestamp."""
    return value.isoformat() if value is not None else None


def _outcome_expires_at(
    outcome: dict[str, object],
    fallback: datetime | None,
) -> datetime | None:
    """Prefer the immutable response expiry while tolerating historic records."""
    value = outcome.get("expires_at")
    if not isinstance(value, str):
        return fallback
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return fallback


def _optional_text(values: dict[str, object], key: str) -> str | None:
    """Read an optional scalar string from a persisted result."""
    value = values.get(key)
    return value if isinstance(value, str) else None


def _required_bool(values: dict[str, object], key: str) -> bool:
    """Read the one required boolean encoded in every assessment outcome."""
    value = values.get(key)
    if not isinstance(value, bool):
        raise TypeError("FreshCheck assessment outcome is invalid")
    return value


def _optional_float(values: dict[str, object], key: str) -> float | None:
    """Read an optional numeric outcome without accepting boolean JSON values."""
    value = values.get(key)
    return (
        float(value)
        if isinstance(value, int | float) and not isinstance(value, bool)
        else None
    )


def _optional_int(values: dict[str, object], key: str) -> int | None:
    """Read an optional integer outcome without widening persisted JSON values."""
    value = values.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _text_tuple(value: object) -> tuple[str, ...]:
    """Return only valid persisted text items from a JSON list."""
    return (
        tuple(item for item in value if isinstance(item, str))
        if isinstance(value, list)
        else ()
    )


def _question_from_rubric_axis(axis: object) -> FreshnessQuestionDTO:
    """Translate one validated KB rubric record into the public API contract."""
    if not isinstance(axis, dict):
        raise FreshCheckKBUnavailableHTTPError()
    raw_options = axis.get("options")
    if not isinstance(raw_options, list) or not raw_options:
        raise FreshCheckKBUnavailableHTTPError()
    options = tuple(
        FreshnessQuestionOptionDTO.model_validate(option) for option in raw_options
    )
    return FreshnessQuestionDTO(
        axis=_required_rubric_text(axis, "axis"),
        question_vi=_required_rubric_text(axis, "question_vi"),
        options=options,
        default=options[0].value,
    )


def _required_rubric_text(axis: dict[object, object], key: str) -> str:
    """Read one non-empty text value from a release artifact record."""
    value = axis.get(key)
    if not isinstance(value, str) or not value.strip():
        raise FreshCheckKBUnavailableHTTPError()
    return value
