"""Dependencies for catalog read routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db_session
from src.module.catalog.catalog_service import CatalogService


async def get_catalog_service(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CatalogService:
    """Build the request-scoped catalog query service."""
    return CatalogService(db_session)
