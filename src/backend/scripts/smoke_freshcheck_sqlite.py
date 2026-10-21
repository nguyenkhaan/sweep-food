"""Throwaway isolated SQLite-backed smoke verification for real FreshCheck sessions and ASGI API.

Portability limit note:
PostgreSQL ORM types (UUID, JSONB, regex ~ CheckConstraints, ::jsonb server defaults,
and conditional unique indexes) are locally adapted for SQLite compilation via @compiles.
This script runs entirely against an in-memory SQLite database, loading the real built
KB 0.4.0 artifact and reviewed mappings. No production DB is accessed.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from uuid import NAMESPACE_URL, UUID, uuid5

# Ensure backend root is on sys.path
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import httpx
from sqlalchemy.dialects.postgresql import JSONB as pgJSONB, UUID as pgUUID
from sqlalchemy.dialects.sqlite.base import SQLiteDDLCompiler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CheckConstraint, Index
import yaml

# --- 1. SQLite compilation adaptors for PostgreSQL-only types ---

@compiles(pgUUID, "sqlite")
def _compile_pg_uuid_sqlite(_type, _compiler, **_kw):
    return "TEXT"


@compiles(pgJSONB, "sqlite")
def _compile_pg_jsonb_sqlite(_type, _compiler, **_kw):
    return "TEXT"


def _custom_default_string(self, column):
    if column.server_default is not None:
        text = str(column.server_default.arg)
        if "::jsonb" in text:
            text = text.replace("::jsonb", "")
        return text
    return None


SQLiteDDLCompiler.get_column_default_string = _custom_default_string


@compiles(CheckConstraint, "sqlite")
def _compile_check_constraint_sqlite(element, compiler, **_kw):
    text = str(element.sqltext)
    if "~" in text or "::" in text:
        return None
    name_str = f"CONSTRAINT {compiler.preparer.format_constraint(element)} " if element.name else ""
    return f"{name_str}CHECK ({text})"


@compiles(Index, "sqlite")
def _compile_index_sqlite(element, compiler, **_kw):
    if element.name == "uq_freshcheck_kb_versions_active":
        return f"CREATE UNIQUE INDEX {element.name} ON {element.table.name} (status) WHERE status = 'ACTIVE'"
    if element.name == "uq_master_ingredients_source_code":
        return f"CREATE UNIQUE INDEX {element.name} ON {element.table.name} (source_code) WHERE source_code IS NOT NULL"
    return compiler.visit_create_index(element)


# --- 2. Imports after compilation adaptors are active ---

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.base import Base
from src.model.enum_model import MeasurementUnit, UserRole
from src.model.freshcheck_assessment_model import FreshCheckAssessmentModel
from src.model.freshcheck_mapping_model import MasterIngredientFreshCheckMappingModel
from src.model.freshcheck_model import (
    FreshCheckArchetypeModel,
    FreshCheckClaimModel,
    FreshCheckIngredientModel,
    FreshCheckKBVersionModel,
    FreshCheckSourceModel,
)
from src.model.ingredient_category_model import IngredientCategoryModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.seed_freshness import (
    SeedConfiguration,
    build_mapping_plan,
    seed_freshness,
)
from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    FreshCheckIngredientReference,
    FreshCheckMappingSeedService,
    parse_mapping_manifest,
)
from src.service.freshcheck_sync_service import (
    FreshCheckSyncService,
    parse_freshcheck_artifact,
)

REPO_ROOT = BACKEND_ROOT.parents[1]
KB_ARTIFACT_PATH = REPO_ROOT / "data_freshness" / "build" / "freshcheck_kb.json"
MAPPINGS_PATH = REPO_ROOT / "data_freshness" / "mappings" / "master_ingredient_freshcheck_mappings.yaml"

# Target stable UUIDs for smoke verification
UUID_PORK_BELLY = "1c1c1c32-dc38-5561-a27c-3a61419aa2b2"  # Thịt ba chỉ (ba rọi) heo (7018)
UUID_PORK_LEAN = "65fc4d6d-56e9-57bd-a2b9-2b28530b243d"   # Thịt nạc heo (lợn) (7017)
UUID_PORK_RIBS = "4cf1e600-442c-53b4-87fc-36724d65a52f"   # Sườn heo (xương heo) (7053)
UUID_BEEF_LOIN = "d79e905a-b5d8-5baa-ad86-70a2bb949c9a"   # Thịt thăn bò (7005)
UUID_BEEF_LEAN = "305b0274-92a7-500b-939d-e8b788dc86fd"   # Thịt bò nạc (7003)
UUID_BEEF = "15a2302f-1140-5a6b-81a6-f56d796e1f2a"        # Thịt bò (generic)
UUID_POULTRY = "b382a56c-a268-589c-add1-38005dcf4041"     # Thịt gà ta (7013)
UUID_WHOLE_FISH = "35ad548d-88f6-568b-95f8-5966bc44180e"  # Cá quả (8022)
UUID_FISH_FILLET = "e2f76e1c-7f34-5880-ba5f-dfd1badf8e2c" # Phi lê cá lóc (fillet)
UUID_TILAPIA = "9efc93e3-26e9-59c8-9ac3-320920603f3e"     # Cá rô phi (8024)
UUID_SHRIMP = "15d45736-3dfa-54b8-9429-2e2c25911758"      # Tôm biển (8051)
UUID_SQUID = "1192fe72-7dc6-5033-aba8-55fd5ce934a6"       # Mực (8040)
UUID_OCTOPUS = "222a6768-2782-51db-b930-54d10bd199af"     # Bạch tuộc tươi (20053)

# Non-raw boundaries
UUID_BEEF_BELLY = "23da8c8e-174e-506e-ba0d-107704420b71"   # Thịt ba chỉ bò (20117)
UUID_CURED_PORK = "39f6f3e0-7129-527b-b2de-4833580406e7"   # Thịt ba chỉ muối (20804)

TABLES = [
    FreshCheckSourceModel.__table__,
    FreshCheckClaimModel.__table__,
    FreshCheckKBVersionModel.__table__,
    FreshCheckArchetypeModel.__table__,
    FreshCheckIngredientModel.__table__,
    IngredientCategoryModel.__table__,
    MasterIngredientModel.__table__,
    MasterIngredientFreshCheckMappingModel.__table__,
    FreshCheckAssessmentModel.__table__,
]


def _ai_code_master_id(code: str) -> UUID:
    """Compute AI catalog importer UUID matching AI.catalog.importer."""
    return uuid5(NAMESPACE_URL, f"sweep-food:master-ingredient:{code.strip()}")


def _create_legacy_masters(cat_meat_id: UUID, cat_fish_id: UUID) -> list[MasterIngredientModel]:
    return [
        MasterIngredientModel(id=UUID(UUID_PORK_BELLY), name="Thịt ba chỉ (ba rọi) heo", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7018"),
        MasterIngredientModel(id=UUID(UUID_PORK_LEAN), name="Thịt nạc heo (lợn)", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7017"),
        MasterIngredientModel(id=UUID(UUID_PORK_RIBS), name="Sườn heo (xương heo)", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7053"),
        MasterIngredientModel(id=UUID(UUID_BEEF_LOIN), name="Thịt thăn bò", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7005"),
        MasterIngredientModel(id=UUID(UUID_BEEF_LEAN), name="Thịt bò nạc", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7003"),
        MasterIngredientModel(id=UUID(UUID_BEEF), name="Thịt bò", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="20362"),
        MasterIngredientModel(id=UUID(UUID_POULTRY), name="Thịt gà ta", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7013"),
        MasterIngredientModel(id=UUID(UUID_WHOLE_FISH), name="Cá quả", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8022"),
        MasterIngredientModel(id=UUID("25e991df-6897-5d79-85b8-c2f31ea19fb2"), name="Cá basa, phi lê", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8063"),
        MasterIngredientModel(id=UUID(UUID_FISH_FILLET), name="Phi lê cá lóc", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code=None),
        MasterIngredientModel(id=UUID(UUID_TILAPIA), name="Cá rô phi", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8024"),
        MasterIngredientModel(id=UUID(UUID_SHRIMP), name="Tôm biển", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8051"),
        MasterIngredientModel(id=UUID(UUID_SQUID), name="Mực", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8040"),
        MasterIngredientModel(id=UUID(UUID_OCTOPUS), name="Bạch tuộc tươi", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="20053"),
        # Non-raw boundaries
        MasterIngredientModel(id=UUID(UUID_BEEF_BELLY), name="Thịt ba chỉ bò", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="20117"),
        MasterIngredientModel(id=UUID(UUID_CURED_PORK), name="Thịt ba chỉ muối", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="20804"),
    ]


def _create_code_masters(cat_meat_id: UUID, cat_fish_id: UUID) -> list[MasterIngredientModel]:
    return [
        MasterIngredientModel(id=_ai_code_master_id("7018"), name="Thịt ba chỉ (ba rọi) heo", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7018"),
        MasterIngredientModel(id=_ai_code_master_id("7017"), name="Thịt nạc heo (lợn)", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7017"),
        MasterIngredientModel(id=_ai_code_master_id("7053"), name="Sườn heo (xương heo)", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7053"),
        MasterIngredientModel(id=_ai_code_master_id("7005"), name="Thịt thăn bò", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7005"),
        MasterIngredientModel(id=_ai_code_master_id("7003"), name="Thịt bò nạc", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7003"),
        MasterIngredientModel(id=_ai_code_master_id("20362"), name="Thịt bò", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="20362"),
        MasterIngredientModel(id=_ai_code_master_id("7013"), name="Thịt gà ta", category_id=cat_meat_id, canonical_unit=MeasurementUnit.GRAM, source_code="7013"),
        MasterIngredientModel(id=_ai_code_master_id("8022"), name="Cá quả", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8022"),
        MasterIngredientModel(id=_ai_code_master_id("8063"), name="Cá basa, phi lê", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8063"),
        MasterIngredientModel(id=_ai_code_master_id("8024"), name="Cá rô phi", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8024"),
        MasterIngredientModel(id=_ai_code_master_id("8051"), name="Tôm biển", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8051"),
        MasterIngredientModel(id=_ai_code_master_id("8040"), name="Mực", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="8040"),
        MasterIngredientModel(id=_ai_code_master_id("20053"), name="Bạch tuộc tươi", category_id=cat_fish_id, canonical_unit=MeasurementUnit.GRAM, source_code="20053"),
    ]


async def run_smoke() -> int:
    print("=== FreshCheck Isolated SQLite Smoke Verification ===")

    # Load artifacts once
    assert KB_ARTIFACT_PATH.is_file(), f"KB artifact missing: {KB_ARTIFACT_PATH}"
    artifact = parse_freshcheck_artifact(json.loads(KB_ARTIFACT_PATH.read_text(encoding="utf-8")))
    assert MAPPINGS_PATH.is_file(), f"Mappings manifest missing: {MAPPINGS_PATH}"
    manifest = parse_mapping_manifest(yaml.safe_load(MAPPINGS_PATH.read_text(encoding="utf-8")))

    cat_meat_id = UUID("105d8682-3a37-5b6c-b772-cd3d63708fd5")
    cat_fish_id = UUID("bf8cf57a-4e2c-5e48-8b5c-867bf80353b1")

    # ---------------------------------------------------------
    # Scenario A: Legacy Host Identity Catalog (Target Host Proof)
    # ---------------------------------------------------------
    print("\n--- Scenario A: Legacy Host Identity Catalog ---")
    engine_a = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory_a = async_sessionmaker(engine_a, expire_on_commit=False)

    async with engine_a.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=TABLES)

    async with session_factory_a() as session, session.begin():
        sync_svc = FreshCheckSyncService(session)
        await sync_svc.stage(artifact, actor="smoke-test")

        session.add(IngredientCategoryModel(id=cat_meat_id, name="Thịt và sản phẩm chế biến"))
        session.add(IngredientCategoryModel(id=cat_fish_id, name="Thủy sản và sản phẩm thủy sản"))
        session.add_all(_create_legacy_masters(cat_meat_id, cat_fish_id))
        await session.flush()

        inserted = await FreshCheckMappingSeedService(session).seed(manifest)
        print(f"   Seeded {inserted} reviewed mappings for legacy host catalog")
        act_res = await sync_svc.activate(artifact, actor="smoke-test")
        print(f"   Activated KB {artifact.kb_version}: {act_res.action}")

    # Set up ASGI test client over Scenario A
    async def _get_session_a():
        async with session_factory_a() as s:
            yield s

    user_id = UUID("00000000-0000-0000-0000-000000000099")
    app.dependency_overrides[get_db_session] = _get_session_a
    app.dependency_overrides[require_authentication] = lambda: AuthenticatedUser(user_id, (UserRole.USER,))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Questions API distinct rubrics
        resp = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_PORK_BELLY}")
        assert resp.status_code == 200, f"Expected 200 for pork belly, got {resp.status_code}: {resp.text}"
        pork_data = resp.json()
        assert pork_data["archetype_id"] == "PORK" and pork_data["freshcheck_ingredient_id"] == "thit_ba_chi_heo"
        print(f"   [PASS] Pork Belly -> Archetype: {pork_data['archetype_id']}, ID: {pork_data['freshcheck_ingredient_id']}")

        resp = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_BEEF}")
        assert resp.status_code == 200
        beef_data = resp.json()
        assert beef_data["archetype_id"] == "BEEF" and beef_data["freshcheck_ingredient_id"] == "thit_bo_than"
        print(f"   [PASS] Beef -> Archetype: {beef_data['archetype_id']}, ID: {beef_data['freshcheck_ingredient_id']}")

        resp = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_POULTRY}")
        assert resp.status_code == 200
        poultry_data = resp.json()
        assert poultry_data["archetype_id"] == "POULTRY" and poultry_data["freshcheck_ingredient_id"] == "thit_ga_ta"
        print(f"   [PASS] Poultry -> Archetype: {poultry_data['archetype_id']}, ID: {poultry_data['freshcheck_ingredient_id']}")

        resp_fish = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_WHOLE_FISH}")
        assert resp_fish.status_code == 200
        fish_data = resp_fish.json()
        assert fish_data["archetype_id"] == "WHOLE_FISH"
        fish_axes = [q["axis"] for q in fish_data["questions"]]
        assert "gills" in fish_axes and "eyes" in fish_axes
        print(f"   [PASS] Whole Fish -> Archetype: {fish_data['archetype_id']} (has gills/eyes: {fish_axes})")

        resp_fillet = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_FISH_FILLET}")
        assert resp_fillet.status_code == 200
        fillet_data = resp_fillet.json()
        assert fillet_data["archetype_id"] == "FISH_FILLET"
        fillet_axes = [q["axis"] for q in fillet_data["questions"]]
        assert "gills" not in fillet_axes and "eyes" not in fillet_axes
        print(f"   [PASS] Fish Fillet -> Archetype: {fillet_data['archetype_id']} (NO gills/eyes: {fillet_axes})")

        resp_shrimp = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_SHRIMP}")
        assert resp_shrimp.status_code == 200
        shrimp_data = resp_shrimp.json()
        assert shrimp_data["archetype_id"] == "SHRIMP"
        shrimp_axes = [q["axis"] for q in shrimp_data["questions"]]
        assert "gills" not in shrimp_axes and "eyes" not in shrimp_axes
        print(f"   [PASS] Shrimp -> Archetype: {shrimp_data['archetype_id']} (NO gills/eyes: {shrimp_axes})")

        resp_squid = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_SQUID}")
        assert resp_squid.status_code == 200
        squid_data = resp_squid.json()
        assert squid_data["archetype_id"] == "SQUID"
        squid_axes = [q["axis"] for q in squid_data["questions"]]
        assert "gills" not in squid_axes and "eyes" not in squid_axes
        print(f"   [PASS] Squid -> Archetype: {squid_data['archetype_id']} (NO gills/eyes: {squid_axes})")

        # 2. Non-raw boundary (cured pork) -> 422
        resp_cured = await client.get(f"/api/freshness/questions?master_ingredient_id={UUID_CURED_PORK}")
        assert resp_cured.status_code == 422
        print("   [PASS] Cured pork -> 422 MAPPING_UNAVAILABLE (boundary verified)")

        # 3. Previews & every hard-stop from built rubrics
        now_iso = datetime.now(UTC).isoformat()

        # Pork fresh
        pork_fresh = {
            "master_ingredient_id": UUID_PORK_BELLY,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"color": "hong_tuoi", "stickiness": "kho_rao", "elasticity": "hoi_ngay", "smell": "thom_tuoi"},
        }
        res = await client.post("/api/freshness/previews", json=pork_fresh)
        assert res.status_code == 200 and res.json()["blocked"] is False and res.json()["remaining_hours_min"] > 0
        print(f"   [PASS] Pork fresh preview -> positive hours: {res.json()['remaining_hours_min']}h")

        # Pork hard-stop
        pork_hs = dict(pork_fresh)
        pork_hs["answers"] = {"color": "xam_xanh", "stickiness": "kho_rao", "elasticity": "hoi_ngay", "smell": "thom_tuoi"}
        res = await client.post("/api/freshness/previews", json=pork_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Pork hard stop ('xam_xanh') -> blocked: True")

        # Beef hard-stop
        beef_hs = {
            "master_ingredient_id": UUID_BEEF,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"color": "xam_xanh", "stickiness": "kho_rao", "elasticity": "hoi_ngay", "smell": "thom_tuoi"},
        }
        res = await client.post("/api/freshness/previews", json=beef_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Beef hard stop ('xam_xanh') -> blocked: True")

        # Poultry hard-stop
        poultry_hs = {
            "master_ingredient_id": UUID_POULTRY,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"color": "xam_xanh", "stickiness": "kho_rao", "elasticity": "hoi_ngay", "smell": "thom_tuoi"},
        }
        res = await client.post("/api/freshness/previews", json=poultry_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Poultry hard stop ('xam_xanh') -> blocked: True")

        # Whole fish hard-stop
        fish_hs = {
            "master_ingredient_id": UUID_WHOLE_FISH,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"gills": "xam_nau_nhot", "eyes": "trong_loi", "flesh_belly": "chac_nguyen", "smell": "nhe_tu_nhien"},
        }
        res = await client.post("/api/freshness/previews", json=fish_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Whole fish hard stop ('xam_nau_nhot') -> blocked: True")

        # Fish fillet hard-stop
        fillet_hs = {
            "master_ingredient_id": UUID_FISH_FILLET,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"appearance": "sang_bong", "texture": "nhun_nat_mun", "smell": "nhe_tu_nhien"},
        }
        res = await client.post("/api/freshness/previews", json=fillet_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Fish fillet hard stop ('nhun_nat_mun') -> blocked: True")

        # Shrimp hard-stop
        shrimp_hs = {
            "master_ingredient_id": UUID_SHRIMP,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"shell_head": "dinh_chat_bong", "flesh_color": "trong_ngoc_trai", "firmness": "san_chac_cang", "smell": "amoniac_thoi_h2s"},
        }
        res = await client.post("/api/freshness/previews", json=shrimp_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Shrimp hard stop ('amoniac_thoi_h2s') -> blocked: True")

        # Squid hard-stop
        squid_hs = {
            "master_ingredient_id": UUID_SQUID,
            "storage_mode": "REFRIGERATED",
            "purchased_at": now_iso,
            "answers": {"skin_mantle": "sang_ong_sac_to_ro", "head_tentacles": "dinh_chat_nguyen_ven", "firmness": "san_chac_day_dan", "smell": "amoniac_thoi"},
        }
        res = await client.post("/api/freshness/previews", json=squid_hs)
        assert res.status_code == 200 and res.json()["blocked"] is True
        print("   [PASS] Squid hard stop ('amoniac_thoi') -> blocked: True")

        # Invalid cross-rubric answer
        cross_bad = dict(pork_fresh)
        cross_bad["answers"] = {"gills": "do_tuoi", "color": "hong_tuoi"}
        res = await client.post("/api/freshness/previews", json=cross_bad)
        assert res.status_code == 422
        print("   [PASS] Cross-rubric invalid answer -> 422 FRESHCHECK_ASSESSMENT_INPUT_INVALID")

    await engine_a.dispose()

    # ---------------------------------------------------------
    # Scenario B: AI Code-Based Identity Catalog (Fresh Install Proof)
    # ---------------------------------------------------------
    print("\n--- Scenario B: AI Code-Based Identity Catalog ---")
    engine_b = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory_b = async_sessionmaker(engine_b, expire_on_commit=False)

    async with engine_b.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=TABLES)

    code_pork_belly_id = _ai_code_master_id("7018")
    code_lean_beef_id = _ai_code_master_id("7003")
    code_basa_fillet_id = _ai_code_master_id("8063")

    async with session_factory_b() as session, session.begin():
        sync_svc = FreshCheckSyncService(session)
        await sync_svc.stage(artifact, actor="smoke-test")

        session.add(IngredientCategoryModel(id=cat_meat_id, name="Thịt và sản phẩm chế biến"))
        session.add(IngredientCategoryModel(id=cat_fish_id, name="Thủy sản và sản phẩm thủy sản"))
        session.add_all(_create_code_masters(cat_meat_id, cat_fish_id))
        await session.flush()

        inserted = await FreshCheckMappingSeedService(session).seed(manifest)
        print(f"   Seeded {inserted} mappings resolving catalog_code on fresh-install catalog")
        await sync_svc.activate(artifact, actor="smoke-test")

    async def _get_session_b():
        async with session_factory_b() as s:
            yield s

    app.dependency_overrides[get_db_session] = _get_session_b
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Pork belly resolved under AI code-based UUID
        resp = await client.get(f"/api/freshness/questions?master_ingredient_id={code_pork_belly_id}")
        assert resp.status_code == 200
        assert resp.json()["archetype_id"] == "PORK" and resp.json()["freshcheck_ingredient_id"] == "thit_ba_chi_heo"
        print(f"   [PASS] Fresh-install AI Code ID ({code_pork_belly_id}) resolved to PORK rubric")

        # Lean beef resolved under AI code-based UUID
        resp_beef = await client.get(f"/api/freshness/questions?master_ingredient_id={code_lean_beef_id}")
        assert resp_beef.status_code == 200
        assert resp_beef.json()["archetype_id"] == "BEEF" and resp_beef.json()["freshcheck_ingredient_id"] == "thit_bo_than"
        print(f"   [PASS] Fresh-install Lean Beef Code ID ({code_lean_beef_id}) resolved to BEEF rubric")

        # Basa fillet resolved under AI code-based UUID
        resp_basa = await client.get(f"/api/freshness/questions?master_ingredient_id={code_basa_fillet_id}")
        assert resp_basa.status_code == 200
        assert resp_basa.json()["archetype_id"] == "FISH_FILLET" and resp_basa.json()["freshcheck_ingredient_id"] == "ca_basa_phi_le"
        print(f"   [PASS] Fresh-install Basa Fillet Code ID ({code_basa_fillet_id}) resolved to FISH_FILLET rubric")

    await engine_b.dispose()

    # ---------------------------------------------------------
    # Scenario C: Active Mapping Preservation Across Releases
    # ---------------------------------------------------------
    print("\n--- Scenario C: Active Mapping Preservation Across Releases ---")
    catalog_items = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Thịt bò"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000002"), "Cá quả"),
    )
    freshcheck_refs = (
        FreshCheckIngredientReference("thit_bo_than", ("thịt bò",)),
        FreshCheckIngredientReference("ca_loc", ("cá quả",)),
    )
    active_m = MasterIngredientFreshCheckMappingModel(
        master_ingredient_id=UUID("00000000-0000-0000-0000-000000000001"),
        kb_version="0.3.0",
        freshcheck_ingredient_id="thit_bo_than",
        match_method="MANUAL_REVIEW",
        reviewed_by="legacy_reviewer",
        note="Active mapping carried from 0.3.0",
    )
    plan = build_mapping_plan(
        "0.4.0",
        catalog_items,
        freshcheck_refs,
        reviewed_manifest=None,
        active_mappings=[active_m],
        prior_active_kb_version="0.3.0",
    )
    assert len(plan.mapping_manifest.mappings) == 2
    mappings_by_mid = {m.master_ingredient_id: m for m in plan.mapping_manifest.mappings}
    assert mappings_by_mid[UUID("00000000-0000-0000-0000-000000000001")].match_method == "MANUAL_REVIEW"
    assert mappings_by_mid[UUID("00000000-0000-0000-0000-000000000002")].match_method == "EXACT_NAME"
    print("   [PASS] Existing active manual mapping preserved and carried forward without being overridden by exact-name matching")

    app.dependency_overrides.pop(get_db_session, None)
    app.dependency_overrides.pop(require_authentication, None)
    print("\n=== All isolated SQLite FreshCheck smoke checks PASSED (100% Green) ===")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run_smoke()))
