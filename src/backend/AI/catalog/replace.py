"""Safe catalog replacement pipeline preserving user-activity data or cascading user data."""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Final, cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from AI.catalog.importer import (
    DEFAULT_BUNDLE_DIR,
    CatalogTransformedData,
    load_catalog_bundle,
    resolve_database_url,
    transform_catalog_bundle,
)
from src.db import build_async_database_url

logger = logging.getLogger(__name__)

REFERENCE_DATA_TABLES: Final[frozenset[str]] = frozenset({
    "ingredient_aliases",
    "shelf_life_rules",
    "master_ingredient_freshcheck_mappings",
})

ACCOUNT_TABLES: Final[frozenset[str]] = frozenset({
    "users",
    "auth_sessions",
    "device_registration",
    "device_registrations",
    "user_notification_preferences",
    "user_notification_preference",
    "premium_interest",
    "premium_interests",
})

CATALOG_TABLES: Final[frozenset[str]] = frozenset({
    "ingredient_categories",
    "master_ingredients",
    "ingredient_aliases",
    "recipes",
    "recipe_ingredients",
})


@dataclass(frozen=True)
class ForeignKeyLink:
    """Discovered foreign key constraint from PostgreSQL catalogs."""

    constraint_name: str
    src_table: str
    src_column: str
    dst_table: str
    dst_column: str


@dataclass(frozen=True)
class ReplaceOptions:
    """Runtime options for catalog replacement."""

    bundle_dir: Path = DEFAULT_BUNDLE_DIR
    backup_dir: Path | None = None
    delete_user_data: bool = False
    dry_run: bool = False
    database_url: str | None = None
    batch_size: int = 500


@dataclass
class ReplaceCatalogPlan:
    """Preflight execution plan for catalog replacement."""

    categories_to_insert: list[dict[str, object]] = field(default_factory=list)
    masters_to_update: list[dict[str, object]] = field(default_factory=list)
    masters_to_insert: list[dict[str, object]] = field(default_factory=list)
    aliases_to_insert: list[dict[str, object]] = field(default_factory=list)
    recipes_to_upsert: list[dict[str, object]] = field(default_factory=list)
    recipe_ingredients_to_upsert: list[dict[str, object]] = field(default_factory=list)

    conflicting_recipes_to_rename: list[dict[str, str]] = field(default_factory=list)

    unprotected_recipes_to_delete: set[UUID] = field(default_factory=set)
    unprotected_ingredients_to_delete: set[UUID] = field(default_factory=set)
    unprotected_masters_to_delete: set[UUID] = field(default_factory=set)

    retained_legacy_recipes: dict[UUID, str] = field(default_factory=dict)
    retained_legacy_masters: dict[UUID, str] = field(default_factory=dict)
    retained_legacy_ingredients: dict[UUID, str] = field(default_factory=dict)

    user_rows_to_delete: dict[str, list[UUID]] = field(default_factory=lambda: defaultdict(list))
    user_deletion_chains: dict[str, str] = field(default_factory=dict)
    preflight_counts: dict[str, int] = field(default_factory=dict)
    alias_duplicates_rejected: int = 0


