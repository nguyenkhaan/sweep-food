"""Clean up the 40-serving outlier and align detailed restructured recipes with
the deduplicated canonical recipe catalog (5,478 canonical recipes).
"""

from __future__ import annotations

import csv
import json
import os
import shutil
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

CANONICAL_RECIPES_CSV = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.csv"
CANONICAL_RECIPES_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.json"

CANONICAL_INGS_CSV = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.csv"
CANONICAL_INGS_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.json"

CANONICAL_MAPPING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_canonical_mapping.csv"
CANONICAL_MAPPING_JSON = ROOT / "data" / "processed" / "recipes" / "recipe_canonical_mapping.json"
CANONICAL_DETAILED = ROOT / "data" / "processed" / "recipes" / "canonical_recipes_detailed.json"
DETAILED_TARGET = ROOT / "data" / "processed" / "recipes" / "recipes_restructured_detailed.json"
CACHE_JSONL = ROOT / "data" / "interim" / "restructured_recipes_cache.jsonl"


def load_csv(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def write_csv(p, fields, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json_safe(p: Path, data: Any) -> None:
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if p.exists():
        p.unlink()
    os.replace(tmp, p)


def main() -> None:
    # 1. Load canonical recipes and identify 40-serving outliers
    r_fields, can_recs = load_csv(CANONICAL_RECIPES_CSV)
    bad_ids = {
        r["id"] for r in can_recs
        if r.get("default_servings") in ("40", "40.0", 40) or "trân châu đen" in r.get("name", "").lower()
    }
    print(f"[Step 1] Identified 40-serving recipes to remove from canonical: {bad_ids}")

    clean_can_recs = [r for r in can_recs if r["id"] not in bad_ids]
    write_csv(CANONICAL_RECIPES_CSV, r_fields, clean_can_recs)
    write_json_safe(CANONICAL_RECIPES_JSON, clean_can_recs)
    print(f"  canonical_recipes: {len(can_recs):,} -> {len(clean_can_recs):,} recipes.")

    # 2. Clean canonical ingredients
    i_fields, can_ings = load_csv(CANONICAL_INGS_CSV)
    clean_can_ings = [i for i in can_ings if i["recipe_id"] not in bad_ids]
    write_csv(CANONICAL_INGS_CSV, i_fields, clean_can_ings)
    write_json_safe(CANONICAL_INGS_JSON, clean_can_ings)
    print(f"  canonical_recipe_ingredients: {len(can_ings):,} -> {len(clean_can_ings):,} rows.")

    # 2b. Clean / update canonical mapping for eliminated outlier(s)
    m_fields, map_rows = load_csv(CANONICAL_MAPPING_CSV)
    valid_canon_ids = {r["id"] for r in clean_can_recs}
    updated_map = 0
    for m in map_rows:
        orig_id = m.get("original_recipe_id")
        canon_id = m.get("canonical_recipe_id")
        if orig_id in bad_ids or (canon_id and canon_id not in valid_canon_ids):
            m["canonical_recipe_id"] = ""
            m["canonical_dish_name"] = ""
            m["canonical_group_id"] = ""
            m["selected_source_url"] = ""
            m["selection_score"] = ""
            m["selection_reason"] = "eliminated: 40-serving / non-dish outlier"
            m["resolution_status"] = "eliminated_outlier"
            m["duplicate_group_size"] = "0"
            updated_map += 1
    write_csv(CANONICAL_MAPPING_CSV, m_fields, map_rows)
    map_json_data = {r["original_recipe_id"]: r["canonical_recipe_id"] for r in map_rows}
    write_json_safe(CANONICAL_MAPPING_JSON, map_json_data)
    print(f"  recipe_canonical_mapping: updated {updated_map} eliminated outlier rows.")

    # 3. Read cache of all restructured recipes to get rich sensory + steps
    cache_lines = open(CACHE_JSONL, encoding="utf-8").readlines()
    by_url = {}
    for l in cache_lines:
        if not l.strip():
            continue
        obj = json.loads(l)
        url = obj.get("source_url")
        for rec in obj.get("recipes", []):
            if rec.get("default_servings", 0) >= 40 or "trân châu đen" in rec.get("dish_name", "").lower():
                continue
            by_url.setdefault(url, []).append(rec)

    # 4. Align each clean canonical recipe with its best restructured match
    aligned_canonical = []
    missing = []
    for c in clean_can_recs:
        url = c.get("source_url")
        candidates = by_url.get(url, [])
        if not candidates:
            missing.append(c)
            continue
        if len(candidates) == 1:
            best_match = candidates[0]
        else:
            c_name = c.get("name", "").lower()
            best_match = max(
                candidates,
                key=lambda d: SequenceMatcher(None, c_name, d.get("dish_name", "").lower()).ratio()
            )

        merged = {
            "canonical_recipe_id": c["id"],
            "canonical_dish_name": c["name"],
            "dish_name": best_match.get("dish_name") or c["name"],
            "dish_type": best_match.get("dish_type") or c.get("dish_type"),
            "cooking_method": best_match.get("cooking_method") or c.get("cooking_method"),
            "estimated_cooking_minutes": best_match.get("estimated_cooking_minutes") or c.get("estimated_cooking_minutes"),
            "default_servings": best_match.get("default_servings") or c.get("default_servings"),
            "total_calories": c.get("total_calories"),
            "total_protein_g": c.get("total_protein_g"),
            "total_fat_g": c.get("total_fat_g"),
            "total_carbs_g": c.get("total_carbs_g"),
            "source_platform": c.get("source_platform"),
            "source_url": url,
            "sensory_profile": best_match.get("sensory_profile", {}),
            "chef_tips": best_match.get("chef_tips", ""),
            "ingredients": best_match.get("ingredients", []),
            "steps": best_match.get("steps", []),
        }
        aligned_canonical.append(merged)

    if missing:
        raise RuntimeError(f"Missing restructured match for {len(missing)} canonical recipes: {[m['name'] for m in missing[:5]]}")

    # Write both canonical_recipes_detailed.json and recipes_restructured_detailed.json
    write_json_safe(CANONICAL_DETAILED, aligned_canonical)
    write_json_safe(DETAILED_TARGET, aligned_canonical)
    print(f"\n[SUCCESS] Exported {len(aligned_canonical):,} deduplicated canonical detailed recipes to:")
    print(f"  - {CANONICAL_DETAILED.relative_to(ROOT)}")
    print(f"  - {DETAILED_TARGET.relative_to(ROOT)}")

    # 5. Final assertion check
    assert len(aligned_canonical) == len(clean_can_recs) == 5478, f"Count mismatch: {len(aligned_canonical)} vs {len(clean_can_recs)}"
    assert {r["canonical_recipe_id"] for r in aligned_canonical} == {r["id"] for r in clean_can_recs}, "ID mismatch!"
    assert {i["recipe_id"] for i in clean_can_ings} == {r["id"] for r in clean_can_recs}, "Ingredient recipe_id mismatch!"
    valid_canon_ids = {r["id"] for r in clean_can_recs}
    mapping_canon_ids = {r["canonical_recipe_id"] for r in map_rows if r.get("canonical_recipe_id")}
    assert mapping_canon_ids.issubset(valid_canon_ids), f"Mapping references non-existent canonical IDs: {mapping_canon_ids - valid_canon_ids}"
    print("\n[VERIFICATION PASS] 100% ID & referential integrity across all canonical and detailed artifacts!")


if __name__ == "__main__":
    main()
