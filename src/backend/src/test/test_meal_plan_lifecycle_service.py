"""Focused lifecycle guards for meal-plan items used by cooking sessions."""

from dataclasses import dataclass, field
from datetime import date
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.cooking_session_model import CookingSessionModel
from src.model.enum_model import (
    CookingSessionStatus,
    MealPlanItemStatus,
    MealSlot,
)
from src.model.meal_plan_item_model import MealPlanItemModel
from src.model.meal_plan_model import MealPlanModel
from src.model.recipe_model import RecipeModel
from src.module.meal_plans.meal_plan_dto import UpdateMealPlanItemRequestDTO
from src.module.meal_plans.meal_plan_service import (
    MealPlanConflictError,
    MealPlanService,
)

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c101")
PLAN_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c102")
ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c103")
RECIPE_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c104")
SESSION_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5c105")


@dataclass
class _ScalarResult:
    value: object | None

    def scalar_one_or_none(self) -> object | None:
        return self.value


@dataclass
class _MealPlanSession:
    results: list[_ScalarResult]
    deleted: list[object] = field(default_factory=list)
    commit_count: int = 0
    rollback_count: int = 0

    async def execute(self, _statement: object) -> _ScalarResult:
        return self.results.pop(0)

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1

    async def delete(self, item: object) -> None:
        self.deleted.append(item)


def _plan() -> MealPlanModel:
    return MealPlanModel(
        id=PLAN_ID,
        user_id=USER_ID,
        name="Lifecycle plan",
        starts_on=date(2026, 9, 7),
        ends_on=date(2026, 9, 13),
    )


def _item(status: MealPlanItemStatus = MealPlanItemStatus.PLANNED) -> MealPlanItemModel:
    return MealPlanItemModel(
        id=ITEM_ID,
        meal_plan_id=PLAN_ID,
        recipe_id=RECIPE_ID,
        recommendation_run_id=None,
        planned_for=date(2026, 9, 7),
        meal_slot=MealSlot.DINNER,
        servings=2.0,
        status=status,
    )


def _recipe() -> RecipeModel:
    return RecipeModel(
        id=RECIPE_ID,
        name="Lifecycle recipe",
        description="Recipe used only by lifecycle service tests.",
        instructions={"steps": []},
        default_servings=2.0,
        estimated_cooking_minutes=15,
        tags={"values": []},
    )


def _session() -> CookingSessionModel:
    return CookingSessionModel(
        id=SESSION_ID,
        user_id=USER_ID,
        recipe_id=RECIPE_ID,
        meal_plan_item_id=ITEM_ID,
        servings=2.0,
        status=CookingSessionStatus.PLANNED,
        nutrition_snapshot={},
    )


@pytest.mark.anyio
async def test_update_rejects_an_item_referenced_by_a_cooking_session() -> None:
    """A session reference preserves its recipe and serving snapshot from plan edits."""
    database = _MealPlanSession(
        [_ScalarResult(_plan()), _ScalarResult(_item()), _ScalarResult(_session())]
    )
    service = MealPlanService(cast(AsyncSession, database))

    with pytest.raises(MealPlanConflictError) as error:
        await service.update_item(
            USER_ID,
            PLAN_ID,
            ITEM_ID,
            UpdateMealPlanItemRequestDTO(servings=3.0),
        )

    assert error.value.status_code == 409
    assert database.commit_count == 0
    assert database.rollback_count == 1


@pytest.mark.anyio
async def test_delete_rejects_a_completed_meal_plan_item() -> None:
    """Completion history remains intact even if no session lookup is needed."""
    item = _item(MealPlanItemStatus.COMPLETED)
    database = _MealPlanSession([_ScalarResult(_plan()), _ScalarResult(item)])
    service = MealPlanService(cast(AsyncSession, database))

    with pytest.raises(MealPlanConflictError) as error:
        await service.remove_item(USER_ID, PLAN_ID, ITEM_ID)

    assert error.value.status_code == 409
    assert not database.deleted
    assert database.commit_count == 0
    assert database.rollback_count == 1


@pytest.mark.anyio
async def test_update_keeps_an_unused_planned_item_editable() -> None:
    """The lifecycle guard leaves the existing planned-item CRUD path unchanged."""
    item = _item()
    database = _MealPlanSession(
        [
            _ScalarResult(_plan()),
            _ScalarResult(item),
            _ScalarResult(None),
            _ScalarResult(_recipe()),
        ]
    )
    service = MealPlanService(cast(AsyncSession, database))

    response = await service.update_item(
        USER_ID,
        PLAN_ID,
        ITEM_ID,
        UpdateMealPlanItemRequestDTO(servings=3.0),
    )

    assert response.servings == 3.0
    assert item.servings == 3.0
    assert database.commit_count == 1
    assert database.rollback_count == 0
