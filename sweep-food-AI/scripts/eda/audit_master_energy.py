"""Read-only source trace and historical >30% energy consistency audit.

Run: python -m scripts.eda.audit_master_energy
Only --write-report writes reports/eda/master_energy_audit.json; never datasets.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from crawler.crawl_viendinhduong import parse_food_item
from nlp.master_extensions import EXTENDED_INGREDIENTS
from nlp.nutrition import NUTRITION_FIELDS, nutrition_value
from scripts.eda.validate_missing_nutrition import audit, inconsistent, read_csv

ROOT = Path(__file__).resolve().parents[2]
MASTER = "data/processed/viendinhduong/master_ingredients_nutrition.csv"
INGREDIENTS = "data/processed/recipes/recipe_ingredients.csv"
RAW = "data/raw/viendinhduong/food_nutrition_raw.json"
CORE = tuple(NUTRITION_FIELDS.values())


def build_report():
    """Compare current files to HEAD and trace every flagged master by code."""
    baseline = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    def original(path):
        return subprocess.check_output(['git', 'show', f'{baseline}:{path}'], cwd=ROOT)

    protected = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted((ROOT / 'data').rglob('*')) if p.is_file()}
    masters = read_csv((ROOT / MASTER).read_bytes())
    before = read_csv(original(MASTER))
    ingredients = read_csv((ROOT / INGREDIENTS).read_bytes())
    old_ingredients = read_csv(original(INGREDIENTS))
    raw = json.loads((ROOT / RAW).read_text(encoding='utf-8'))['data']
    traces = []
    for row in masters:
        if not inconsistent(row, CORE):
            continue
        matches = [item for item in raw if str(item['code']) == row['code']]
        extensions = [item for item in EXTENDED_INGREDIENTS if item['code'] == row['code']]
        assert len(matches) + len(extensions) == 1, row['code']
        source = matches[0] if matches else extensions[0]
        parsed = parse_food_item(source) if matches else source
        assert all(nutrition_value(parsed[k]) == nutrition_value(row[k]) for k in CORE)
        e, p, f, c = [float(row[k]) for k in CORE]
        estimate = p * 4 + c * 4 + f * 9
        reason = ('Raw energy is already 1; no repository-backed replacement.' if matches else
                  'Extension literals match; no record-specific source reference or authoritative replacement.')
        if row['code'] == '12079':
            reason += ' Raw protein is already 335 g; decimal/column correction cannot be established.'
        traces.append(dict(
            code=row['code'], name_vi=row['name_vi'],
            processed_core={k: row[k] for k in CORE},
            source_core={k: parsed[k] for k in CORE},
            source_origin=RAW if matches else 'nlp/master_extensions.py',
            source_name=source['name_vi'], raw_nutrients=source.get('nutrition'),
            extension_fiber_g=source.get('fiber_g'),
            estimated_energy=estimate, relative_difference_percent=abs(e-estimate)/e*100,
            diagnosis=reason, safe_automatic_fix=False,
            proposed_action='Leave unchanged; requires source verification.',
            linked_inconsistent_rows=sum(r['master_ingredient_code'] == row['code'] and inconsistent(r)
                                         for r in ingredients)))
    downstream = audit(old_ingredients, ingredients, {r['code']: r for r in masters})
    # Git checkout can convert LF to CRLF; compare every CSV cell to HEAD.
    assert before == masters
    assert old_ingredients == ingredients
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest
               for p, digest in protected.items())
    return dict(
        baseline_commit=baseline,
        formula='abs(E - (P*4 + C*4 + F*9)) / E * 100 > 30; complete core and E > 0',
        master_rows=len(masters),
        complete_core_master_rows=sum(all(nutrition_value(r[k]) is not None for k in CORE) for r in masters),
        zero_energy_complete_master_rows=sum(all(nutrition_value(r[k]) is not None for k in CORE)
                                             and nutrition_value(r['energy_kcal']) == 0 for r in masters),
        master_inconsistent_before=sum(inconsistent(r, CORE) for r in before),
        master_inconsistent_after=len(traces), fixed_records=[], unresolved_records=traces,
        downstream=downstream, rows_resolved_by_master_corrections=0,
        ingredient_rows_excluded_missing_core=sum(any(nutrition_value(r[k]) is None for k in NUTRITION_FIELDS)
                                                 for r in ingredients),
        protected_data_sha256=protected, master_and_ingredient_cells_equal_baseline=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    report = build_report()
    assert report == build_report(), 'Audit must reproduce exactly'
    output = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.write_report:
        (ROOT / 'reports/eda/master_energy_audit.json').write_text(output, encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
