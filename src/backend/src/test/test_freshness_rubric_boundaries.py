"""Regression tests verifying distinct sensory rubrics and boundary safety."""

from collections.abc import Sequence
from datetime import UTC, datetime
import json
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import StorageMode
from src.module.freshness.freshness_dto import FreshnessPreviewRequestDTO
from src.module.freshness.freshness_service import (
    FreshCheckAssessmentInputError,
    FreshnessQuestionService,
)
from src.service.freshcheck_mapping_service import parse_mapping_manifest

NOW = datetime(2026, 10, 22, 10, 0, 0, tzinfo=UTC)

# Canonical stable UUIDs derived from master catalog imports
PORK_BELLY_MASTER_ID = UUID("1c1c1c32-dc38-5561-a27c-3a61419aa2b2")  # Thịt ba chỉ (ba rọi) heo
BEEF_BELLY_MASTER_ID = UUID("23da8c8e-174e-506e-ba0d-107704420b71")  # Thịt ba chỉ bò
CURED_PORK_BELLY_MASTER_ID = UUID("39f6f3e0-7129-527b-b2de-4833580406e7")  # Thịt ba chỉ muối
WHOLE_FISH_MASTER_ID = UUID("35ad548d-88f6-568b-95f8-5966bc44180e")  # Cá quả
FISH_FILLET_MASTER_ID = UUID("e2f76e1c-7f34-5880-ba5f-dfd1badf8e2c")  # Phi lê cá lóc
SHRIMP_MASTER_ID = UUID("15d45736-3dfa-54b8-9429-2e2c25911758")  # Tôm biển
SQUID_MASTER_ID = UUID("1192fe72-7dc6-5033-aba8-55fd5ce934a6")  # Mực
POULTRY_MASTER_ID = UUID("b382a56c-a268-589c-add1-38005dcf4041")  # Thịt gà ta
BEEF_MASTER_ID = UUID("15a2302f-1140-5a6b-81a6-f56d796e1f2a")  # Thịt bò


class _FakeScalarResult:
    def __init__(self, rows: Sequence[object]) -> None:
        self._rows = list(rows)

    def all(self) -> list[object]:
        return self._rows


class _InMemoryFreshCheckSession:
    """Session serving the active KB artifact and reviewed manifest mappings."""

    def __init__(self, kb_data: dict[str, object], mappings_by_id: dict[UUID, str]) -> None:
        self.kb_version = str(kb_data["kb_version"])
        self.kb_data = kb_data
        self.mappings_by_id = mappings_by_id
        self.added: list[object] = []
        self.executed: list[object] = []
        self.committed = False

    async def scalar(self, statement: object) -> object | None:
        stmt_str = str(statement)
        if "freshcheck_kb_versions" in stmt_str:
            return SimpleNamespace(
                kb_version=self.kb_version,
                artifact=self.kb_data,
            )
        if "master_ingredient_freshcheck_mappings" in stmt_str:
            # Extract queried master_ingredient_id from compiled statement parameters if available
            return None
        return None

    async def scalars(self, statement: object) -> _FakeScalarResult:
        stmt_str = str(statement)
        if "freshcheck_archetypes" in stmt_str:
            rows = [
                SimpleNamespace(
                    archetype_id=arch_id,
                    sensory_tiers=arch["sensory_tiers"],
                    inspection_rubric=arch["inspection_rubric"],
                    preservation_protocols=arch.get("preservation_protocols", {}),
                )
                for arch_id, arch in self.kb_data.get("archetypes", {}).items()
            ]
            return _FakeScalarResult(rows)
        if "freshcheck_ingredients" in stmt_str:
            rows = [
                SimpleNamespace(
                    freshcheck_ingredient_id=ing_id,
                    archetype_id=ing["archetype"],
                    base_shelf_life_hours=ing["base_shelf_life_hours"],
                )
                for ing_id, ing in self.kb_data.get("ingredients", {}).items()
            ]
            return _FakeScalarResult(rows)
        return _FakeScalarResult([])


