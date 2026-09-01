"""Dependencies for read-only recipe routes."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.recipes.recipe_service import RecipeService


@dataclass(frozen=True)
class RecipeListQuery:
    """Validated query parameters for a recipe browse request."""

    query: str | None
    tag: str | None
    max_cooking_minutes: int | None
    page: int
    per_page: int


async def get_recipe_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RecipeService:
    """Build the request-scoped seeded recipe query service."""
    return RecipeService(db_session)


async def get_recipe_list_query(
    q: Annotated[str | None, Query(max_length=100)] = None,
    tag: Annotated[str | None, Query(max_length=100)] = None,
    max_cooking_minutes: Annotated[int | None, Query(ge=1)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> RecipeListQuery:
    """Collect and validate public recipe list query parameters."""
    return RecipeListQuery(
        query=q,
        tag=tag,
        max_cooking_minutes=max_cooking_minutes,
        page=page,
        per_page=per_page,
    )
