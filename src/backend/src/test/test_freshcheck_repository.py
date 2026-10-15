"""Unit tests for loading the active FreshCheck KB from PostgreSQL models."""

from types import SimpleNamespace
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.freshcheck_repository import (
    FreshCheckKBUnavailableError,
    FreshCheckKnowledgeBaseCache,
    FreshCheckKnowledgeBaseRepository,
)


class FakeScalarResult:
    """Expose the only scalar-result operation used by the repository."""

    def __init__(self, values: list[object]) -> None:
        self._values = values

    def all(self) -> list[object]:
        """Return the configured ORM-like rows."""
        return self._values


class FakeSession:
    """Return a sequenced active version and matching KB rows without a database."""

    def __init__(
        self,
        active_versions: list[object | None],
        rows_by_version: dict[str, tuple[list[object], list[object]]],
    ) -> None:
        self._active_versions = active_versions
        self._rows_by_version = rows_by_version
        self.scalar_calls = 0
        self.scalars_calls = 0
        self._active_version: str | None = None

    async def scalar(self, _statement: object) -> object | None:
        """Return the next active release selected by the repository."""
        self.scalar_calls += 1
        active_version = self._active_versions.pop(0)
        self._active_version = (
            active_version.kb_version if active_version is not None else None
        )
        return active_version

    async def scalars(self, _statement: object) -> FakeScalarResult:
        """Return archetypes then ingredients for the selected active release."""
        assert self._active_version is not None
        rows = self._rows_by_version[self._active_version]
        index = self.scalars_calls % 2
        self.scalars_calls += 1
        return FakeScalarResult(rows[index])


def _archetype(version: str) -> SimpleNamespace:
    """Build an ORM-like archetype record for one version."""
    return SimpleNamespace(
        kb_version=version,
        archetype_id="LEAFY_VEG",
        sensory_tiers={"tier_1_fresh": {"score_range": [0.0, 10.0]}},
        inspection_rubric=[],
        preservation_protocols={},
    )


def _ingredient(version: str) -> SimpleNamespace:
    """Build an ORM-like ingredient record for one version."""
    return SimpleNamespace(
        kb_version=version,
        freshcheck_ingredient_id=f"rau_muong_{version}",
        archetype_id="LEAFY_VEG",
        base_shelf_life_hours={"fridge_2_4c": {"value": 72.0}},
    )


@pytest.mark.anyio
async def test_repository_reloads_when_the_active_version_changes() -> None:
    """The cache is keyed by active kb_version, never by a stale global snapshot."""
    first_version = SimpleNamespace(kb_version="0.3.0")
    second_version = SimpleNamespace(kb_version="0.4.0")
    database = FakeSession(
        [first_version, first_version, second_version],
        {
            "0.3.0": ([_archetype("0.3.0")], [_ingredient("0.3.0")]),
            "0.4.0": ([_archetype("0.4.0")], [_ingredient("0.4.0")]),
        },
    )
    repository = FreshCheckKnowledgeBaseRepository(
        cast(AsyncSession, database), FreshCheckKnowledgeBaseCache()
    )

    first_snapshot = await repository.get_active()
    repeated_snapshot = await repository.get_active()
    refreshed_snapshot = await repository.get_active()

    assert first_snapshot.kb_version == "0.3.0"
    assert repeated_snapshot is first_snapshot
    assert refreshed_snapshot.kb_version == "0.4.0"
    assert set(refreshed_snapshot.ingredients) == {"rau_muong_0.4.0"}
    assert database.scalar_calls == 3
    assert database.scalars_calls == 4


@pytest.mark.anyio
async def test_repository_rejects_missing_active_kb() -> None:
    """FreshCheck has an explicit domain failure when no version is activated."""
    repository = FreshCheckKnowledgeBaseRepository(
        cast(AsyncSession, FakeSession([None], {})), FreshCheckKnowledgeBaseCache()
    )

    with pytest.raises(FreshCheckKBUnavailableError):
        await repository.get_active()
