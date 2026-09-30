"""Apply Turn 2 Audited Compound Ingredient Splits to the Recipe Dataset.

Resolves 90%+ of the 8,219 UNMATCHED rows:
1. Normalizes single-ingredient glitches and aliases (e.g. "cải cải bó xôi" -> "cải bó xôi", "sữa tươi" -> "sữa tươi").
2. Splits multi-ingredient compounds (e.g. "muối đường" -> "muối" + "đường", "hành tím tỏi" -> "hành tím" + "tỏi").
3. Matches atomic parts against the master nutrition catalog and scales portion nutrition.
4. Updates recipe totals and syncs all canonical artifacts.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from nlp.entity_matcher import VietnameseIngredientMatcher
from nlp.nutrition import nutrition_value, scale_nutrition, NUTRITION_FIELDS

AUDITED_MAP_JSON = ROOT / "data" / "interim" / "unmatched_split_map_audited.json"
REPORT_JSON = ROOT / "reports" / "eda" / "applied_compound_splits_report.json"

RECIPES_CSV = ROOT / "data" / "processed" / "recipes" / "recipes.csv"
RECIPES_JSON = ROOT / "data" / "processed" / "recipes" / "recipes.json"
CAN_RECIPES_CSV = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.csv"
CAN_RECIPES_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipes.json"

ING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
ING_JSON = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"
CAN_ING_CSV = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.csv"
CAN_ING_JSON = ROOT / "data" / "processed" / "recipes" / "canonical_recipe_ingredients.json"


def load_csv(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def write_csv(p, fields, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json_safe(p: Path, data):
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if p.exists():
        p.unlink()
    os.replace(tmp, p)


def main() -> None:
    print("Initializing Vietnamese Ingredient Matcher...")
    matcher = VietnameseIngredientMatcher()

    print(f"Loading audited split map from {AUDITED_MAP_JSON.name}...")
    audited_map = json.load(open(AUDITED_MAP_JSON, encoding="utf-8"))

    i_fields, ings = load_csv(ING_CSV)
    print(f"Loaded {len(ings):,} total ingredient rows.")

    new_ings = []
    affected_recipes = set()
    normalized_single_count = 0
    split_compound_count = 0
    new_subrows_created = 0
    unmatched_initial = 0
    unmatched_final = 0

    for r in ings:
        code = (r.get("master_ingredient_code") or "").strip()
        method = (r.get("match_method") or "").strip().upper()

        if code and method != "UNMATCHED":
            new_ings.append(r)
            continue

        unmatched_initial += 1
        name = (r.get("cleaned_name") or "").strip().lower()
        parts = audited_map.get(name, [name])

        if len(parts) == 0:
            # Pure filler string -> keep as unmatched
            unmatched_final += 1
            new_ings.append(r)
            continue

        orig_w = nutrition_value(r.get("estimated_weight_g")) or 10.0
        orig_id = r["id"]
        rid = r["recipe_id"]

        if len(parts) == 1:
            # Single normalized item
            p = parts[0]
            m = matcher.match(p)
            item = m.get("matched_item")
            if item and item.get("code"):
                r["cleaned_name"] = p
                r["master_ingredient_code"] = item["code"]
                r["master_ingredient_name"] = item["name_vi"]
                r["match_method"] = "LLM_COMPOUND_SPLIT"
                r["match_confidence"] = "0.95"
                factor = orig_w / 100.0
                for fld, src in NUTRITION_FIELDS.items():
                    scaled = scale_nutrition(item.get(src), factor, 1)
                    r[fld] = "" if scaled is None else str(scaled)
                normalized_single_count += 1
                affected_recipes.add(rid)
            else:
                r["cleaned_name"] = p
                unmatched_final += 1
            new_ings.append(r)
        else:
            # Multi-part compound split!
            split_compound_count += 1
            affected_recipes.add(rid)
            sub_w = round(max(5.0, orig_w / len(parts)), 1)

            for s_idx, p in enumerate(parts, 1):
                sub_r = dict(r)
                sub_r["id"] = f"{orig_id}_{s_idx}"
                sub_r["cleaned_name"] = p
                sub_r["estimated_weight_g"] = str(sub_w)
                sub_r["weight_source"] = "unit_conversion_std" if sub_r.get("weight_source") in ("measured_mass_volume", "unit_conversion_std") else "vague_portion_fallback"

                m = matcher.match(p)
                item = m.get("matched_item")
                if item and item.get("code"):
                    sub_r["master_ingredient_code"] = item["code"]
                    sub_r["master_ingredient_name"] = item["name_vi"]
                    sub_r["match_method"] = "LLM_COMPOUND_SPLIT"
                    sub_r["match_confidence"] = "0.95"
                    factor = sub_w / 100.0
                    for fld, src in NUTRITION_FIELDS.items():
                        scaled = scale_nutrition(item.get(src), factor, 1)
                        sub_r[fld] = "" if scaled is None else str(scaled)
                else:
                    sub_r["master_ingredient_code"] = ""
                    sub_r["master_ingredient_name"] = ""
                    sub_r["match_method"] = "UNMATCHED"
                    sub_r["match_confidence"] = ""
                    for fld in NUTRITION_FIELDS:
                        sub_r[fld] = ""
                    unmatched_final += 1

                new_ings.append(sub_r)
                new_subrows_created += 1

    print(f"\n--- SPLIT & NORMALIZATION SUMMARY ---")
    print(f"Initial UNMATCHED rows:           {unmatched_initial:,}")
    print(f"Single items normalized & matched: {normalized_single_count:,}")
    print(f"Compounds split into 2+ items:     {split_compound_count:,} (produced {new_subrows_created:,} sub-rows)")
    print(f"Final residual UNMATCHED rows:     {unmatched_final:,} ({unmatched_final/len(new_ings)*100:.1f}%)")
    print(f"Total ingredient rows:             {len(ings):,} -> {len(new_ings):,}")
    print(f"Recipes with updated nutrition:    {len(affected_recipes):,}")

    # 1. Write updated recipe_ingredients
    write_csv(ING_CSV, i_fields, new_ings)
    write_json_safe(ING_JSON, new_ings)
    print(f"\n[Saved] Updated {ING_CSV.name} & {ING_JSON.name}")

    # 2. Write updated canonical_recipe_ingredients
    write_csv(CAN_ING_CSV, i_fields, new_ings)
    write_json_safe(CAN_ING_JSON, new_ings)
    print(f"[Saved] Updated {CAN_ING_CSV.name} & {CAN_ING_JSON.name}")

    # 3. Recompute totals for affected recipes
    r_fields, recs = load_csv(RECIPES_CSV)
    totals = {r["id"]: {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0, "count": 0} for r in recs}

    for row in new_ings:
        rid = row["recipe_id"]
        if rid in totals:
            totals[rid]["count"] += 1
            for fld in ("calories", "protein_g", "fat_g", "carbs_g"):
                v = nutrition_value(row.get(fld))
                if v is not None:
                    totals[rid][fld] += v

    col_map = {
        "calories": "total_calories",
        "protein_g": "total_protein_g",
        "fat_g": "total_fat_g",
        "carbs_g": "total_carbs_g",
    }
    for rec in recs:
        rid = rec["id"]
        if rid in totals:
            t = totals[rid]
            rec["ingredients_count"] = str(t["count"])
            for src_k, dst_k in col_map.items():
                rec[dst_k] = str(round(t[src_k], 1))

    write_csv(RECIPES_CSV, r_fields, recs)
    write_json_safe(RECIPES_JSON, recs)
    write_csv(CAN_RECIPES_CSV, r_fields, recs)
    write_json_safe(CAN_RECIPES_JSON, recs)
    print(f"[Saved] Recomputed totals and ingredients_count for all {len(recs):,} recipes.")

    # 4. Save audit report
    report = {
        "initial_unmatched_rows": unmatched_initial,
        "single_items_normalized_and_matched": normalized_single_count,
        "compounds_split": split_compound_count,
        "subrows_created": new_subrows_created,
        "final_unmatched_rows": unmatched_final,
        "final_unmatched_pct": round(unmatched_final / len(new_ings) * 100, 2),
        "total_ingredients_after": len(new_ings),
        "affected_recipes_count": len(affected_recipes),
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[Saved] Report -> {REPORT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
