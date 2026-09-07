"""Request and response DTOs for waste-reduction reports."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class WasteReductionPeriod(str, Enum):
    """Calendar periods supported by the waste-reduction report."""

    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class WasteReductionQueryDTO(BaseModel):
    """Select the current product-calendar report period."""

    model_config = ConfigDict(extra="forbid")

    period: WasteReductionPeriod = WasteReductionPeriod.MONTH


class TopSavedIngredientDTO(BaseModel):
    """One ingredient's eligible estimated mass in the selected period."""

    name: str
    saved_kg: Decimal


class WasteReductionCoverageDTO(BaseModel):
    """Explain the evidence available for an otherwise numeric report."""

    data_from: datetime | None
    missing_evidence_count: int = Field(ge=0)
    unsupported_unit_count: int = Field(ge=0)


class WasteReductionReportDTO(BaseModel):
    """M7 waste-reduction fields plus calendar and evidence coverage metadata."""

    total_saved_kg: Decimal
    period: WasteReductionPeriod
    weekly_series: list[Decimal]
    top_saved_ingredients: list[TopSavedIngredientDTO]
    weekly_labels: list[date]
    period_start: datetime
    period_end: datetime
    timezone: str
    coverage: WasteReductionCoverageDTO
