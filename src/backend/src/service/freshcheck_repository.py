"""PostgreSQL-backed loading and version-aware caching for FreshCheck KBs."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import FreshCheckKBVersionStatus
from src.model.freshcheck_model import (
    FreshCheckArchetypeModel,
    FreshCheckIngredientModel,
    FreshCheckKBVersionModel,
)
from src.service.freshcheck_engine import (
    FreshCheckArchetype,
    FreshCheckIngredient,
    FreshCheckKnowledgeBase,
)


class FreshCheckKBUnavailableError(RuntimeError):
    """Raised when FreshCheck is called before a KB release is activated."""


class FreshCheckKnowledgeBaseCache:
    """Keep immutable KB snapshots separate by their release version."""

    def __init__(self) -> None:
        self._snapshots: dict[str, FreshCheckKnowledgeBase] = {}

    def get(self, kb_version: str) -> FreshCheckKnowledgeBase | None:
        """Return a cached immutable snapshot for one known version."""
        return self._snapshots.get(kb_version)

    def store(self, snapshot: FreshCheckKnowledgeBase) -> FreshCheckKnowledgeBase:
        """Cache a snapshot and preserve the first equivalent immutable instance."""
        return self._snapshots.setdefault(snapshot.kb_version, snapshot)


class FreshCheckKnowledgeBaseRepository:
    """Load the currently active FreshCheck KB without filesystem dependencies."""

    def __init__(
        self,
        session: AsyncSession,
        cache: FreshCheckKnowledgeBaseCache,
    ) -> None:
        self._session = session
        self._cache = cache

    async def get_active(self) -> FreshCheckKnowledgeBase:
        """Return the current active release, refreshing cache selection by version."""
        active_version = await self._session.scalar(
            select(FreshCheckKBVersionModel).where(
                FreshCheckKBVersionModel.status == FreshCheckKBVersionStatus.ACTIVE
            )
        )
        if active_version is None:
            raise FreshCheckKBUnavailableError("No FreshCheck KB version is active.")
        cached_snapshot = self._cache.get(active_version.kb_version)
        if cached_snapshot is not None:
            return cached_snapshot
        return self._cache.store(
            await self._load_version(active_version.kb_version)
        )

    async def _load_version(self, kb_version: str) -> FreshCheckKnowledgeBase:
        archetype_rows = (
            await self._session.scalars(
                select(FreshCheckArchetypeModel).where(
                    FreshCheckArchetypeModel.kb_version == kb_version
                )
            )
        ).all()
        ingredient_rows = (
            await self._session.scalars(
                select(FreshCheckIngredientModel).where(
                    FreshCheckIngredientModel.kb_version == kb_version
                )
            )
        ).all()
        archetypes = {
            row.archetype_id: FreshCheckArchetype(
                archetype_id=row.archetype_id,
                sensory_tiers=row.sensory_tiers,
                inspection_rubric=tuple(row.inspection_rubric),
                preservation_protocols=row.preservation_protocols,
            )
            for row in archetype_rows
        }
        ingredients = {
            row.freshcheck_ingredient_id: FreshCheckIngredient(
                freshcheck_ingredient_id=row.freshcheck_ingredient_id,
                archetype_id=row.archetype_id,
                base_shelf_life_hours=row.base_shelf_life_hours,
            )
            for row in ingredient_rows
        }
        return FreshCheckKnowledgeBase(kb_version, archetypes, ingredients)
