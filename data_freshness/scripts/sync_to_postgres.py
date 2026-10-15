"""
scripts/sync_to_postgres.py

DEPRECATED: script này không còn được phép ghi trực tiếp PostgreSQL hoặc chạy DDL.
Hãy dùng `src/backend/scripts/sync_freshcheck_kb.py` với schema do Alembic quản lý.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_PATH = REPO_ROOT / "build/freshcheck_kb.json"

DDL_STATEMENTS = ""


def load_kb_payload() -> dict:
    if not KB_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy artifact {KB_PATH}. Vui lòng chạy 'python scripts/build_kb.py' trước."
        )
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


def generate_sync_plan(kb: dict) -> dict:
    """Tạo kế hoạch đồng bộ SQL."""
    kb_ver = kb["kb_version"]
    archetypes = kb.get("archetypes", {})
    ingredients = kb.get("ingredients", {})
    claims = kb.get("claims", [])
    sources = kb.get("sources", [])

    return {
        "kb_version": kb_ver,
        "total_sources": len(sources),
        "total_claims": len(claims),
        "total_archetypes": len(archetypes),
        "total_ingredients": len(ingredients),
        "sample_ingredient": next(iter(ingredients.values())) if ingredients else None,
    }


def main() -> int:
    """Stop callers before the removed direct-DDL implementation can run."""
    print(
        "Deprecated: use src/backend/scripts/sync_freshcheck_kb.py; "
        "only Alembic manages FreshCheck schema."
    )
    return 2

    parser = argparse.ArgumentParser(description="Đồng bộ FreshCheck KB sang PostgreSQL.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Chỉ in kế hoạch đồng bộ và câu lệnh DDL mà không ghi vào DB.",
    )
    args = parser.parse_args()

    kb = load_kb_payload()
    plan = generate_sync_plan(kb)

    print(f"=== Đồng bộ FreshCheck KB v{plan['kb_version']} ===")
    print(f"  - Số Sources    : {plan['total_sources']}")
    print(f"  - Số Claims     : {plan['total_claims']}")
    print(f"  - Số Archetypes : {plan['total_archetypes']}")
    print(f"  - Số Ingredients: {plan['total_ingredients']}")

    db_url = os.environ.get("DATABASE_URL")
    if not db_url or args.dry_run:
        print("\n[CHẾ ĐỘ DRY-RUN / KIỂM TRA SCHEMA]")
        print("DATABASE_URL chưa được cấu hình hoặc đã chọn --dry-run.")
        print("DDL schema đã được xác thực hợp lệ:")
        for line in DDL_STATEMENTS.strip().splitlines()[:12]:
            print(f"  {line}")
        print("  ... (và các bảng liên kết)")
        print("\n=> Kế hoạch đồng bộ Idempotent: SẴN SÀNG.")
        return

    # Khi có DATABASE_URL (production hoặc staging)
    try:
        import psycopg2
        from psycopg2.extras import Json
    except ImportError:
        print("Cần cài đặt thư viện 'psycopg2' để kết nối PostgreSQL trực tiếp:")
        print("  pip install psycopg2-binary")
        sys.exit(1)

    print(f"\nĐang kết nối tới PostgreSQL...")
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            # 1. Chạy DDL
            cur.execute(DDL_STATEMENTS)

            # 2. Upsert KB Version
            cur.execute(
                """
                INSERT INTO freshcheck_kb_versions (kb_version, generated_at, stats)
                VALUES (%s, %s, %s)
                ON CONFLICT (kb_version) DO UPDATE
                SET generated_at = EXCLUDED.generated_at,
                    synced_at = NOW(),
                    stats = EXCLUDED.stats;
                """,
                (kb["kb_version"], kb["generated_at"], Json(kb["stats"])),
            )

            # 3. Upsert Archetypes
            for aid, a in kb["archetypes"].items():
                cur.execute(
                    """
                    INSERT INTO freshcheck_archetypes
                    (archetype_id, name_vi, applies_to_groups, sensory_tiers, inspection_rubric, preservation_protocols, business_rules, kb_version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (archetype_id) DO UPDATE
                    SET name_vi = EXCLUDED.name_vi,
                        applies_to_groups = EXCLUDED.applies_to_groups,
                        sensory_tiers = EXCLUDED.sensory_tiers,
                        inspection_rubric = EXCLUDED.inspection_rubric,
                        preservation_protocols = EXCLUDED.preservation_protocols,
                        business_rules = EXCLUDED.business_rules,
                        kb_version = EXCLUDED.kb_version;
                    """,
                    (
                        aid,
                        a["name_vi"],
                        Json(a["applies_to_groups"]),
                        Json(a["sensory_tiers"]),
                        Json(a["inspection_rubric"]),
                        Json(a["preservation_protocols"]),
                        Json(a["business_rules"]),
                        kb["kb_version"],
                    ),
                )

            # 4. Upsert Ingredients
            for iid, item in kb["ingredients"].items():
                cur.execute(
                    """
                    INSERT INTO freshcheck_ingredients
                    (ingredient_id, code, names_vi, archetype_id, base_shelf_life_hours, kb_version)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ingredient_id) DO UPDATE
                    SET code = EXCLUDED.code,
                        names_vi = EXCLUDED.names_vi,
                        archetype_id = EXCLUDED.archetype_id,
                        base_shelf_life_hours = EXCLUDED.base_shelf_life_hours,
                        kb_version = EXCLUDED.kb_version;
                    """,
                    (
                        iid,
                        item["code"],
                        Json(item["names_vi"]),
                        item["archetype"],
                        Json(item["base_shelf_life_hours"]),
                        kb["kb_version"],
                    ),
                )

            # 5. Upsert Claims
            for c in kb["claims"]:
                cur.execute(
                    """
                    INSERT INTO freshcheck_claims
                    (claim_id, statement_vi, source_id, locator, conditions, evidence_level, status, extracted_by, reviewed_by, kb_version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (claim_id) DO UPDATE
                    SET statement_vi = EXCLUDED.statement_vi,
                        source_id = EXCLUDED.source_id,
                        locator = EXCLUDED.locator,
                        conditions = EXCLUDED.conditions,
                        evidence_level = EXCLUDED.evidence_level,
                        status = EXCLUDED.status,
                        extracted_by = EXCLUDED.extracted_by,
                        reviewed_by = EXCLUDED.reviewed_by,
                        kb_version = EXCLUDED.kb_version;
                    """,
                    (
                        c["id"],
                        c["statement_vi"],
                        c["source"],
                        c["locator"],
                        Json(c["conditions"]),
                        c["evidence_level"],
                        c["status"],
                        c["extracted_by"],
                        c["reviewed_by"],
                        kb["kb_version"],
                    ),
                )

            conn.commit()
            print(f"\n=> ĐỒNG BỘ THÀNH CÔNG toàn bộ tri thức sang PostgreSQL!")
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
