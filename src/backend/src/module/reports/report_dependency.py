"""FastAPI dependency construction for reports."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.reports.report_service import ReportService


async def get_report_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReportService:
    """Build the request-scoped report reader."""
    return ReportService(db_session)
