"""Dependency for ingredient management routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.ingredient.ingredient_service import IngredientService


async def get_ingredient_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IngredientService:
    """Build a request-scoped ingredient management service."""
    return IngredientService(db_session)