@pytest.fixture(scope="module")
def built_kb_data() -> dict[str, object]:
    kb_path = Path(__file__).resolve().parents[4] / "data_freshness" / "build" / "freshcheck_kb.json"
    assert kb_path.is_file(), f"Built artifact not found at {kb_path}"
    return json.loads(kb_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reviewed_manifest() -> dict[UUID, str]:
    manifest_path = (
        Path(__file__).resolve().parents[4]
        / "data_freshness"
        / "mappings"
        / "master_ingredient_freshcheck_mappings.yaml"
    )
    import yaml

    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest = parse_mapping_manifest(payload)
    return {m.master_ingredient_id: m.freshcheck_ingredient_id for m in manifest.mappings}


def _make_service(
    kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
    target_master_id: UUID | None = None,
) -> FreshnessQuestionService:
    session = _InMemoryFreshCheckSession(kb_data, reviewed_manifest)

    # Wrap scalar to look up reviewed mapping accurately
    async def scalar_lookup(statement: object) -> object | None:
        stmt_str = str(statement)
        if "freshcheck_kb_versions" in stmt_str:
            return SimpleNamespace(
                kb_version=session.kb_version,
                artifact=session.kb_data,
            )
        if "master_ingredient_freshcheck_mappings" in stmt_str:
            if target_master_id and target_master_id in reviewed_manifest:
                fc_id = reviewed_manifest[target_master_id]
                return SimpleNamespace(
                    master_ingredient_id=target_master_id,
                    kb_version=session.kb_version,
                    freshcheck_ingredient_id=fc_id,
                )
            return None
        return None

    session.scalar = scalar_lookup  # type: ignore[method-assign]
    return FreshnessQuestionService(cast(AsyncSession, session))


@pytest.mark.anyio
async def test_distinct_rubrics_poultry_vs_beef_vs_pork(
    built_kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
) -> None:
    """Chicken, beef, and pork rubrics are distinct and food-specific."""
    pork_service = _make_service(built_kb_data, reviewed_manifest, PORK_BELLY_MASTER_ID)
    pork_q = await pork_service.questions(PORK_BELLY_MASTER_ID)
    assert pork_q.archetype_id == "PORK"
    assert pork_q.freshcheck_ingredient_id == "thit_ba_chi_heo"
    pork_axes = {q.axis: [opt.value for opt in q.options] for q in pork_q.questions}
    assert "color" in pork_axes
    assert "hong_tuoi" in pork_axes["color"]
    assert "hoi_ngay" in pork_axes["elasticity"]

    beef_service = _make_service(built_kb_data, reviewed_manifest, BEEF_MASTER_ID)
    beef_q = await beef_service.questions(BEEF_MASTER_ID)
    assert beef_q.archetype_id == "BEEF"
    assert beef_q.freshcheck_ingredient_id == "thit_bo_than"
    beef_axes = {q.axis: [opt.value for opt in q.options] for q in beef_q.questions}
    assert "do_tuoi_tham" in beef_axes["color"]
    assert "hoi_am" in beef_axes["stickiness"]

    poultry_service = _make_service(built_kb_data, reviewed_manifest, POULTRY_MASTER_ID)
    poultry_q = await poultry_service.questions(POULTRY_MASTER_ID)
    assert poultry_q.archetype_id == "POULTRY"
    assert poultry_q.freshcheck_ingredient_id == "thit_ga_ta"
    poultry_axes = {q.axis: [opt.value for opt in q.options] for q in poultry_q.questions}
    assert "hong_sang" in poultry_axes["color"]
    assert "xin_xam_bam" in poultry_axes["color"]


@pytest.mark.anyio
async def test_whole_fish_vs_fillet_applicability(
    built_kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
) -> None:
    """Whole fish rubrics inspect gills and eyes; fillet rubrics never inspect missing anatomy."""
    fish_service = _make_service(built_kb_data, reviewed_manifest, WHOLE_FISH_MASTER_ID)
    fish_q = await fish_service.questions(WHOLE_FISH_MASTER_ID)
    assert fish_q.archetype_id == "WHOLE_FISH"
    fish_axes = [q.axis for q in fish_q.questions]
    assert "gills" in fish_axes
    assert "eyes" in fish_axes

    fillet_service = _make_service(built_kb_data, reviewed_manifest, FISH_FILLET_MASTER_ID)
    fillet_q = await fillet_service.questions(FISH_FILLET_MASTER_ID)
    assert fillet_q.archetype_id == "FISH_FILLET"
    fillet_axes = [q.axis for q in fillet_q.questions]
    # Fillet must NOT ask gills or eyes
    assert "gills" not in fillet_axes
    assert "eyes" not in fillet_axes


@pytest.mark.anyio
async def test_shrimp_and_squid_have_distinct_non_fish_rubrics(
    built_kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
) -> None:
    """Shrimp and squid rubrics do not ask fish gills or fish eyes."""
    shrimp_service = _make_service(built_kb_data, reviewed_manifest, SHRIMP_MASTER_ID)
    shrimp_q = await shrimp_service.questions(SHRIMP_MASTER_ID)
    assert shrimp_q.archetype_id == "SHRIMP"
    shrimp_axes = [q.axis for q in shrimp_q.questions]
    assert "gills" not in shrimp_axes
    assert "eyes" not in shrimp_axes

    squid_service = _make_service(built_kb_data, reviewed_manifest, SQUID_MASTER_ID)
    squid_q = await squid_service.questions(SQUID_MASTER_ID)
    assert squid_q.archetype_id == "SQUID"
    squid_axes = [q.axis for q in squid_q.questions]
    assert "gills" not in squid_axes
    assert "eyes" not in squid_axes


@pytest.mark.anyio
async def test_raw_pork_belly_distinguished_from_beef_and_cured(
    built_kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
) -> None:
    """Canonical pork belly resolves to thit_ba_chi_heo; beef belly and cured products do not cross."""
    # 1. Canonical raw pork belly
    pork_service = _make_service(built_kb_data, reviewed_manifest, PORK_BELLY_MASTER_ID)
    pork_q = await pork_service.questions(PORK_BELLY_MASTER_ID)
    assert pork_q.freshcheck_ingredient_id == "thit_ba_chi_heo"
    assert pork_q.archetype_id == "PORK"

    # 2. Beef belly (ba chỉ bò) does not map to pork belly
    assert reviewed_manifest.get(BEEF_BELLY_MASTER_ID) != "thit_ba_chi_heo"

    # 3. Cured pork belly (thịt ba chỉ muối) is not mapped to raw pork belly
    assert reviewed_manifest.get(CURED_PORK_BELLY_MASTER_ID) is None


@pytest.mark.anyio
async def test_pork_belly_preview_fresh_and_hard_stop(
    built_kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
) -> None:
    """Fresh sensory answers estimate positive shelf-life; spoiled options trigger hard stops."""
    service = _make_service(built_kb_data, reviewed_manifest, PORK_BELLY_MASTER_ID)

    # 1. Fresh pork preview
    fresh_req = FreshnessPreviewRequestDTO(
        master_ingredient_id=PORK_BELLY_MASTER_ID,
        storage_mode=StorageMode.REFRIGERATED,
        purchased_at=NOW,
        answers={
            "color": "hong_tuoi",
            "stickiness": "kho_rao",
            "elasticity": "hoi_ngay",
            "smell": "thom_tuoi",
        },
    )
    fresh_res = await service.preview(fresh_req, now=NOW)
    assert fresh_res.blocked is False
    assert fresh_res.expires_at is not None
    assert fresh_res.expires_at > NOW
    assert fresh_res.remaining_hours_min is not None and fresh_res.remaining_hours_min > 0

    # 2. Spoiled hard-stop pork preview
    spoiled_req = FreshnessPreviewRequestDTO(
        master_ingredient_id=PORK_BELLY_MASTER_ID,
        storage_mode=StorageMode.REFRIGERATED,
        purchased_at=NOW,
        answers={
            "color": "xam_xanh",
            "stickiness": "kho_rao",
            "elasticity": "hoi_ngay",
            "smell": "thom_tuoi",
        },
    )
    spoiled_res = await service.preview(spoiled_req, now=NOW)
    assert spoiled_res.blocked is True
    assert spoiled_res.expires_at == NOW


@pytest.mark.anyio
async def test_invalid_cross_rubric_answers_rejected(
    built_kb_data: dict[str, object],
    reviewed_manifest: dict[UUID, str],
) -> None:
    """Submitting sensory options from a different archetype is rejected with 422."""
    service = _make_service(built_kb_data, reviewed_manifest, PORK_BELLY_MASTER_ID)

    # Submitting fish gills value to pork belly
    invalid_req = FreshnessPreviewRequestDTO(
        master_ingredient_id=PORK_BELLY_MASTER_ID,
        storage_mode=StorageMode.REFRIGERATED,
        purchased_at=NOW,
        answers={
            "gills": "do_tuoi",
            "color": "hong_tuoi",
        },
    )
    with pytest.raises(FreshCheckAssessmentInputError):
        await service.preview(invalid_req, now=NOW)
