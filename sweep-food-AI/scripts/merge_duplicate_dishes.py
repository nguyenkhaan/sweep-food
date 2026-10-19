"""Merge duplicate canonical recipes linked by spelling variants or dialect clusters.

Pipeline execution order:
    1) scripts/merge_duplicate_dishes.py
    2) scripts/tag_accompaniments.py
    3) scripts/rebuild_recipe_aggregates.py

Some dishes appear more than once in the canonical recipe dataset because their names
differ by:
    (a) an accepted Vietnamese spelling variant (e.g. cuốn/cuộn, hủ/hũ, băm/bằm/bầm), or
    (b) a regional dialect pair sharing the same non-empty dish_cluster_id (e.g.
        ba rọi / ba chỉ, heo / lợn, móng giò / chân giò).

Connected components (via union-find) are formed over recipes linked by either condition.
For each connected group, exactly one canonical recipe is kept, chosen by explicit,
deterministic lexicographic quality criteria. Every other recipe in the
group is removed from the canonical recipe and ingredient datasets, and all rows in
recipe_canonical_mapping are re-pointed to the selected winner recipe.

Selection criteria (lexicographic, first decisive criterion is reported):
    1. valid_match_rate        higher  (rows with master match / total rows)
    2. unmatched_count         lower
    3. fallback_10g_count      lower   (rows with estimated_weight_g == 10)
    4. explicit_quantity_rate  higher  (rows with required_quantity / total rows)
    5. nutrition_anomaly_flag  lower
    6. incomplete_flag         lower
    7. ingredient_rows         higher
    8. valid_source_url        higher
    9. id                      ascending (tie-break)

Files are rewritten at byte/string level (csv module / json with detected line terminators
and original indentation/separators) to preserve untouched rows. The script is idempotent:
after one run, no group has more than one member, and a second run produces byte-identical files.

Report: reports/eda/duplicate_dish_merge.csv (one row per group member, with group_reason).
"""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "data" / "processed" / "recipes"
RECIPES_CSV = RECIPES_DIR / "recipes.csv"
RECIPES_JSON = RECIPES_DIR / "recipes.json"
INGREDIENTS_CSV = RECIPES_DIR / "recipe_ingredients.csv"
INGREDIENTS_JSON = RECIPES_DIR / "recipe_ingredients.json"
MAPPING_CSV = RECIPES_DIR / "recipe_canonical_mapping.csv"
MAPPING_JSON = RECIPES_DIR / "recipe_canonical_mapping.json"
REPORT_CSV = ROOT / "reports" / "eda" / "duplicate_dish_merge.csv"

# Token-level spelling variants of the same word -> one representative form.
SPELLING_VARIANTS = {
    "cuộn": "cuốn",
    "hũ": "hủ",
    "bằm": "băm",
    "bầm": "băm",
}

CRITERIA = [
    # (name, higher_is_better)
    ("valid_match_rate", True),
    ("unmatched_count", False),
    ("fallback_10g_count", False),
    ("explicit_quantity_rate", True),
    ("nutrition_anomaly_flag", False),
    ("incomplete_flag", False),
    ("ingredient_rows", True),
    ("valid_source_url", True),
]

URL_RE = re.compile(r"^https?://\S+$")


def normalize_name(name: str) -> str:
    text = unicodedata.normalize("NFC", name).lower()
    tokens = re.sub(r"\s+", " ", text).strip().split(" ")
    return " ".join(SPELLING_VARIANTS.get(t, t) for t in tokens)


# --------------------------------------------------------------------------
# Byte-preserving readers/writers
# --------------------------------------------------------------------------
def read_csv_rows(path: Path) -> list[list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def safe_write_bytes(path: Path, data: bytes) -> None:
    import time
    for attempt in range(10):
        try:
            path.write_bytes(data)
            return
        except OSError:
            if attempt == 9:
                raise
            time.sleep(0.2)


def write_csv_rows(path: Path, rows: list[list[str]], lineterminator: str) -> None:
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator=lineterminator).writerows(rows)
    safe_write_bytes(path, buf.getvalue().encode("utf-8"))

def detect_lineterminator(path: Path) -> str:
    head = path.read_bytes()[:4096]
    return "\r\n" if b"\r\n" in head else "\n"


def dump_pandas_style_json(records: list[dict], crlf: bool) -> bytes:
    """Same bytes as pandas ``to_json(orient='records', indent=2, force_ascii=False)``."""
    text = json.dumps(records, ensure_ascii=False, indent=2, separators=(",", ":")).replace("/", "\\/")
    if crlf:
        text = text.replace("\n", "\r\n")
    return text.encode("utf-8")


def dump_plain_json(records: list[dict], crlf: bool) -> bytes:
    """Same bytes as ``json.dump(..., ensure_ascii=False, indent=2)`` (recipes.json)."""
    text = json.dumps(records, ensure_ascii=False, indent=2)
    if crlf:
        text = text.replace("\n", "\r\n")
    return text.encode("utf-8")


