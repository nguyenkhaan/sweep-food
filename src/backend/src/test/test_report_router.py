"""Route tests for the authenticated waste-reduction report."""

from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import cast
from uuid import UUID

import httpx
import pytest

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole
from src.module.reports.report_dependency import get_report_service
from src.module.reports.report_dto import (
    WasteReductionCoverageDTO,
    WasteReductionPeriod,
    WasteReductionReportDTO,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a121")


class FakeReportService:
    """Return a deterministic report without a database connection."""

    async def get_waste_reduction(
        self,
        _user_id: UUID,
        period: WasteReductionPeriod,
    ) -> WasteReductionReportDTO:
        """Expose the route's service boundary for contract assertions."""
        now = datetime(2026, 9, 3, 5, tzinfo=UTC)
        return WasteReductionReportDTO(
            total_saved_kg=Decimal("1.4"),
            period=period,
            weekly_series=[Decimal("1.4")],
            top_saved_ingredients=[],
            weekly_labels=[date(2026, 8, 31)],
            period_start=datetime(2026, 8, 31, 17, tzinfo=UTC),
            period_end=now,
            timezone="Asia/Ho_Chi_Minh",
            coverage=WasteReductionCoverageDTO(
                data_from=None,
                missing_evidence_count=0,
                unsupported_unit_count=0,
            ),
        )


@pytest.mark.anyio
async def test_report_route_requires_authentication(
    api_client: httpx.AsyncClient,
) -> None:
    """The reports endpoint never exposes a cross-user aggregate anonymously."""
    async def get_fake_report_service() -> FakeReportService:
        """Avoid opening a database session before authentication fails."""
        return FakeReportService()

    async def get_unused_db_session() -> AsyncGenerator[object, None]:
        """Satisfy auth dependency construction without configuring a real database."""
        yield object()

    app.dependency_overrides[get_report_service] = get_fake_report_service
    app.dependency_overrides[get_db_session] = get_unused_db_session
    try:
        response = await api_client.get("/api/reports/waste-reduction")
    finally:
        app.dependency_overrides.pop(get_report_service, None)
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 401


@pytest.mark.anyio
async def test_report_route_returns_the_new_contract_for_an_authenticated_user(
    api_client: httpx.AsyncClient,
) -> None:
    """The router passes the selected period to the scoped report service."""
    fake_service = FakeReportService()

    async def get_fake_report_service() -> FakeReportService:
        """Avoid database access in this route contract test."""
        return fake_service

    async def get_authenticated_user() -> AuthenticatedUser:
        """Provide an authenticated subject for the route."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[get_report_service] = get_fake_report_service
    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        response = await api_client.get("/api/reports/waste-reduction?period=month")
    finally:
        app.dependency_overrides.pop(get_report_service, None)
        app.dependency_overrides.pop(require_authentication, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["period"] == "month"
    assert payload["total_saved_kg"] == "1.4"
    assert payload["weekly_labels"] == ["2026-08-31"]


@pytest.mark.anyio
async def test_report_route_rejects_an_unknown_period(
    api_client: httpx.AsyncClient,
) -> None:
    """FastAPI returns the shared 422 envelope before invoking the service."""
    async def get_authenticated_user() -> AuthenticatedUser:
        """Authenticate the request so only query validation is under test."""
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    async def get_fake_report_service() -> FakeReportService:
        """Avoid database setup while FastAPI validates the query string."""
        return FakeReportService()

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_report_service] = get_fake_report_service
    try:
        response = await api_client.get("/api/reports/waste-reduction?period=day")
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_report_service, None)

    assert response.status_code == 422
    assert response.json()["path"] == "/api/reports/waste-reduction"


def test_report_openapi_documents_bearer_auth_and_period_query() -> None:
    """The public schema exposes only the approved read-only report endpoint."""
    app.openapi_schema = None
    paths = cast(dict[str, object], app.openapi()["paths"])
    operation = cast(
        dict[str, object],
        cast(dict[str, object], paths["/api/reports/waste-reduction"])["get"],
    )
    parameters = cast(list[dict[str, object]], operation["parameters"])

    assert operation["security"] == [{"BearerAuth": []}]
    assert [parameter["name"] for parameter in parameters] == ["period"]
