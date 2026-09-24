"""Dependencies for ingredient-category routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.category.category_service import CategoryService


async def get_category_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CategoryService:
    """Build the request-scoped category service."""
    return CategoryService(db_session)