def json_serializer(obj: object) -> object:
    """Serialize UUID, Decimal, and datetime objects to JSON primitives."""
    if isinstance(obj, (UUID, Decimal)):
        return str(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not JSON serializable")


async def discover_foreign_keys(conn: AsyncConnection) -> list[ForeignKeyLink]:
    """Discover all foreign key constraints in schema public from pg_constraint."""
    query = """
    SELECT
        c.conname AS constraint_name,
        src_cl.relname AS src_table,
        src_att.attname AS src_column,
        dst_cl.relname AS dst_table,
        dst_att.attname AS dst_column
    FROM pg_constraint c
    JOIN pg_class src_cl ON src_cl.oid = c.conrelid
    JOIN pg_namespace src_ns ON src_ns.oid = src_cl.relnamespace
    JOIN pg_attribute src_att ON src_att.attrelid = src_cl.oid AND src_att.attnum = ANY(c.conkey)
    JOIN pg_class dst_cl ON dst_cl.oid = c.confrelid
    JOIN pg_namespace dst_ns ON dst_ns.oid = dst_cl.relnamespace
    JOIN pg_attribute dst_att ON dst_att.attrelid = dst_cl.oid AND dst_att.attnum = ANY(c.confkey)
    WHERE c.contype = 'f' AND src_ns.nspname = 'public' AND cardinality(c.conkey) = 1
    ORDER BY dst_cl.relname, src_cl.relname;
    """
    # A composite foreign key cannot be represented as one column pair. None may point into the
    # catalog tables this tool rewrites; if one ever does, stop instead of planning wrongly.
    composite = await conn.execute(
        text(
            "SELECT c.conname FROM pg_constraint c JOIN pg_class d ON d.oid = c.confrelid "
            "WHERE c.contype = 'f' AND cardinality(c.conkey) > 1 "
            "AND d.relname = ANY(:catalog_tables);"
        ),
        {"catalog_tables": sorted(CATALOG_TABLES)},
    )
    composite_names = [row[0] for row in composite.all()]
    if composite_names:
        raise ValueError(
            f"Composite foreign keys into catalog tables are not supported: {composite_names}"
        )
    result = await conn.execute(text(query))
    return [
        ForeignKeyLink(
            constraint_name=row["constraint_name"],
            src_table=row["src_table"],
            src_column=row["src_column"],
            dst_table=row["dst_table"],
            dst_column=row["dst_column"],
        )
        for row in result.mappings().all()
    ]


async def build_replace_plan(
    conn: AsyncConnection,
    bundle_data: CatalogTransformedData,
    fks: list[ForeignKeyLink],
    options: ReplaceOptions,
) -> ReplaceCatalogPlan:
    """Analyze DB state against bundle and build an atomic replacement plan."""
    plan = ReplaceCatalogPlan()

    # Preflight row counts for all tables
    all_tables_query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
    tables_res = await conn.execute(text(all_tables_query))
    db_tables = [r[0] for r in tables_res.all()]
    for tbl in db_tables:
        cnt_res = await conn.execute(text(f"SELECT count(*) FROM {tbl}"))
        plan.preflight_counts[tbl] = int(cnt_res.scalar() or 0)

    # 1. Categories
    existing_cats_res = await conn.execute(text("SELECT id, name FROM ingredient_categories;"))
    existing_cat_names = {r["name"].strip().casefold(): r["id"] for r in existing_cats_res.mappings().all()}
    for cat in bundle_data.categories:
        if str(cat["name"]).strip().casefold() not in existing_cat_names:
            plan.categories_to_insert.append(cat)

    # 2. Master identity matching: (category_id, lower(name))
    existing_masters_res = await conn.execute(
        text("SELECT id, category_id, name, source_code FROM master_ingredients;")
    )
    existing_masters = existing_masters_res.mappings().all()
    existing_master_by_nat: dict[tuple[UUID, str], UUID] = {
        (r["category_id"], str(r["name"]).strip().casefold()): r["id"]
        for r in existing_masters
    }
    existing_master_ids = {r["id"] for r in existing_masters}

    resolved_master_ids: dict[UUID, UUID] = {}
    kept_master_ids: set[UUID] = set()

    for bm in bundle_data.masters:
        bundle_id = cast(UUID, bm["id"])
        nat_key = (cast(UUID, bm["category_id"]), str(bm["name"]).strip().casefold())
        matched_id = existing_master_by_nat.get(nat_key)
        if matched_id is not None:
            resolved_master_ids[bundle_id] = matched_id
            kept_master_ids.add(matched_id)
            updated_master = dict(bm)
            updated_master["id"] = matched_id
            plan.masters_to_update.append(updated_master)
        else:
            resolved_master_ids[bundle_id] = bundle_id
            kept_master_ids.add(bundle_id)
            plan.masters_to_insert.append(bm)

    # 3. Aliases
    existing_aliases_res = await conn.execute(text("SELECT normalized_alias FROM ingredient_aliases;"))
    existing_alias_norms = {r[0] for r in existing_aliases_res.all()}
    for alias in bundle_data.aliases:
        norm = cast(str, alias["normalized_alias"])
        if norm not in existing_alias_norms:
            alias_to_insert = dict(alias)
            orig_m_id = cast(UUID, alias["master_ingredient_id"])
            alias_to_insert["master_ingredient_id"] = resolved_master_ids.get(orig_m_id, orig_m_id)
            plan.aliases_to_insert.append(alias_to_insert)

    # 4. Recipes
    bundle_recipes = bundle_data.recipes
    bundle_recipe_ids = {cast(UUID, r["id"]) for r in bundle_recipes}
    bundle_recipe_names = {str(r["name"]).strip().casefold(): cast(UUID, r["id"]) for r in bundle_recipes}
    bundle_recipe_urls = {str(r["source_url"]).strip(): cast(UUID, r["id"]) for r in bundle_recipes}
    plan.recipes_to_upsert = [dict(r) for r in bundle_recipes]

    existing_recipes_res = await conn.execute(text("SELECT id, name, source_url FROM recipes;"))
    existing_recipes = existing_recipes_res.mappings().all()
    all_legacy_recipe_ids = {r["id"] for r in existing_recipes}
    removed_recipe_candidates = all_legacy_recipe_ids - bundle_recipe_ids

    # 5. Recipe Ingredients
    for ing in bundle_data.recipe_ingredients:
        ing_row = dict(ing)
        orig_mid = cast(UUID, ing["master_ingredient_id"])
        ing_row["master_ingredient_id"] = resolved_master_ids.get(orig_mid, orig_mid)
        plan.recipe_ingredients_to_upsert.append(ing_row)

    bundle_ing_ids = {cast(UUID, ing["id"]) for ing in bundle_data.recipe_ingredients}
    existing_ings_res = await conn.execute(text("SELECT id, recipe_id FROM recipe_ingredients;"))
    all_legacy_ings = existing_ings_res.mappings().all()
    all_legacy_ing_ids = {r["id"] for r in all_legacy_ings}
    removed_ing_candidates = all_legacy_ing_ids - bundle_ing_ids

    # 6. Legacy and Conflict analysis
    # Map foreign keys pointing into recipes, recipe_ingredients, master_ingredients
    fks_by_dst: dict[str, list[ForeignKeyLink]] = defaultdict(list)
    for fk in fks:
        fks_by_dst[fk.dst_table].append(fk)

    if not options.delete_user_data:
        # PROTECTIVE RETENTION MODE
        # Protect recipes referenced by non-catalog tables
        for fk in fks_by_dst.get("recipes", []):
            if fk.src_table in CATALOG_TABLES:
                continue
            refs_res = await conn.execute(
                text(f"SELECT DISTINCT {fk.src_column} FROM {fk.src_table} WHERE {fk.src_column} IS NOT NULL;")
            )
            ref_ids = {r[0] for r in refs_res.all()}
            for rid in ref_ids:
                if rid in removed_recipe_candidates:
                    plan.retained_legacy_recipes[rid] = fk.src_table

        # Unprotected legacy recipes are marked for deletion
        plan.unprotected_recipes_to_delete = removed_recipe_candidates - set(plan.retained_legacy_recipes.keys())

        # Recipe ingredients protection (cooking_consumptions)
        for fk in fks_by_dst.get("recipe_ingredients", []):
            refs_res = await conn.execute(
                text(f"SELECT DISTINCT {fk.src_column} FROM {fk.src_table} WHERE {fk.src_column} IS NOT NULL;")
            )
            ref_ids = {r[0] for r in refs_res.all()}
            for iid in ref_ids:
                if iid in removed_ing_candidates:
                    plan.retained_legacy_ingredients[iid] = fk.src_table

        # Ingredients of deleted recipes or obsolete bundle ingredients deleted if unprotected
        for ing_row in all_legacy_ings:
            iid = ing_row["id"]
            rid = ing_row["recipe_id"]
            if (
                rid in plan.unprotected_recipes_to_delete
                or (rid in bundle_recipe_ids and iid not in bundle_ing_ids)
            ) and iid not in plan.retained_legacy_ingredients:
                plan.unprotected_ingredients_to_delete.add(iid)

        # Protect master ingredients
        # Reference tables protect masters always
        for ref_tbl in REFERENCE_DATA_TABLES:
            for fk in fks_by_dst.get("master_ingredients", []):
                if fk.src_table == ref_tbl:
                    refs_res = await conn.execute(
                        text(f"SELECT DISTINCT {fk.src_column} FROM {fk.src_table} WHERE {fk.src_column} IS NOT NULL;")
                    )
                    for r in refs_res.all():
                        if r[0] in existing_master_ids and r[0] not in kept_master_ids:
                            plan.retained_legacy_masters[r[0]] = ref_tbl

        # User activity tables protect masters
        for fk in fks_by_dst.get("master_ingredients", []):
            if fk.src_table in CATALOG_TABLES or fk.src_table in REFERENCE_DATA_TABLES:
                continue
            refs_res = await conn.execute(
                text(f"SELECT DISTINCT {fk.src_column} FROM {fk.src_table} WHERE {fk.src_column} IS NOT NULL;")
            )
            for r in refs_res.all():
                if r[0] in existing_master_ids and r[0] not in kept_master_ids:
                    plan.retained_legacy_masters[r[0]] = fk.src_table

        # Retained ingredients also protect their masters
        for ing_row in all_legacy_ings:
            if ing_row["id"] in plan.retained_legacy_ingredients:
                mid_res = await conn.execute(
                    text("SELECT master_ingredient_id FROM recipe_ingredients WHERE id = :id"),
                    {"id": ing_row["id"]},
                )
                mid_val = mid_res.scalar()
                if mid_val and mid_val in existing_master_ids and mid_val not in kept_master_ids:
                    plan.retained_legacy_masters[mid_val] = "recipe_ingredients (retained)"

        # Unprotected masters not in keep set are deleted
        all_legacy_master_ids = existing_master_ids - kept_master_ids
        plan.unprotected_masters_to_delete = all_legacy_master_ids - set(plan.retained_legacy_masters.keys())

    else:
        # DELETE USER DATA MODE
        # All legacy recipes not in bundle are to be removed
        plan.unprotected_recipes_to_delete = removed_recipe_candidates
        plan.unprotected_ingredients_to_delete = removed_ing_candidates

        # Reference tables protect their masters (reference data is NOT user data)
        for ref_tbl in REFERENCE_DATA_TABLES:
            for fk in fks_by_dst.get("master_ingredients", []):
                if fk.src_table == ref_tbl:
                    refs_res = await conn.execute(
                        text(f"SELECT DISTINCT {fk.src_column} FROM {fk.src_table} WHERE {fk.src_column} IS NOT NULL;")
                    )
                    for r in refs_res.all():
                        if r[0] in existing_master_ids and r[0] not in kept_master_ids:
                            plan.retained_legacy_masters[r[0]] = ref_tbl

        all_legacy_master_ids = existing_master_ids - kept_master_ids
        plan.unprotected_masters_to_delete = all_legacy_master_ids - set(plan.retained_legacy_masters.keys())

        # Recursively find user rows referencing removed recipes/masters/ingredients
        target_deletions: list[tuple[str, str, set[UUID]]] = [
            ("recipes", "id", plan.unprotected_recipes_to_delete),
            ("recipe_ingredients", "id", plan.unprotected_ingredients_to_delete),
            ("master_ingredients", "id", plan.unprotected_masters_to_delete),
        ]

        # BFS cascade tracking
        queue: list[tuple[str, set[UUID]]] = [
            (tbl, ids) for tbl, _, ids in target_deletions if ids
        ]
        visited_deleted: dict[str, set[UUID]] = defaultdict(set)

        while queue:
            curr_target_table, curr_target_ids = queue.pop(0)
            if not curr_target_ids:
                continue

            for fk in fks_by_dst.get(curr_target_table, []):
                src_tbl = fk.src_table
                if src_tbl in ACCOUNT_TABLES or src_tbl in REFERENCE_DATA_TABLES or src_tbl in CATALOG_TABLES:
                    continue

                # Query dependent rows in child user table
                # Bounded query using ANY(:ids)
                id_list = list(curr_target_ids)
                chunk_size = 1000
                child_ids: set[UUID] = set()
                for i in range(0, len(id_list), chunk_size):
                    chunk = id_list[i : i + chunk_size]
                    q = text(f"SELECT id FROM {src_tbl} WHERE {fk.src_column} = ANY(:ids);")
                    c_res = await conn.execute(q, {"ids": chunk})
                    child_ids.update(r[0] for r in c_res.all())

                new_child_ids = child_ids - visited_deleted[src_tbl]
                if new_child_ids:
                    visited_deleted[src_tbl].update(new_child_ids)
                    chain_str = plan.user_deletion_chains.get(curr_target_table, curr_target_table)
                    plan.user_deletion_chains[src_tbl] = f"{src_tbl} <- {chain_str}"
                    queue.append((src_tbl, new_child_ids))

        # Order user table deletions topologically (children before parents)
        # Build dependency graph among user tables
        user_graph: dict[str, set[str]] = defaultdict(set)
        for tbl, ids in visited_deleted.items():
            plan.user_rows_to_delete[tbl] = list(ids)
            user_graph[tbl] = set()

        for fk in fks:
            if fk.src_table in visited_deleted and fk.dst_table in visited_deleted and fk.src_table != fk.dst_table:
                # dst_table requires src_table (child) to be deleted first
                user_graph[fk.dst_table].add(fk.src_table)

        # Topological sort
        from graphlib import CycleError, TopologicalSorter

        ts = TopologicalSorter(user_graph)
        try:
            sorted_order = list(ts.static_order())
        except (CycleError, ValueError):
            sorted_order = list(visited_deleted.keys())

        # Reorder user_rows_to_delete according to topological order
        ordered_user_deletions = {tbl: plan.user_rows_to_delete[tbl] for tbl in sorted_order if tbl in plan.user_rows_to_delete}
        plan.user_rows_to_delete = ordered_user_deletions

    # Check for recipe name/URL conflicts between retained legacy recipes and bundle recipes
    for r_row in existing_recipes:
        r_id = r_row["id"]
        r_name_low = str(r_row["name"]).strip().casefold()
        r_url = str(r_row["source_url"]).strip()

        is_retained = r_id in plan.retained_legacy_recipes
        conflicts = (
            (r_name_low in bundle_recipe_names and bundle_recipe_names[r_name_low] != r_id)
            or (r_url in bundle_recipe_urls and bundle_recipe_urls[r_url] != r_id)
        )
        if conflicts:
            if is_retained:
                short_id = str(r_id)[:8]
                new_name = f"{r_row['name']} (legacy {short_id})"
                new_url = f"{r_row['source_url']}?legacy={short_id}"
                plan.conflicting_recipes_to_rename.append({
                    "id": str(r_id),
                    "name": new_name,
                    "source_url": new_url,
                })
            else:
                plan.unprotected_recipes_to_delete.add(r_id)

    return plan


def write_backup(
    plan: ReplaceCatalogPlan,
    db_rows_to_backup: dict[str, list[dict[str, object]]],
    backup_dir: Path,
) -> Path:
    """Serialize all overwritten or deleted rows and execution plan to disk."""
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Write JSONL for each table
    for table_name, rows in db_rows_to_backup.items():
        if not rows:
            continue
        file_path = backup_dir / f"{table_name}.jsonl"
        with file_path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, default=json_serializer, ensure_ascii=False) + "\n")

    # Write plan.json
    plan_dict = {
        "preflight_counts": plan.preflight_counts,
        "categories_to_insert": len(plan.categories_to_insert),
        "masters_to_update": len(plan.masters_to_update),
        "masters_to_insert": len(plan.masters_to_insert),
        "aliases_to_insert": len(plan.aliases_to_insert),
        "recipes_to_upsert": len(plan.recipes_to_upsert),
        "recipe_ingredients_to_upsert": len(plan.recipe_ingredients_to_upsert),
        "conflicting_recipes_to_rename": plan.conflicting_recipes_to_rename,
        "unprotected_recipes_to_delete": [str(x) for x in plan.unprotected_recipes_to_delete],
        "unprotected_ingredients_to_delete": [str(x) for x in plan.unprotected_ingredients_to_delete],
        "unprotected_masters_to_delete": [str(x) for x in plan.unprotected_masters_to_delete],
        "retained_legacy_recipes": {str(k): v for k, v in plan.retained_legacy_recipes.items()},
        "retained_legacy_masters": {str(k): v for k, v in plan.retained_legacy_masters.items()},
        "user_rows_to_delete": {k: [str(x) for x in v] for k, v in plan.user_rows_to_delete.items()},
        "user_deletion_chains": plan.user_deletion_chains,
    }
    with (backup_dir / "plan.json").open("w", encoding="utf-8") as fh:
        json.dump(plan_dict, fh, indent=2, ensure_ascii=False)

    # Write restore README
    readme_text = (
        "Catalog Replacement Row-Level Backup\n"
        "====================================\n\n"
        f"Timestamp: {datetime.now(UTC).isoformat()}\n"
        "This directory contains full row-level JSONL backups of every row\n"
        "overwritten or deleted during python -m AI.catalog.importer --replace-catalog.\n\n"
        "Files:\n"
        "- plan.json: Summary of planned operations, counts, and retained IDs\n"
        "- <table_name>.jsonl: Complete JSON representation of each affected row\n\n"
        "To inspect or restore rows, read the JSONL files into dictionaries and\n"
        "insert back into the corresponding tables using SQLAlchemy or psql.\n"
    )
    with (backup_dir / "README.txt").open("w", encoding="utf-8") as fh:
        fh.write(readme_text)

    return backup_dir


