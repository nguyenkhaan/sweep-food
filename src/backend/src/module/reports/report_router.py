"""Authenticated HTTP route for waste-reduction reports."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.reports.report_dependency import get_report_service
from src.module.reports.report_dto import (
    WasteReductionQueryDTO,
    WasteReductionReportDTO,
)
from src.module.reports.report_service import ReportService

report_router = APIRouter(prefix="/reports", tags=["reports"])


@report_router.get("/waste-reduction", response_model=WasteReductionReportDTO)
async def get_waste_reduction_report(
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[ReportService, Depends(get_report_service)],
    query: Annotated[WasteReductionQueryDTO, Query()],
) -> WasteReductionReportDTO:
    """Return the authenticated user's current waste-reduction report."""
    return await service.get_waste_reduction(user.user_id, query.period)
