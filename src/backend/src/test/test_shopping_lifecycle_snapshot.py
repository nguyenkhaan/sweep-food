"""Regression coverage for cooking's effect on generated shopping requirements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.model.enum_model import MealPlanItemStatus
from src.module.inventory.inventory_service import InventoryService
from src.module.shopping_lists.shopping_service import ShoppingService

PLAN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5d101")


@dataclass
class _RequirementResult:
    def tuples(self) -> _RequirementResult:
        return self

    def all(self) -> list[tuple[object, object, object, object]]:
        return []


class _CapturingSession:
    def __init__(self) -> None:
        self.statement: object | None = None

    async def execute(self, statement: object) -> _RequirementResult:
        self.statement = statement
        return _RequirementResult()


@pytest.mark.anyio
async def test_new_shopping_requirements_query_only_planned_meal_plan_items() -> None:
    """Completion never refreshes a list; later generation excludes completed items."""
    database = _CapturingSession()
    service = ShoppingService(
        cast(AsyncSession, database),
        cast(InventoryService, object()),
    )

    requirements = await service._requirements_for_plan(PLAN_ID)

    assert requirements == []
    assert database.statement is not None
    compiled = cast(Select[tuple[object]], database.statement).compile()
    assert MealPlanItemStatus.PLANNED in compiled.params.values()