def print_plan_summary(plan: ReplaceCatalogPlan, options: ReplaceOptions) -> None:
    """Print structured table of planned operations and retained records."""
    header = f"{'Table':<32} {'Inserted':<10} {'Updated':<10} {'Unchanged':<10} {'Deleted':<10} {'Retained':<10}"
    divider = "-" * 82
    print("\n" + "=" * 82)
    print("CATALOG REPLACEMENT EXECUTION PLAN" + (" (DRY RUN)" if options.dry_run else ""))
    print("=" * 82)
    print(header)
    print(divider)

    print(
        f"{'ingredient_categories':<32} {len(plan.categories_to_insert):<10} {0:<10} "
        f"{plan.preflight_counts.get('ingredient_categories', 0):<10} {0:<10} {0:<10}"
    )
    print(
        f"{'master_ingredients':<32} {len(plan.masters_to_insert):<10} {len(plan.masters_to_update):<10} "
        f"{0:<10} {len(plan.unprotected_masters_to_delete):<10} {len(plan.retained_legacy_masters):<10}"
    )
    print(
        f"{'ingredient_aliases':<32} {len(plan.aliases_to_insert):<10} {0:<10} "
        f"{plan.preflight_counts.get('ingredient_aliases', 0):<10} {0:<10} {0:<10}"
    )
    print(
        f"{'recipes':<32} {len(plan.recipes_to_upsert):<10} {0:<10} "
        f"{0:<10} {len(plan.unprotected_recipes_to_delete):<10} {len(plan.retained_legacy_recipes):<10}"
    )
    print(
        f"{'recipe_ingredients':<32} {len(plan.recipe_ingredients_to_upsert):<10} {0:<10} "
        f"{0:<10} {len(plan.unprotected_ingredients_to_delete):<10} {len(plan.retained_legacy_ingredients):<10}"
    )

    if plan.user_rows_to_delete:
        print(divider)
        print("User Data Deletions (--delete-user-data):")
        for tbl, ids in plan.user_rows_to_delete.items():
            chain = plan.user_deletion_chains.get(tbl, tbl)
            print(f"  {tbl:<30} {len(ids):<6} rows to delete (chain: {chain})")

    print(divider)
    if plan.retained_legacy_recipes:
        print(f"Retained Legacy Recipes ({len(plan.retained_legacy_recipes)} protected):")
        for rid, reason in list(plan.retained_legacy_recipes.items())[:5]:
            print(f"  {rid} (protected by: {reason})")
        if len(plan.retained_legacy_recipes) > 5:
            print(f"  ... and {len(plan.retained_legacy_recipes) - 5} more (see plan.json)")

    if plan.retained_legacy_masters:
        print(f"Retained Legacy Masters ({len(plan.retained_legacy_masters)} protected):")
        for mid, reason in list(plan.retained_legacy_masters.items())[:5]:
            print(f"  {mid} (protected by: {reason})")
        if len(plan.retained_legacy_masters) > 5:
            print(f"  ... and {len(plan.retained_legacy_masters) - 5} more (see plan.json)")

    if plan.conflicting_recipes_to_rename:
        print(f"Conflicting Protected Recipes to Rename ({len(plan.conflicting_recipes_to_rename)}):")
        for item in plan.conflicting_recipes_to_rename:
            print(f"  {item['id']} -> {item['name']}")
    print("=" * 82 + "\n")


