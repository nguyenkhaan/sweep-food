"""Dependencies for meal-plan routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.meal_plans.meal_plan_service import MealPlanService


async def get_meal_plan_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MealPlanService:
    """Build the request-scoped meal-plan service."""
    return MealPlanService(db_session)