# --------------------------------------------------------------------------
# Quality metrics
# --------------------------------------------------------------------------
def quality_metrics(recipe: dict[str, str], ing_rows: list[dict[str, str]]) -> dict[str, float]:
    n = len(ing_rows)
    matched = sum(1 for r in ing_rows if r["match_method"] != "UNMATCHED" and r["master_ingredient_code"])
    unmatched = sum(1 for r in ing_rows if r["match_method"] == "UNMATCHED")
    fallback_10 = sum(1 for r in ing_rows if r["estimated_weight_g"] and float(r["estimated_weight_g"]) == 10.0)
    explicit_qty = sum(1 for r in ing_rows if r["required_quantity"].strip())
    return {
        "valid_match_rate": round(matched / n, 6) if n else 0.0,
        "unmatched_count": unmatched,
        "fallback_10g_count": fallback_10,
        "explicit_quantity_rate": round(explicit_qty / n, 6) if n else 0.0,
        "nutrition_anomaly_flag": int(float(recipe["nutrition_anomaly_flag"] or 0)),
        "incomplete_flag": int(float(recipe["incomplete_flag"] or 0)),
        "ingredient_rows": n,
        "valid_source_url": 1 if URL_RE.match(recipe["source_url"] or "") else 0,
    }


def sort_key(metrics: dict[str, float], recipe_id: str) -> tuple:
    key = []
    for name, higher in CRITERIA:
        value = metrics[name]
        key.append(-value if higher else value)
    key.append(recipe_id)
    return tuple(key)


def decisive_criterion(winner: dict, runner_up: dict) -> str:
    for name, _ in CRITERIA:
        if winner["metrics"][name] != runner_up["metrics"][name]:
            return name
    return "recipe_id ascending tie-break"


