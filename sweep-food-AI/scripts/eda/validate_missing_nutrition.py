"""Restore only processed ingredient nulls and audit against a Git baseline.

Run: python -m scripts.eda.validate_missing_nutrition --write
Without --write, validate the existing outputs. No matching or totals are rerun.
"""

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

from nlp.nutrition import NUTRITION_FIELDS, nutrition_value, restore_missing_nutrition

ROOT = Path(__file__).resolve().parents[2]
CSV = "data/processed/recipes/recipe_ingredients.csv"
JSON = "data/processed/recipes/recipe_ingredients.json"
MASTER = "data/processed/viendinhduong/master_ingredients_nutrition.csv"


def read_csv(payload):
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"), newline="")))


def inconsistent(row, fields=tuple(NUTRITION_FIELDS)):
    values = [nutrition_value(row[f]) for f in fields]
    if any(v is None for v in values) or values[0] <= 0:
        return False
    energy, protein, fat, carbs = values
    # Keep the historical EDA operation order, including floating point boundaries.
    return abs(energy - (protein * 4 + carbs * 4 + fat * 9)) / energy * 100 > 30


def audit(before, after, masters):
    assert len(before) == len(after)
    assert len({r['id'] for r in after}) == len(after)
    fields = {}
    for field, source in NUTRITION_FIELDS.items():
        linked = [i for i, r in enumerate(before) if r['master_ingredient_code'] in masters]
        missing = [i for i in linked if nutrition_value(masters[before[i]['master_ingredient_code']][source]) is None]
        zeros = [i for i in linked if nutrition_value(masters[before[i]['master_ingredient_code']][source]) == 0]
        fields[source] = {
            'master_missing': sum(nutrition_value(m[source]) is None for m in masters.values()),
            'linked_missing_instances': len(missing),
            'zero_before': sum(nutrition_value(before[i][field]) == 0 for i in missing),
            'missing_after': sum(nutrition_value(after[i][field]) is None for i in missing),
            'true_zero_instances': len(zeros),
            'true_zero_before': sum(nutrition_value(before[i][field]) == 0 for i in zeros),
            'true_zero_after': sum(nutrition_value(after[i][field]) == 0 for i in zeros),
        }
        assert fields[source]['missing_after'] == len(missing)
        assert fields[source]['true_zero_before'] == fields[source]['true_zero_after']
    affected = set()
    categories = Counter()
    for old, new in zip(before, after):
        master = masters.get(old['master_ingredient_code'])
        for key in old:
            if old[key] != new[key]:
                assert key in NUTRITION_FIELDS and master is not None, (old['id'], key)
                assert nutrition_value(master[NUTRITION_FIELDS[key]]) is None
                assert nutrition_value(new[key]) is None
                affected.add(old['id'])
        if inconsistent(new):
            if master is None:
                categories['no_master_reference'] += 1
            elif inconsistent(master, tuple(NUTRITION_FIELDS.values())):
                categories['inconsistent_master'] += 1
            else:
                weight = nutrition_value(new['estimated_weight_g'])
                rounding = weight is not None and all(
                    nutrition_value(master[source]) is not None
                    and abs(float(new[field]) - float(master[source]) * weight / 100) <= (1.0 if field == 'calories' else 0.11)
                    for field, source in NUTRITION_FIELDS.items())
                categories['rounding_scaling_tolerance' if rounding else 'remaining_scaling_or_data_mismatch'] += 1
    return {
        'fields': fields,
        'ingredient_rows': len(after),
        'affected_rows': len(affected),
        'affected_recipes': len({r['recipe_id'] for r in before if r['id'] in affected}),
        'unexpected_numeric_or_unrelated_changes': 0,
        'inconsistent_before': sum(inconsistent(r) for r in before),
        'inconsistent_after': sum(inconsistent(r) for r in after),
        'previously_inconsistent_now_missing_macro': sum(inconsistent(a) and any(nutrition_value(b[f]) is None for f in ('protein_g', 'fat_g', 'carbs_g')) for a, b in zip(before, after)),
        'remaining_categories': dict(categories),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--before-ref', default='HEAD')
    args = parser.parse_args()
    baseline = subprocess.check_output(['git', 'rev-parse', args.before_ref], cwd=ROOT).decode().strip()
    def original(path):
        return subprocess.check_output(['git', 'show', f'{baseline}:{path}'], cwd=ROOT)
    protected = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'data').rglob('*') if p.is_file() and p.relative_to(ROOT).as_posix() not in (CSV, JSON)}
    before = read_csv(original(CSV))
    masters_list = read_csv((ROOT / MASTER).read_bytes())
    masters = {r['code']: r for r in masters_list}
    assert len(masters) == len(masters_list)
    # Regenerate from existing processed rows: no upstream matching/weight changes.
    current = read_csv((ROOT / CSV).read_bytes())
    restored = restore_missing_nutrition(current, masters)
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=list(current[0]))
    writer.writeheader()
    writer.writerows(restored)
    csv_bytes = output.getvalue().encode('utf-8-sig')
    json_before = json.loads(original(JSON))
    json_current = json.loads((ROOT / JSON).read_text(encoding='utf-8'))
    json_restored = restore_missing_nutrition(json_current, masters)
    audit(json_before, json_restored, masters)
    json_bytes = json.dumps(json_restored, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8')
    after = read_csv(csv_bytes)
    report = audit(before, after, masters)
    # Existing aggregate policy: missing contributes zero. Assert no sum changes.
    def totals(rows):
        result = Counter()
        for r in rows:
            for f in NUTRITION_FIELDS:
                result[r['recipe_id'], f] += nutrition_value(r[f]) or 0.0
        return result
    assert totals(before) == totals(after)
    for a, b in zip(after, json_restored):
        assert a['id'] == b['id']
        assert all(nutrition_value(a[f]) == nutrition_value(b[f]) for f in NUTRITION_FIELDS)
    recipe_ids = {r['id'] for r in read_csv((ROOT / 'data/processed/recipes/recipes.csv').read_bytes())}
    assert all(r['recipe_id'] in recipe_ids for r in after)
    assert restore_missing_nutrition(restored, masters) == restored
    if args.write:
        (ROOT / CSV).write_bytes(csv_bytes)
        (ROOT / JSON).write_bytes(json_bytes)
    else:
        assert (ROOT / CSV).read_bytes() == csv_bytes
        assert (ROOT / JSON).read_bytes() == json_bytes
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in protected.items())
    report.update(baseline_commit=baseline, protected_data_files_verified=len(protected), legacy_aggregate_sums_unchanged=True,
                  output_sha256={name: hashlib.sha256(payload).hexdigest() for name, payload in [(CSV, csv_bytes), (JSON, json_bytes)]})
    text = json.dumps(report, indent=2) + '\n'
    if args.write:
        (ROOT / 'reports/eda/missing_nutrition_validation.json').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
