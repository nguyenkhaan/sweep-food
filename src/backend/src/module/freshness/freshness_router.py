"""Authenticated FreshCheck sensory-question routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.freshness.freshness_dependency import (
    get_freshness_assessment_service,
    get_freshness_questions_service,
)
from src.module.freshness.freshness_dto import (
    FreshnessAssessmentRequestDTO,
    FreshnessAssessmentResponseDTO,
    FreshnessPreviewRequestDTO,
    FreshnessPreviewResponseDTO,
    FreshnessQuestionsResponseDTO,
)
from src.module.freshness.freshness_service import (
    FreshnessAssessmentService,
    FreshnessQuestionService,
)

freshness_router = APIRouter(prefix="/freshness", tags=["freshness"])


@freshness_router.get("/questions", response_model=FreshnessQuestionsResponseDTO)
async def get_freshness_questions(
    master_ingredient_id: UUID,
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[
        FreshnessQuestionService,
        Depends(get_freshness_questions_service),
    ],
) -> FreshnessQuestionsResponseDTO:
    """Return the active sensory rubric for one reviewed master ingredient mapping."""
    return await service.questions(master_ingredient_id)


@freshness_router.post("/previews", response_model=FreshnessPreviewResponseDTO)
async def post_freshness_preview(
    body: FreshnessPreviewRequestDTO,
    _user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[
        FreshnessQuestionService,
        Depends(get_freshness_questions_service),
    ],
) -> FreshnessPreviewResponseDTO:
    """Estimate an expiry for an unsaved ingredient; nothing is persisted."""
    return await service.preview(body)


@freshness_router.post(
    "/batches/{batch_id}/assessment",
    response_model=FreshnessAssessmentResponseDTO,
)
async def post_freshness_assessment(
    batch_id: UUID,
    body: FreshnessAssessmentRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[
        FreshnessAssessmentService,
        Depends(get_freshness_assessment_service),
    ],
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=1, max_length=255),
    ],
) -> FreshnessAssessmentResponseDTO:
    """Persist one safe FreshCheck expiry decision and its idempotent audit."""
    return await service.assess_batch(user.user_id, batch_id, body, idempotency_key)
