"""Tests for safe catalog replacement and cascading user-data options."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Final
from uuid import UUID

import pytest

from AI.catalog.importer import (
    DEFAULT_BUNDLE_DIR,
    load_catalog_bundle,
    transform_catalog_bundle,
)
from AI.catalog.replace import (
    ACCOUNT_TABLES,
    CATALOG_TABLES,
    REFERENCE_DATA_TABLES,
    ReplaceCatalogPlan,
    ReplaceOptions,
    json_serializer,
    run_replace_catalog,
    write_backup,
)

try:
    import pgserver

    PGSERVER_AVAILABLE: Final[bool] = True
except ImportError:
    PGSERVER_AVAILABLE = False


# =========================================================================
# Pure Unit Tests (Always run, no PostgreSQL required)
# =========================================================================


def test_constants_and_tables_classification() -> None:
    """Core table classification sets are properly partitioned and non-empty."""
    assert "ingredient_aliases" in REFERENCE_DATA_TABLES
    assert "shelf_life_rules" in REFERENCE_DATA_TABLES
    assert "master_ingredient_freshcheck_mappings" in REFERENCE_DATA_TABLES

    assert "users" in ACCOUNT_TABLES
    assert "auth_sessions" in ACCOUNT_TABLES
    assert "device_registrations" in ACCOUNT_TABLES

    assert "recipes" in CATALOG_TABLES
    assert "recipe_ingredients" in CATALOG_TABLES
    assert "master_ingredients" in CATALOG_TABLES

    # Disjointness checks
    assert not (REFERENCE_DATA_TABLES & ACCOUNT_TABLES)


def test_json_serializer_handles_types() -> None:
    """json_serializer converts UUID, Decimal, and datetime to serializable strings."""
    u = UUID("11111111-1111-1111-1111-111111111111")
    d = Decimal("12.345")
    dt = datetime(2026, 10, 19, 12, 0, 0, tzinfo=UTC)

    assert json_serializer(u) == "11111111-1111-1111-1111-111111111111"
    assert json_serializer(d) == "12.345"
    assert json_serializer(dt) == "2026-10-19T12:00:00+00:00"

    with pytest.raises(TypeError):
        json_serializer(object())


def test_write_backup_creates_expected_structure(tmp_path: Path) -> None:
    """write_backup creates plan.json, README.txt, and table jsonl files."""
    plan = ReplaceCatalogPlan()
    plan.preflight_counts = {"recipes": 100}
    plan.retained_legacy_recipes = {UUID("11111111-1111-1111-1111-111111111111"): "cooking_sessions"}

    db_rows = {
        "recipes": [{"id": UUID("11111111-1111-1111-1111-111111111111"), "name": "Legacy Recipe"}],
    }

    backup_dir = write_backup(plan, db_rows, tmp_path / "backup_test")
    assert (backup_dir / "plan.json").is_file()
    assert (backup_dir / "README.txt").is_file()
    assert (backup_dir / "recipes.jsonl").is_file()

    with (backup_dir / "recipes.jsonl").open(encoding="utf-8") as fh:
        line = fh.readline()
        data = json.loads(line)
        assert data["id"] == "11111111-1111-1111-1111-111111111111"
        assert data["name"] == "Legacy Recipe"


def test_topological_deletion_sorter() -> None:
    """Child-first deletion ordering places dependent tables before parent tables."""
    from graphlib import TopologicalSorter

    # cooking_consumptions references cooking_sessions, which references recipes
    # When deleting: consumptions first, then sessions, then recipes
    user_graph = {
        "recipes": {"cooking_sessions"},
        "cooking_sessions": {"cooking_consumptions"},
    }
    ts = TopologicalSorter(user_graph)
    order = list(ts.static_order())
    assert order.index("cooking_consumptions") < order.index("cooking_sessions")
    assert order.index("cooking_sessions") < order.index("recipes")


# =========================================================================
# Integration Tests with Throwaway PostgreSQL (pgserver)
# =========================================================================


@pytest.mark.skipif(not PGSERVER_AVAILABLE, reason="pgserver is not available in environment")
@pytest.mark.asyncio
async def test_replace_catalog_protective_and_delete_user_data_modes(tmp_path: Path) -> None:
    """Comprehensive test exercising both protective retention and cascade deletion."""
    import asyncio
    import os
    import subprocess
    import sys
    import tempfile

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from AI.catalog.snapshot import load_snapshot

    pg_dir = Path(tempfile.mkdtemp(prefix="pg_replace_test_"))
    srv = pgserver.get_server(pg_dir, cleanup_mode="stop")
    uri = srv.get_uri().replace("postgresql://", "postgresql+asyncpg://", 1)

    backend_root = Path(__file__).resolve().parents[2]

    try:
        # Run alembic upgrade head
        res = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=backend_root,
            env=dict(os.environ, DATABASE_URL=uri, PYTHONUTF8="1"),
            check=False,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, res.stderr

        engine = create_async_engine(uri, connect_args={"statement_cache_size": 0})

        # Load real bundle to know bundle IDs
        bundle_raw = load_catalog_bundle(DEFAULT_BUNDLE_DIR)
        bundle_data, _ = transform_catalog_bundle(bundle_raw)
        bundle_r1_id = bundle_data.recipes[0]["id"]
        bundle_r1_name = bundle_data.recipes[0]["name"]
        bundle_m1_name = bundle_data.masters[0]["name"]
        bundle_m1_cat = bundle_data.masters[0]["category_id"]

        legacy_m1_id = UUID("aaaaaaaa-1111-1111-1111-111111111111")
        unprotected_legacy_m2_id = UUID("aaaaaaaa-2222-2222-2222-222222222222")
        protected_legacy_m3_id = UUID("aaaaaaaa-3333-3333-3333-333333333333")

        protected_legacy_r1_id = UUID("bbbbbbbb-1111-1111-1111-111111111111")
        unprotected_legacy_r2_id = UUID("bbbbbbbb-2222-2222-2222-222222222222")
        conflict_legacy_r3_id = UUID("bbbbbbbb-3333-3333-3333-333333333333")

        test_user_id = UUID("cccccccc-1111-1111-1111-111111111111")

        # Seed initial simulated DB
        async with engine.begin() as conn:
            # Insert categories
            for cat in bundle_data.categories[:3]:
                await conn.execute(
                    text("INSERT INTO ingredient_categories (id, name, description) VALUES (:id, :name, :description) ON CONFLICT DO NOTHING;"),
                    {"id": cat["id"], "name": cat["name"], "description": cat["description"]},
                )

            # Insert user (account)
            await conn.execute(
                text("INSERT INTO users (id, phone_e164, name, email, password_hash, role, status, phone_verified_at) VALUES (:id, '+84999999999', 'Test User', 'user@test.local', 'dummy_hash', 'USER', 'ACTIVE', now());"),
                {"id": test_user_id},
            )

            # Insert masters:
            # legacy_m1 has same (category, name) as bundle_data.masters[0] but different ID!
            await conn.execute(
                text("INSERT INTO master_ingredients (id, name, category_id, canonical_unit) VALUES (:id, :name, :cat_id, 'GRAM');"),
                {"id": legacy_m1_id, "name": bundle_m1_name, "cat_id": bundle_m1_cat},
            )
            # unprotected legacy_m2
            await conn.execute(
                text("INSERT INTO master_ingredients (id, name, category_id, canonical_unit) VALUES (:id, 'Unprotected Master', :cat_id, 'GRAM');"),
                {"id": unprotected_legacy_m2_id, "cat_id": bundle_m1_cat},
            )
            # protected legacy_m3 (referenced by inventory batch)
            await conn.execute(
                text("INSERT INTO master_ingredients (id, name, category_id, canonical_unit) VALUES (:id, 'Protected Master', :cat_id, 'GRAM');"),
                {"id": protected_legacy_m3_id, "cat_id": bundle_m1_cat},
            )

            # Insert recipes:
            # Overlap bundle recipe
            await conn.execute(
                text("INSERT INTO recipes (id, name, description, instructions, source_url, default_servings, estimated_cooking_minutes) VALUES (:id, 'Old Recipe 1', 'Desc', '{}'::jsonb, 'http://old.test/1', 2, 15);"),
                {"id": bundle_r1_id},
            )
            # Protected legacy recipe (referenced by favorite_recipes)
            await conn.execute(
                text("INSERT INTO recipes (id, name, description, instructions, source_url, default_servings, estimated_cooking_minutes) VALUES (:id, 'Protected Legacy Recipe', 'Desc', '{}'::jsonb, 'http://legacy.test/protected', 2, 15);"),
                {"id": protected_legacy_r1_id},
            )
            # Unprotected legacy recipe
            await conn.execute(
                text("INSERT INTO recipes (id, name, description, instructions, source_url, default_servings, estimated_cooking_minutes) VALUES (:id, 'Unprotected Legacy Recipe', 'Desc', '{}'::jsonb, 'http://legacy.test/unprotected', 2, 15);"),
                {"id": unprotected_legacy_r2_id},
            )
            # Conflicting legacy recipe (same name as bundle recipe, different ID, protected by cooking session)
            await conn.execute(
                text("INSERT INTO recipes (id, name, description, instructions, source_url, default_servings, estimated_cooking_minutes) VALUES (:id, :name, 'Desc', '{}'::jsonb, 'http://legacy.test/conflict', 2, 15);"),
                {"id": conflict_legacy_r3_id, "name": bundle_r1_name},
            )

            # User activity rows:
            # favorite_recipes -> protected_legacy_r1
            await conn.execute(
                text("INSERT INTO favorite_recipes (id, user_id, recipe_id) VALUES (gen_random_uuid(), :uid, :rid);"),
                {"uid": test_user_id, "rid": protected_legacy_r1_id},
            )
            # cooking_session -> conflict_legacy_r3
            cs_id = UUID("dddddddd-1111-1111-1111-111111111111")
            await conn.execute(
                text("INSERT INTO cooking_sessions (id, user_id, recipe_id, servings, status) VALUES (:id, :uid, :rid, 2.0, 'COMPLETED');"),
                {"id": cs_id, "uid": test_user_id, "rid": conflict_legacy_r3_id},
            )
            # inventory_batch -> protected_legacy_m3
            batch_id = UUID("eeeeeeee-1111-1111-1111-111111111111")
            await conn.execute(
                text("INSERT INTO inventory_batches (id, user_id, master_ingredient_id, initial_quantity, current_quantity, unit, storage_mode, status, batch_type, expiration_source, source) VALUES (:id, :uid, :mid, 100, 100, 'GRAM', 'ROOM_TEMPERATURE', 'ACTIVE', 'RAW_INGREDIENT', 'ESTIMATED', 'MANUAL');"),
                {"id": batch_id, "uid": test_user_id, "mid": protected_legacy_m3_id},
            )

        # -------------------------------------------------------------
        # Part A: Protective Retention Mode (--replace-catalog, NO --delete-user-data)
        # -------------------------------------------------------------
        # 1. Dry run
        dry_opts = ReplaceOptions(
            bundle_dir=DEFAULT_BUNDLE_DIR,
            dry_run=True,
            database_url=uri,
        )
        plan_dry = await run_replace_catalog(dry_opts)
        assert protected_legacy_r1_id in plan_dry.retained_legacy_recipes
        assert protected_legacy_m3_id in plan_dry.retained_legacy_masters
        assert unprotected_legacy_r2_id in plan_dry.unprotected_recipes_to_delete
        assert unprotected_legacy_m2_id in plan_dry.unprotected_masters_to_delete
        assert any(c["id"] == str(conflict_legacy_r3_id) for c in plan_dry.conflicting_recipes_to_rename)

        # Check DB unchanged after dry-run
        async with engine.connect() as conn:
            cnt_u = (await conn.execute(text("SELECT count(*) FROM users;"))).scalar()
            assert cnt_u == 1

        # 2. Real Run (protective)
        backup_dir = tmp_path / "backup_protective"
        real_opts = ReplaceOptions(
            bundle_dir=DEFAULT_BUNDLE_DIR,
            dry_run=False,
            database_url=uri,
            backup_dir=backup_dir,
        )
        await run_replace_catalog(real_opts)

        # Assertions post protective run:
        async with engine.connect() as conn:
            # Bundle recipes present and have ai_features
            cnt_ai_r = (await conn.execute(text("SELECT count(*) FROM recipes WHERE ai_features <> '{}'::jsonb;"))).scalar()
            assert cnt_ai_r == 1075

            # Unprotected legacy rows deleted
            cnt_unprot_r = (await conn.execute(text("SELECT count(*) FROM recipes WHERE id = :id;"), {"id": unprotected_legacy_r2_id})).scalar()
            assert cnt_unprot_r == 0
            cnt_unprot_m = (await conn.execute(text("SELECT count(*) FROM master_ingredients WHERE id = :id;"), {"id": unprotected_legacy_m2_id})).scalar()
            assert cnt_unprot_m == 0

            # Protected legacy rows retained!
            cnt_prot_r = (await conn.execute(text("SELECT count(*) FROM recipes WHERE id = :id;"), {"id": protected_legacy_r1_id})).scalar()
            assert cnt_prot_r == 1
            cnt_prot_m = (await conn.execute(text("SELECT count(*) FROM master_ingredients WHERE id = :id;"), {"id": protected_legacy_m3_id})).scalar()
            assert cnt_prot_m == 1

            # Conflict recipe renamed
            conf_name = (await conn.execute(text("SELECT name FROM recipes WHERE id = :id;"), {"id": conflict_legacy_r3_id})).scalar()
            assert conf_name.endswith(f"(legacy {str(conflict_legacy_r3_id)[:8]})")

            # Matched master kept its OLD id and received source_code
            m_matched_code = (await conn.execute(text("SELECT source_code FROM master_ingredients WHERE id = :id;"), {"id": legacy_m1_id})).scalar()
            assert m_matched_code is not None

            # User data preserved
            cnt_fav = (await conn.execute(text("SELECT count(*) FROM favorite_recipes;"))).scalar()
            assert cnt_fav == 1
            cnt_cs = (await conn.execute(text("SELECT count(*) FROM cooking_sessions;"))).scalar()
            assert cnt_cs == 1
            cnt_batch = (await conn.execute(text("SELECT count(*) FROM inventory_batches;"))).scalar()
            assert cnt_batch == 1

        # 3. Snapshot verification: loads exactly 1075 recipes and excludes legacy retained rows
        async with engine.connect() as conn:
            session_factory = async_sessionmaker(engine, expire_on_commit=False)
            async with session_factory() as session:
                snap = await load_snapshot(session)
                assert len(snap.recipes) == 1075
                assert len(snap.ingredients) == 10406
                assert str(protected_legacy_r1_id) not in snap.recipes_by_id

        # 4. Idempotency test: Run 2 is a no-op
        plan_run2 = await run_replace_catalog(real_opts)
        assert len(plan_run2.unprotected_recipes_to_delete) == 0
        assert len(plan_run2.unprotected_masters_to_delete) == 0

        # -------------------------------------------------------------
        # Part B: Delete User Data Mode (--replace-catalog --delete-user-data)
        # -------------------------------------------------------------
        # Now run with delete_user_data=True
        del_user_opts = ReplaceOptions(
            bundle_dir=DEFAULT_BUNDLE_DIR,
            delete_user_data=True,
            database_url=uri,
            backup_dir=tmp_path / "backup_cascade",
        )
        await run_replace_catalog(del_user_opts)

        async with engine.connect() as conn:
            # Users account is NEVER deleted
            cnt_u = (await conn.execute(text("SELECT count(*) FROM users;"))).scalar()
            assert cnt_u == 1

            # Legacy recipe protected_legacy_r1 and its favorite_recipes were deleted
            cnt_prot_r = (await conn.execute(text("SELECT count(*) FROM recipes WHERE id = :id;"), {"id": protected_legacy_r1_id})).scalar()
            assert cnt_prot_r == 0
            cnt_fav = (await conn.execute(text("SELECT count(*) FROM favorite_recipes;"))).scalar()
            assert cnt_fav == 0

            # Legacy master protected_legacy_m3 and its inventory_batches were deleted
            cnt_prot_m = (await conn.execute(text("SELECT count(*) FROM master_ingredients WHERE id = :id;"), {"id": protected_legacy_m3_id})).scalar()
            assert cnt_prot_m == 0
            cnt_batch = (await conn.execute(text("SELECT count(*) FROM inventory_batches;"))).scalar()
            assert cnt_batch == 0

            # 1075 bundle recipes still healthy
            cnt_ai_r = (await conn.execute(text("SELECT count(*) FROM recipes WHERE ai_features <> '{}'::jsonb;"))).scalar()
            assert cnt_ai_r == 1075

        await engine.dispose()
    finally:
        srv.cleanup()
