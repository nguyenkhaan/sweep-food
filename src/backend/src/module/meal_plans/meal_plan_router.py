"""Authenticated meal-plan routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.module.meal_plans.meal_plan_dependency import get_meal_plan_service
from src.module.meal_plans.meal_plan_dto import (
    CreateMealPlanItemRequestDTO,
    CreateMealPlanRequestDTO,
    MealPlanDTO,
    MealPlanItemDTO,
    UpdateMealPlanItemRequestDTO,
)
from src.module.meal_plans.meal_plan_service import MealPlanService

meal_plan_router = APIRouter(prefix="/meal-plans", tags=["meal-plans"])


@meal_plan_router.post("", response_model=MealPlanDTO, status_code=status.HTTP_201_CREATED)
async def post_meal_plan(
    body: CreateMealPlanRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[MealPlanService, Depends(get_meal_plan_service)],
) -> MealPlanDTO:
    """Create one owned, bounded meal plan."""
    return await service.create(user.user_id, body)


@meal_plan_router.get("/{meal_plan_id}", response_model=MealPlanDTO)
async def get_meal_plan(
    meal_plan_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[MealPlanService, Depends(get_meal_plan_service)],
) -> MealPlanDTO:
    """Read an owned plan and its selected recipe slots."""
    return await service.get(user.user_id, meal_plan_id)


@meal_plan_router.post(
    "/{meal_plan_id}/items",
    response_model=MealPlanItemDTO,
    status_code=status.HTTP_201_CREATED,
)
async def post_meal_plan_item(
    meal_plan_id: UUID,
    body: CreateMealPlanItemRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[MealPlanService, Depends(get_meal_plan_service)],
) -> MealPlanItemDTO:
    """Select one recipe for a date and meal slot."""
    return await service.add_item(user.user_id, meal_plan_id, body)


@meal_plan_router.patch(
    "/{meal_plan_id}/items/{item_id}", response_model=MealPlanItemDTO
)
async def patch_meal_plan_item(
    meal_plan_id: UUID,
    item_id: UUID,
    body: UpdateMealPlanItemRequestDTO,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[MealPlanService, Depends(get_meal_plan_service)],
) -> MealPlanItemDTO:
    """Replace or reschedule one selected recipe."""
    return await service.update_item(user.user_id, meal_plan_id, item_id, body)


@meal_plan_router.delete(
    "/{meal_plan_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_meal_plan_item(
    meal_plan_id: UUID,
    item_id: UUID,
    user: Annotated[AuthenticatedUser, Depends(require_authentication)],
    service: Annotated[MealPlanService, Depends(get_meal_plan_service)],
) -> Response:
    """Remove one selected recipe from an owned plan."""
    await service.remove_item(user.user_id, meal_plan_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