async def execute_replace_plan(
    conn: AsyncConnection,
    plan: ReplaceCatalogPlan,
    fks: list[ForeignKeyLink],
    options: ReplaceOptions,
) -> None:
    """Execute the mutation steps atomically inside the transaction."""
    # 0. User data deletions (child tables first, per topological order)
    if options.delete_user_data and plan.user_rows_to_delete:
        for tbl, ids in plan.user_rows_to_delete.items():
            if ids:
                for i in range(0, len(ids), options.batch_size):
                    chunk = ids[i : i + options.batch_size]
                    await conn.execute(text(f"DELETE FROM {tbl} WHERE id = ANY(:ids);"), {"ids": chunk})

    # 1. Rename conflicting protected recipes to free unique(lower(name)) and unique(source_url)
    for conf in plan.conflicting_recipes_to_rename:
        await conn.execute(
            text("UPDATE recipes SET name = :name, source_url = :source_url WHERE id = :id;"),
            {"id": conf["id"], "name": conf["name"], "source_url": conf["source_url"]},
        )

    # 2. Delete unprotected conflicting / removed recipes & ingredients first to avoid constraint collisions
    if plan.unprotected_ingredients_to_delete:
        del_ings = list(plan.unprotected_ingredients_to_delete)
        for i in range(0, len(del_ings), options.batch_size):
            chunk = del_ings[i : i + options.batch_size]
            await conn.execute(text("DELETE FROM recipe_ingredients WHERE id = ANY(:ids);"), {"ids": chunk})

    if plan.unprotected_recipes_to_delete:
        del_recs = list(plan.unprotected_recipes_to_delete)
        for i in range(0, len(del_recs), options.batch_size):
            chunk = del_recs[i : i + options.batch_size]
            await conn.execute(text("DELETE FROM recipes WHERE id = ANY(:ids);"), {"ids": chunk})

    # 3. Insert categories
    if plan.categories_to_insert:
        cat_stmt = """
        INSERT INTO ingredient_categories (id, name, description)
        VALUES (:id, :name, :description)
        ON CONFLICT (id) DO NOTHING;
        """
        await conn.execute(text(cat_stmt), plan.categories_to_insert)

    # 4. Upsert Masters
    if plan.masters_to_update:
        upd_master_stmt = """
        UPDATE master_ingredients SET
            source_code = :source_code,
            name = :name,
            description = :description,
            category_id = :category_id,
            canonical_unit = :canonical_unit,
            calories = :calories,
            protein_g = :protein_g,
            fat_g = :fat_g,
            carbs_g = :carbs_g,
            sugar_g = :sugar_g,
            sodium_mg = :sodium_mg,
            other_nutrients = CAST(:other_nutrients AS jsonb),
            is_verified = :is_verified
        WHERE id = :id;
        """
        for i in range(0, len(plan.masters_to_update), options.batch_size):
            chunk = plan.masters_to_update[i : i + options.batch_size]
            formatted_chunk = [
                {**m, "canonical_unit": str(m["canonical_unit"].value if hasattr(m["canonical_unit"], "value") else m["canonical_unit"]), "other_nutrients": json.dumps(m["other_nutrients"])}
                for m in chunk
            ]
            await conn.execute(text(upd_master_stmt), formatted_chunk)

    if plan.masters_to_insert:
        ins_master_stmt = """
        INSERT INTO master_ingredients (
            id, source_code, name, description, category_id, canonical_unit,
            calories, protein_g, fat_g, carbs_g, sugar_g, sodium_mg, other_nutrients, is_verified
        ) VALUES (
            :id, :source_code, :name, :description, :category_id, :canonical_unit,
            :calories, :protein_g, :fat_g, :carbs_g, :sugar_g, :sodium_mg, CAST(:other_nutrients AS jsonb), :is_verified
        ) ON CONFLICT (id) DO UPDATE SET
            source_code = EXCLUDED.source_code,
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            category_id = EXCLUDED.category_id,
            canonical_unit = EXCLUDED.canonical_unit,
            calories = EXCLUDED.calories,
            protein_g = EXCLUDED.protein_g,
            fat_g = EXCLUDED.fat_g,
            carbs_g = EXCLUDED.carbs_g,
            sugar_g = EXCLUDED.sugar_g,
            sodium_mg = EXCLUDED.sodium_mg,
            other_nutrients = EXCLUDED.other_nutrients,
            is_verified = EXCLUDED.is_verified;
        """
        for i in range(0, len(plan.masters_to_insert), options.batch_size):
            chunk = plan.masters_to_insert[i : i + options.batch_size]
            formatted_chunk = [
                {**m, "canonical_unit": str(m["canonical_unit"].value if hasattr(m["canonical_unit"], "value") else m["canonical_unit"]), "other_nutrients": json.dumps(m["other_nutrients"])}
                for m in chunk
            ]
            await conn.execute(text(ins_master_stmt), formatted_chunk)

    # 5. Insert aliases
    if plan.aliases_to_insert:
        alias_stmt = """
        INSERT INTO ingredient_aliases (id, master_ingredient_id, alias, normalized_alias)
        VALUES (:id, :master_ingredient_id, :alias, :normalized_alias)
        ON CONFLICT (normalized_alias) DO NOTHING;
        """
        for i in range(0, len(plan.aliases_to_insert), options.batch_size):
            chunk = plan.aliases_to_insert[i : i + options.batch_size]
            await conn.execute(text(alias_stmt), chunk)

    # 6. Upsert Recipes (overwrite bundle columns)
    if plan.recipes_to_upsert:
        recipe_stmt = """
        INSERT INTO recipes (
            id, name, description, instructions, media_url, source_platform, source_url,
            default_servings, estimated_cooking_minutes, estimated_cost, total_calories,
            total_protein_g, total_fat_g, total_carbs_g, total_sugar_g, other_nutrients,
            nutrition_status, tags, ai_features
        ) VALUES (
            :id, :name, :description, CAST(:instructions AS jsonb), :media_url, :source_platform, :source_url,
            :default_servings, :estimated_cooking_minutes, :estimated_cost, :total_calories,
            :total_protein_g, :total_fat_g, :total_carbs_g, :total_sugar_g, CAST(:other_nutrients AS jsonb),
            :nutrition_status, CAST(:tags AS jsonb), CAST(:ai_features AS jsonb)
        ) ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            instructions = EXCLUDED.instructions,
            media_url = EXCLUDED.media_url,
            source_platform = EXCLUDED.source_platform,
            source_url = EXCLUDED.source_url,
            default_servings = EXCLUDED.default_servings,
            estimated_cooking_minutes = EXCLUDED.estimated_cooking_minutes,
            estimated_cost = EXCLUDED.estimated_cost,
            total_calories = EXCLUDED.total_calories,
            total_protein_g = EXCLUDED.total_protein_g,
            total_fat_g = EXCLUDED.total_fat_g,
            total_carbs_g = EXCLUDED.total_carbs_g,
            total_sugar_g = EXCLUDED.total_sugar_g,
            other_nutrients = EXCLUDED.other_nutrients,
            nutrition_status = EXCLUDED.nutrition_status,
            tags = EXCLUDED.tags,
            ai_features = EXCLUDED.ai_features;
        """
        for i in range(0, len(plan.recipes_to_upsert), options.batch_size):
            chunk = plan.recipes_to_upsert[i : i + options.batch_size]
            formatted_chunk = [
                {
                    **r,
                    "instructions": json.dumps(r["instructions"]),
                    "other_nutrients": json.dumps(r["other_nutrients"]),
                    "tags": json.dumps(r["tags"]),
                    "ai_features": json.dumps(r["ai_features"]),
                }
                for r in chunk
            ]
            await conn.execute(text(recipe_stmt), formatted_chunk)

    # 7. Upsert Recipe Ingredients
    if plan.recipe_ingredients_to_upsert:
        ing_stmt = """
        INSERT INTO recipe_ingredients (
            id, recipe_id, master_ingredient_id, required_quantity, unit,
            display_quantity, display_unit, is_optional, preparation_note, ai_attributes
        ) VALUES (
            :id, :recipe_id, :master_ingredient_id, :required_quantity, :unit,
            :display_quantity, :display_unit, :is_optional, :preparation_note, CAST(:ai_attributes AS jsonb)
        ) ON CONFLICT (id) DO UPDATE SET
            recipe_id = EXCLUDED.recipe_id,
            master_ingredient_id = EXCLUDED.master_ingredient_id,
            required_quantity = EXCLUDED.required_quantity,
            unit = EXCLUDED.unit,
            display_quantity = EXCLUDED.display_quantity,
            display_unit = EXCLUDED.display_unit,
            is_optional = EXCLUDED.is_optional,
            preparation_note = EXCLUDED.preparation_note,
            ai_attributes = EXCLUDED.ai_attributes;
        """
        for i in range(0, len(plan.recipe_ingredients_to_upsert), options.batch_size):
            chunk = plan.recipe_ingredients_to_upsert[i : i + options.batch_size]
            formatted_chunk = [
                {
                    **ing,
                    "unit": str(ing["unit"].value if hasattr(ing["unit"], "value") else ing["unit"]),
                    "ai_attributes": json.dumps(ing["ai_attributes"]),
                }
                for ing in chunk
            ]
            await conn.execute(text(ing_stmt), formatted_chunk)

    # 8. Purge unprotected legacy masters
    if plan.unprotected_masters_to_delete:
        del_masters = list(plan.unprotected_masters_to_delete)
        for i in range(0, len(del_masters), options.batch_size):
            chunk = del_masters[i : i + options.batch_size]
            await conn.execute(text("DELETE FROM master_ingredients WHERE id = ANY(:ids);"), {"ids": chunk})

    # 9. Post-Checks inside transaction
    cnt_ai_recipes = int((await conn.execute(text("SELECT count(*) FROM recipes WHERE ai_features <> '{}'::jsonb;"))).scalar() or 0)
    if cnt_ai_recipes != len(plan.recipes_to_upsert):
        raise ValueError(f"Post-check failed: expected {len(plan.recipes_to_upsert)} AI recipes, found {cnt_ai_recipes}")

    cnt_ai_ings = int((await conn.execute(text("SELECT count(*) FROM recipe_ingredients WHERE ai_attributes <> '{}'::jsonb;"))).scalar() or 0)
    if cnt_ai_ings != len(plan.recipe_ingredients_to_upsert):
        raise ValueError(f"Post-check failed: expected {len(plan.recipe_ingredients_to_upsert)} AI ingredients, found {cnt_ai_ings}")

    # Generic FK Orphan Check
    for fk in fks:
        chk_query = f"""
        SELECT count(*)
        FROM {fk.src_table}
        WHERE {fk.src_column} IS NOT NULL
          AND {fk.src_column} NOT IN (SELECT {fk.dst_column} FROM {fk.dst_table});
        """
        orphan_count = int((await conn.execute(text(chk_query))).scalar() or 0)
        if orphan_count > 0:
            raise ValueError(
                f"Post-check failed: FK orphan detected for {fk.constraint_name} "
                f"({fk.src_table}.{fk.src_column} -> {fk.dst_table}.{fk.dst_column}): {orphan_count} rows"
            )

    # Check account rows unchanged
    for acc_tbl in ACCOUNT_TABLES:
        if acc_tbl in plan.preflight_counts:
            post_cnt = int((await conn.execute(text(f"SELECT count(*) FROM {acc_tbl};"))).scalar() or 0)
            pre_cnt = plan.preflight_counts[acc_tbl]
            if post_cnt != pre_cnt:
                raise ValueError(f"Post-check failed: account table {acc_tbl} modified ({pre_cnt} -> {post_cnt})")


