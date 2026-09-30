"""Complete missing master macros (fat_g, carbs_g, protein_g) by kcal
energy-balance derivation.

For a master ingredient with one or more blank macros, the energy not explained
by the KNOWN macros is `residual = energy_kcal - sum(4*protein + 4*carbs +
9*fat over present macros)`. When that residual is ~0 relative to the missing
macro(s), the missing macro(s) are derivably ~0 and are filled with 0.0:

- exactly one macro missing  -> fill 0.0 iff implied grams (residual / kcal_per_g)
  in [-0.5, 0.6];
- two macros missing         -> fill both 0.0 iff residual in [-2.0, 3.0] kcal.

A derivation requires >= 1 macro already present, so the energy is anchored
(this correctly refuses all-blank rows whose energy comes from ethanol, acetic
acid, MSG, or an erroneous ~1 kcal record -- e.g. spirits, vinegar, five-spice
powder, stock -- which are left missing and flagged).

Example: cooking oil (fat 99.7 g, energy 897) -> residual -0.3 kcal -> protein
and carbs filled 0.0. Filling with 0.0 leaves every recipe total numerically
unchanged; only completeness improves. Idempotent. Every change is recorded in
reports/eda/macro_energy_balance_completion.json and, with a citation, in the
sanctioned master_nutrition_overrides.json.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "processed" / "viendinhduong" / "master_ingredients_nutrition.csv"
OVERRIDES = ROOT / "data" / "processed" / "viendinhduong" / "master_nutrition_overrides.json"
ING_CSV = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.csv"
ING_JSON = ROOT / "data" / "processed" / "recipes" / "recipe_ingredients.json"
REPORT = ROOT / "reports" / "eda" / "macro_energy_balance_completion.json"

MACROS = ("protein_g", "carbs_g", "fat_g")
KCAL = {"protein_g": 4.0, "carbs_g": 4.0, "fat_g": 9.0}
ONE_MISSING_G = 0.6      # implied grams tolerance when a single macro is missing
MULTI_MISSING_KCAL = 3.0  # residual kcal tolerance when two macros are missing


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def derive_zeros(m: dict) -> list[str] | None:
    """Return the list of missing macro fields to set to 0.0, or None."""
    e = num(m.get("energy_kcal"))
    if e is None or e == 0:
        return None
    present = {f: num(m.get(f)) for f in MACROS if num(m.get(f)) is not None}
    missing = [f for f in MACROS if num(m.get(f)) is None]
    if not missing or not present:  # need an anchor macro
        return None
    residual = e - sum(KCAL[f] * g for f, g in present.items())
    if len(missing) == 1:
        implied = residual / KCAL[missing[0]]
        return missing if -0.5 <= implied <= ONE_MISSING_G else None
    if -2.0 <= residual <= MULTI_MISSING_KCAL:  # two missing, energy explained by the anchor
        return missing
    return None


def main() -> None:
    with open(MASTER, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        m_fields = reader.fieldnames
        masters = list(reader)

    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    filled_codes = {f: set() for f in MACROS}
    excluded = []

    for m in masters:
        fields = derive_zeros(m)
        if not fields:
            if any(num(m.get(f)) is None for f in MACROS):
                miss = [f for f in MACROS if num(m.get(f)) is None]
                excluded.append({"code": m["code"], "name_vi": m.get("name_vi", ""),
                                 "missing": miss, "energy_kcal": m.get("energy_kcal", "")})
            continue
        for f in fields:
            m[f] = "0.0"
            filled_codes[f].add(m["code"])
        ov = overrides.get(m["code"], {"name_vi": m.get("name_vi", "")})
        for f in fields:
            ov[f] = "0.0"
        ov["citation"] = (
            "Derived by kcal energy balance: energy_kcal is fully explained by the "
            "present macro(s), so the missing macro(s) are ~0 g/100g."
        )
        ov["reason"] = "Blank macro(s) completed as 0.0 for a composition established by macro/energy balance."
        overrides[m["code"]] = ov

    with open(MASTER, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=m_fields)
        w.writeheader(); w.writerows(masters)
    OVERRIDES.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")

    # propagate to matched ingredient rows: master macro 0 -> row macro 0.0 at any weight
    with open(ING_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        i_fields = reader.fieldnames
        ings = list(reader)
    rows_filled = {f: 0 for f in MACROS}
    for r in ings:
        code = r.get("master_ingredient_code")
        if not code:
            continue
        for f in MACROS:
            if code in filled_codes[f] and not (r.get(f) or "").strip():
                r[f] = "0.0"
                rows_filled[f] += 1
    with open(ING_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=i_fields)
        w.writeheader(); w.writerows(ings)

    json_rows = json.loads(ING_JSON.read_text(encoding="utf-8"))
    row_by_id = {r["id"]: r for r in ings}
    for jr in json_rows:
        src = row_by_id.get(jr.get("id"))
        if not src:
            continue
        for f in MACROS:
            if jr.get(f) in (None, "", "nan") and (src.get(f) or "").strip() == "0.0":
                jr[f] = 0.0
    ING_JSON.write_text(json.dumps(json_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "method": "kcal energy balance anchored by >=1 present macro; fill missing macro(s) 0.0 when energy is fully explained",
        "masters_completed": {f: len(filled_codes[f]) for f in MACROS},
        "ingredient_rows_filled": rows_filled,
        "masters_left_incomplete": len(excluded),
        "excluded": excluded,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in MACROS:
        print(f"{f}: completed {len(filled_codes[f])} masters -> {rows_filled[f]} rows")
    print(f"left incomplete (flagged): {len(excluded)} masters")
    print(f"Report -> {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