# --------------------------------------------------------------------------
def main() -> None:
    recipe_rows = read_csv_rows(RECIPES_CSV)
    r_header, r_body = recipe_rows[0], recipe_rows[1:]
    recipes = [dict(zip(r_header, row)) for row in r_body]

    ing_rows = read_csv_rows(INGREDIENTS_CSV)
    i_header, i_body = ing_rows[0], ing_rows[1:]
    rid_idx = i_header.index("recipe_id")
    ings_by_recipe: dict[str, list[dict[str, str]]] = {}
    for row in i_body:
        ings_by_recipe.setdefault(row[rid_idx], []).append(dict(zip(i_header, row)))

    # Connected components over recipes linked by:
    # (a) same spelling-variant-normalized name
    # (b) same non-empty dish_cluster_id
    parent: dict[str, str] = {r["id"]: r["id"] for r in recipes}

    def find(i: str) -> str:
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    def union(i: str, j: str) -> None:
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    # Link (a): spelling variants
    name_to_ids: dict[str, list[str]] = defaultdict(list)
    for r in recipes:
        name_to_ids[normalize_name(r["name"])].append(r["id"])
    for rids in name_to_ids.values():
        for rid in rids[1:]:
            union(rids[0], rid)

    # Link (b): dialect clusters (non-empty dish_cluster_id)
    cluster_to_ids: dict[str, list[str]] = defaultdict(list)
    for r in recipes:
        cid = (r.get("dish_cluster_id") or "").strip()
        if cid:
            cluster_to_ids[cid].append(r["id"])
    for rids in cluster_to_ids.values():
        for rid in rids[1:]:
            union(rids[0], rid)

    # Group recipes by connected component
    components: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in recipes:
        components[find(r["id"])].append(r)

    multi_groups = [g for g in components.values() if len(g) > 1]

    remap: dict[str, str] = {}  # removed recipe id -> selected recipe id
    report: list[dict] = []

    # Sort groups deterministically by min recipe id
    multi_groups.sort(key=lambda g: sorted(m["id"] for m in g)[0])

    for members in multi_groups:
        has_spelling = len({normalize_name(m["name"]) for m in members}) < len(members)
        clusters = {m["dish_cluster_id"] for m in members if (m.get("dish_cluster_id") or "").strip()}
        has_cluster = len(clusters) == 1 and len(members) > 1
        reasons = []
        if has_spelling:
            reasons.append("spelling_variant")
        if has_cluster:
            reasons.append("dialect_cluster")
        group_reason = "|".join(reasons)

        if has_spelling:
            group_key = normalize_name(members[0]["name"])
        else:
            group_key = next(iter(clusters))

        scored = sorted(
            (
                {"recipe": m, "metrics": quality_metrics(m, ings_by_recipe.get(m["id"], []))}
                for m in members
            ),
            key=lambda s: sort_key(s["metrics"], s["recipe"]["id"]),
        )
        winner, runner_up = scored[0], scored[1]
        reason = f"best lexicographic quality; decisive versus runner-up: {decisive_criterion(winner, runner_up)}"
        for rank, s in enumerate(scored, 1):
            selected = rank == 1
            if not selected:
                remap[s["recipe"]["id"]] = winner["recipe"]["id"]
            report.append({
                "group_key": group_key,
                "group_reason": group_reason,
                "recipe_id": s["recipe"]["id"],
                "name": s["recipe"]["name"],
                "source_url": s["recipe"]["source_url"],
                "rank": rank,
                "selected": int(selected),
                "selected_recipe_id": winner["recipe"]["id"],
                **s["metrics"],
                "selection_reason": reason if selected else f"merged into {winner['recipe']['id']}",
            })

    removed = set(remap)

    # recipes.csv / recipes.json
    write_csv_rows(
        RECIPES_CSV,
        [r_header] + [row for row in r_body if row[0] not in removed],
        detect_lineterminator(RECIPES_CSV),
    )
    recipes_raw = RECIPES_JSON.read_bytes()
    recipes_json = json.loads(recipes_raw)
    safe_write_bytes(
        RECIPES_JSON,
        dump_plain_json([r for r in recipes_json if r["id"] not in removed], b"\r\n" in recipes_raw[:4096]),
    )

    # recipe_ingredients.csv / .json
    write_csv_rows(
        INGREDIENTS_CSV,
        [i_header] + [row for row in i_body if row[rid_idx] not in removed],
        detect_lineterminator(INGREDIENTS_CSV),
    )
    ing_raw = INGREDIENTS_JSON.read_bytes()
    ing_json = json.loads(ing_raw)
    safe_write_bytes(
        INGREDIENTS_JSON,
        dump_pandas_style_json([r for r in ing_json if r["recipe_id"] not in removed], b"\r\n" in ing_raw[:4096]),
    )

    # recipe_canonical_mapping.csv / .json: re-point rows of removed recipes
    canonical_name = {}
    map_rows = read_csv_rows(MAPPING_CSV)
    m_header, m_body = map_rows[0], map_rows[1:]
    c_id, c_name = m_header.index("canonical_recipe_id"), m_header.index("canonical_dish_name")
    for row in m_body:
        canonical_name.setdefault(row[c_id], row[c_name])
    for row in m_body:
        target = remap.get(row[c_id])
        if target:
            row[c_id], row[c_name] = target, canonical_name[target]
    write_csv_rows(MAPPING_CSV, [m_header] + m_body, detect_lineterminator(MAPPING_CSV))

    map_raw = MAPPING_JSON.read_bytes()
    map_json = json.loads(map_raw)
    for rec in map_json:
        target = remap.get(rec["canonical_recipe_id"])
        if target:
            rec["canonical_recipe_id"], rec["canonical_dish_name"] = target, canonical_name[target]
    safe_write_bytes(MAPPING_JSON, dump_pandas_style_json(map_json, b"\r\n" in map_raw[:4096]))

    # Report (only written when there is something to report; keeps reruns idempotent)
    if report:
        REPORT_CSV.parent.mkdir(parents=True, exist_ok=True)
        fields = list(report[0].keys())
        buf = io.StringIO(newline="")
        lt = detect_lineterminator(MAPPING_CSV)
        writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=lt)
        writer.writeheader()
        writer.writerows(report)
        safe_write_bytes(REPORT_CSV, buf.getvalue().encode("utf-8"))

    # Validation
    final_recipes = [dict(zip(r_header, row)) for row in read_csv_rows(RECIPES_CSV)[1:]]
    final_ids = {r["id"] for r in final_recipes}
    assert len(final_ids) == len(final_recipes), "duplicate recipe ids"
    final_ing_ids = {row[rid_idx] for row in read_csv_rows(INGREDIENTS_CSV)[1:]}
    assert final_ids == final_ing_ids, "recipes and ingredients reference different recipe ids"
    final_map = read_csv_rows(MAPPING_CSV)[1:]
    assert all(row[c_id] in final_ids for row in final_map), "mapping points to a missing canonical recipe"
    orig_idx = m_header.index("original_recipe_id")
    orig_ids = [row[orig_idx] for row in final_map]
    assert len(orig_ids) == len(set(orig_ids)), "mapping original_recipe_id not unique"
    assert len(final_map) == 4895, f"Expected 4895 mapping rows, got {len(final_map)}"

    # Leftover checks
    leftover_spelling: dict[str, list[str]] = defaultdict(list)
    for r in final_recipes:
        leftover_spelling[normalize_name(r["name"])].append(r["id"])
    assert all(len(v) == 1 for v in leftover_spelling.values()), "spelling-variant duplicates remain"

    leftover_cluster: dict[str, list[str]] = defaultdict(list)
    for r in final_recipes:
        cid = (r.get("dish_cluster_id") or "").strip()
        if cid:
            leftover_cluster[cid].append(r["id"])
    assert all(len(v) == 1 for v in leftover_cluster.values()), "dialect cluster duplicates remain"

    # Print summary and group list
    print("=" * 80)
    print("DUPLICATE DISH MERGE SUMMARY")
    print("=" * 80)
    print(f"groups merged:   {len(multi_groups)}")
    print(f"recipes removed: {len(removed)}")
    print(f"recipes now:     {len(final_recipes)} | mapping rows: {len(final_map)}")
    print("=" * 80)
    for row in report:
        mark = "KEEP" if row["selected"] else "drop"
        print(f"  [{mark:4s}] {row['name']:30s} ({row['recipe_id'][:8]}) [{row['group_reason']:30s}] -> {row['selection_reason']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