async def run_replace_catalog(options: ReplaceOptions) -> ReplaceCatalogPlan:
    """Execute complete catalog replacement pipeline."""
    start_time = time.time()
    db_url = options.database_url or resolve_database_url()
    if not db_url:
        raise ValueError("Database URL is required for catalog replacement.")

    bundle_raw = load_catalog_bundle(options.bundle_dir)
    transformed_data, _ = transform_catalog_bundle(bundle_raw)

    engine = create_async_engine(
        build_async_database_url(db_url),
        connect_args={"statement_cache_size": 0},
        pool_pre_ping=True,
    )

    try:
        async with engine.connect() as conn:
            fks = await discover_foreign_keys(conn)
            plan = await build_replace_plan(conn, transformed_data, fks, options)

            print_plan_summary(plan, options)

            if options.dry_run:
                print("Dry-run mode: plan verified, no database writes executed.")
                return plan

            # Prepare backup data
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_dir = options.backup_dir or Path(f"./backups/catalog-{timestamp}")

            db_rows_to_backup: dict[str, list[dict[str, object]]] = {}
            for tbl, ids in plan.user_rows_to_delete.items():
                if ids:
                    q = text(f"SELECT * FROM {tbl} WHERE id = ANY(:ids);")
                    res = await conn.execute(q, {"ids": ids})
                    db_rows_to_backup[tbl] = [dict(r) for r in res.mappings().all()]

            # The replacement deletes and overwrites rows across the whole catalog, so back up
            # every catalog table in full rather than only the rows the plan names.
            for catalog_table in ("recipes", "recipe_ingredients", "master_ingredients", "ingredient_aliases"):
                res = await conn.execute(text(f"SELECT * FROM {catalog_table};"))
                db_rows_to_backup[catalog_table] = [dict(r) for r in res.mappings().all()]

            write_backup(plan, db_rows_to_backup, backup_dir)
            print(f"Backup written successfully to: {backup_dir.resolve()}")

        # Execute transaction in a dedicated engine.begin() context
        async with engine.begin() as mut_conn:
            await execute_replace_plan(mut_conn, plan, fks, options)

            elapsed = time.time() - start_time
            print(f"Catalog replacement completed successfully in {elapsed:.2f}s.")
            return plan
    finally:
        await engine.dispose()
