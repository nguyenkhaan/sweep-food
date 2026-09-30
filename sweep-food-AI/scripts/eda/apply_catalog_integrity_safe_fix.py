"""USE_7038_CANONICAL: reviewed 72-row / 61-recipe repair; dry-run by default.

The adjacent JSON is a frozen review manifest, never discovered or refreshed at
runtime. Full before records pin IDs, semantics, nutrition and source context.
All inputs must equal their complete reviewed before or computed after state.
Catalog, aliases, processed rows and rollups are planned before any writes.
Canonical composition is also checked before writing for identity/group drift.
--apply writes in that order, rebuilds the untracked embedding cache, exports
canonical CSV/JSON and runs canonical --check. A completed rerun writes nothing.
"""

import argparse
from copy import deepcopy
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from nlp.entity_matcher import (
    DEPRECATED_CATALOG_IDENTITIES, VietnameseIngredientMatcher,
    clean_culinary_query, normalize_vietnamese_text,
)
from nlp.matching_integrity import stage_qwen_update
from scripts.eda.apply_qwen_safe_fix import (
    read_csv, read_json, write_json, clear_row, recompute_recipe_rollups, _apply_rollups,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
from scripts.canonicalize_recipes import compose_reviewed_aliases

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('catalog_integrity_reviewed_state.json')
OUT = ROOT / 'reports/eda/catalog_integrity_fix'
CAT = Path('data/processed/viendinhduong/master_ingredients_nutrition.csv')
ALIASES = CAT.with_name('ingredient_alias_map.json')
DATA = Path('data/processed/recipes')
NUTRIENTS = ('calories', 'protein_g', 'fat_g', 'carbs_g')
CATALOG_PATCHES = {
    '7038': {'name_vi': 'Đuôi lợn'},
    '7041': {'name_vi': 'Gan lợn'},
    '7056': {'name_vi': 'Tim gà', 'name_en': 'Chicken, heart, raw'},
    '20079': {'name_vi': DEPRECATED_CATALOG_IDENTITIES['20079'], 'name_en': ''},
}
ALIAS_PATCHES = {
    'gan heo': '7041', 'gan lợn': '7041', 'lưỡi heo': '7045', 'tim heo': '7057',
    'mỡ gà': None, 'đuôi heo': '7038', 'đuôi lợn': '7038',
    'đuôi heo tươi': '7038', 'đuôi heo đuôi lợn': None,
}
COHORTS = {
    'pork_tail': ('20079', '7038', {'đuôi heo'}, 17),
    'pork_liver': ('7038', '7041', {'gan heo', 'gan lợn'}, 18),
    'pork_tongue': ('7041', '7045', {'lưỡi heo'}, 7),
    'chicken_fat': ('7041', None, {'mỡ gà'}, 9),
    'pork_heart': ('7056', '7057', {'tim heo'}, 19),
    'chicken_heart': ('', '7056', {'tim gà'}, 2),
}
PROBES = {
    'gan heo': '7041', 'gan lợn': '7041', 'lưỡi heo': '7045',
    'tim heo': '7057', 'tim gà': '7056', 'tim gà tươi': '7056', 'mỡ gà': None,
    'đuôi heo': '7038', 'đuôi lợn': '7038', 'đuôi heo tươi': '7038',
    'đuôi lợn tươi': '7038', 'đuôi heo đuôi lợn': '7038',
    'gan bò': '7039', 'gan gà': '7040', 'gan vịt': '7042', 'lưỡi bò': '7044',
    'lưỡi lợn': '7045', 'tim bò': '7055', 'tim lợn': '7057',
    'đuôi bò': '7037', 'đuôi': '7037', 'mỡ heo': '7016', 'mỡ lợn': '7016',
}


class DriftError(ValueError):
    """Reviewed precondition or resulting blast radius no longer holds."""


def require(condition, message):
    if not condition:
        raise DriftError(message)


def logical(row):
    return {k: '' if v is None else str(v) for k, v in row.items()}


def write_csv(path, rows, fieldnames):
    """Preserve the live file's BOM; previous remediations used both encodings."""
    encoding = 'utf-8-sig' if path.read_bytes().startswith(b'\xef\xbb\xbf') else 'utf-8'
    with path.open('w', encoding=encoding, newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def index(rows, key='id'):
    result = {r[key]: r for r in rows}
    require(len(result) == len(rows), f'Duplicate {key}')
    return result


def parity(csv_rows, json_rows):
    a, b = index(csv_rows), index(json_rows)
    require(a.keys() == b.keys(), 'CSV/JSON IDs differ')
    for rid, row in a.items():
        require(logical(row) == logical({k: b[rid][k] for k in row}), f'CSV/JSON drift: {rid}')


def expected_row(reviewed, catalog):
    row = deepcopy(reviewed['before'])
    code = reviewed['target_code']
    if code is None:
        return clear_row(row)
    # Exact/cleaned names take precedence over aliases in the real matcher.
    norm = normalize_vietnamese_text(row['cleaned_name'])
    name = catalog[code]['name_vi']
    exact = norm == normalize_vietnamese_text(name)
    method, confidence = ('EXACT_CATALOG_MATCH', '1.0') if exact else ('PRESET_ALIAS_MATCH', '0.98')
    patch = stage_qwen_update(row, catalog, float(row['estimated_weight_g']), {
        'master_ingredient_code': code, 'master_ingredient_name': name,
        'match_method': method, 'match_confidence': confidence,
    })
    patch.pop('estimated_weight_g')  # Preserve source weight byte-for-byte.
    row.update(patch)
    return row


def nutrient_report(before, after):
    result = {}
    for f in NUTRIENTS:
        def total(rows):
            return sum((Decimal(str(r[f])) for r in rows if r.get(f) not in (None, '')), Decimal(0))
        b, a = total(before), total(after)
        result[f] = {
            'before_known_sum': str(b), 'after_known_sum': str(a), 'known_sum_delta': str(a-b),
            'before_null_count': sum(r.get(f) in (None, '') for r in before),
            'after_null_count': sum(r.get(f) in (None, '') for r in after),
            'value_to_null': sum(x.get(f) not in (None, '') and y.get(f) in (None, '') for x,y in zip(before,after)),
            'zero_to_null': sum(x.get(f) not in (None, '') and Decimal(str(x[f])) == 0 and y.get(f) in (None, '') for x,y in zip(before,after)),
            'null_to_value': sum(x.get(f) in (None, '') and y.get(f) not in (None, '') for x,y in zip(before,after)),
        }
    return result


def embedding_input_digest(catalog):
    texts = [f"{r['name_vi']} ({r['category_vi']})" for r in catalog]
    return hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode('utf-8')).hexdigest()


def verify_canonical(root):
    subprocess.run([sys.executable, 'scripts/canonicalize_recipes.py', '--check'], cwd=root, check=True)
    for name in ('canonical_recipes', 'canonical_recipe_ingredients'):
        parity(read_csv(root/DATA/(name+'.csv')), read_json(root/DATA/(name+'.json')))
    mapping = read_csv(root/DATA/'recipe_canonical_mapping.csv')
    require({r['original_recipe_id']:r['canonical_recipe_id'] for r in mapping} ==
            read_json(root/DATA/'recipe_canonical_mapping.json'), 'Canonical mapping JSON drift')


def plan(root=ROOT):
    review = read_json(REVIEW)
    cat = read_csv(root / CAT)
    require(len(cat) == review['catalog_count'] == 750, 'Catalog row count drift')
    by_code = index(cat, 'code')
    new_cat = deepcopy(cat)
    new_by_code = index(new_cat, 'code')
    for before in review['catalog_before']:
        code = before['code']
        after = dict(before, **CATALOG_PATCHES.get(code, {}))
        require(by_code.get(code) in (before, after), f'Catalog drift: {code}')
        new_by_code[code].update(after)
    aliases = read_json(root / ALIASES)
    new_aliases = dict(aliases)
    for key, before in review['aliases_before'].items():
        after = ALIAS_PATCHES.get(key, before)
        require(aliases.get(key) in (before, after), f'Alias drift: {key}')
        if after is None:
            new_aliases.pop(key, None)
        else:
            new_aliases[key] = after
    require('20079' not in new_aliases.values(), 'Unreviewed alias targets deprecated 20079')
    require('tim gà' not in aliases, 'Unexpected redundant tim gà alias')
    require({k for k in aliases.keys() | new_aliases.keys() if aliases.get(k) != new_aliases.get(k)} <= ALIAS_PATCHES.keys(), 'Unrelated alias change')
    ingredients = read_csv(root / DATA / 'recipe_ingredients.csv')
    ingredients_json = read_json(root / DATA / 'recipe_ingredients.json')
    parity(ingredients, ingredients_json)
    live = index(ingredients)
    pins = {x['before']['id']: x for x in review['rows']}
    require(len(pins) == 72, 'Review manifest row count drift')
    expected = {rid: expected_row(pin, new_by_code) for rid,pin in pins.items()}
    for rid, pin in pins.items():
        require(rid in live and logical(live[rid]) in (logical(pin['before']), logical(expected[rid])), f'Row drift: {rid}')
    for cohort, (old, target, names, count) in COHORTS.items():
        selected = {r['id'] for r in ingredients if r['cleaned_name'] in names}
        pinned = {rid for rid,pin in pins.items() if pin['cohort'] == cohort}
        require(selected == pinned and len(pinned) == count, f'Semantic cohort drift: {cohort}')
        require(all(pins[rid]['before']['master_ingredient_code'] == old and pins[rid]['target_code'] == target for rid in pinned), f'Reviewed outcomes drift: {cohort}')
    require({r['id'] for r in ingredients if r['master_ingredient_code'] in {'7038','7041','7056','20079'}} <= pins.keys(), 'Additional rows on repaired codes')
    recipes_affected = {r['recipe_id'] for r in expected.values()}
    require(len(recipes_affected) == 61, 'Recipe radius drift')
    tail_recipes = {pins[rid]['before']['recipe_id'] for rid in pins if pins[rid]['cohort'] == 'pork_tail'}
    organ_recipes = {pins[rid]['before']['recipe_id'] for rid in pins if pins[rid]['cohort'] != 'pork_tail'}
    require(len(tail_recipes) == 16 and len(organ_recipes) == 45 and not tail_recipes & organ_recipes, 'Cohort recipe overlap drift')
    marker = normalize_vietnamese_text(DEPRECATED_CATALOG_IDENTITIES['20079'])
    queries = set(aliases) | {r['raw_text'] for r in ingredients} | {r['cleaned_name'] for r in ingredients}
    require(not any(marker in (normalize_vietnamese_text(q), clean_culinary_query(q)) for q in queries), 'Deprecation marker collides with live query')
    require(not any(marker == normalize_vietnamese_text(r['name_vi']) for r in new_cat if r['code'] != '20079'), 'Deprecation marker catalog collision')
    def transform(rows):
        return [dict(r, **{k:v for k,v in expected[r['id']].items() if k in NUTRIENTS or k.startswith('master_ingredient_') or k in ('match_method','match_confidence')}) if r['id'] in expected else dict(r) for r in rows]
    new_ing, new_ing_json = transform(ingredients), transform(ingredients_json)
    parity(new_ing, new_ing_json)
    require(not any(r['master_ingredient_code'] == '20079' for r in new_ing), 'Deprecated processed rows remain')
    recipes = read_csv(root / DATA / 'recipes.csv')
    recipes_json = read_json(root / DATA / 'recipes.json')
    parity(recipes, recipes_json)
    new_recipes, new_recipes_json = deepcopy(recipes), deepcopy(recipes_json)
    rollups = recompute_recipe_rollups(new_ing)
    affected_rollups = {k:v for k,v in rollups.items() if k in recipes_affected}
    _apply_rollups(new_recipes, affected_rollups)
    _apply_rollups(new_recipes_json, affected_rollups)
    status = _recompute_status([r for r in new_recipes_json if r['id'] in recipes_affected], new_ing_json)
    parity(new_recipes, new_recipes_json)
    outputs, _ = compose_reviewed_aliases(new_recipes, new_ing, new_cat, read_json(root / DATA / 'recipe_name_alias_decisions.json')['relationships'])
    canonical = {}
    for name in ('canonical_recipes.csv','canonical_recipe_ingredients.csv','recipe_canonical_mapping.csv'):
        old_rows = read_csv(root / DATA / name)
        key = 'original_recipe_id' if name == 'recipe_canonical_mapping.csv' else 'id'
        before, after = index(old_rows, key), index(outputs[name], key)
        require(before.keys() == after.keys(), f'Canonical ID drift: {name}')
        changed = [rid for rid in before if logical(before[rid]) != logical(after[rid])]
        if name == 'recipe_canonical_mapping.csv':
            stable = ('canonical_recipe_id', 'phase1_canonical_recipe_id', 'selected_source_url',
                      'canonical_group_id', 'canonical_dish_name', 'duplicate_group_size')
            require(all(all(logical(before[rid])[f] == logical(after[rid])[f] for f in stable) for rid in before),
                    'Canonical mapping / representative drift')
            affected_groups = {r['canonical_recipe_id'] for rid,r in before.items() if rid in recipes_affected}
            require(all(before[rid]['canonical_recipe_id'] in affected_groups for rid in changed),
                    'Unrelated canonical mapping group changed')
        elif name == 'canonical_recipe_ingredients.csv':
            require(set(changed) <= pins.keys(), 'Unrelated canonical ingredients changed')
        else:
            # Canonical ID is the representative source recipe ID in this dataset.
            require(set(changed) <= recipes_affected, 'Unrelated canonical recipe changed')
        canonical[name] = {'changed_count': len(changed), 'changed_ids': sorted(changed)}
    files = {CAT: new_cat, ALIASES: new_aliases,
             DATA/'recipe_ingredients.csv':new_ing, DATA/'recipe_ingredients.json':new_ing_json,
             DATA/'recipes.csv':new_recipes, DATA/'recipes.json':new_recipes_json}
    before_files = {CAT:cat, ALIASES:aliases, DATA/'recipe_ingredients.csv':ingredients,
                    DATA/'recipe_ingredients.json':ingredients_json, DATA/'recipes.csv':recipes,
                    DATA/'recipes.json':recipes_json}
    changed_now = [rid for rid in pins if logical(live[rid]) != logical(expected[rid])]
    report = dict(policy='USE_7038_CANONICAL', root_cause='Corrupted Vietnamese display identities and duplicate tail extension polluted early alias matching.',
                  rows_repaired=72, rows_pending=len(changed_now), recipes_affected=61,
                  affected_recipe_ids=sorted(recipes_affected), catalog_count=750,
                  catalog_diff={c:{k:{'before':next(r for r in review['catalog_before'] if r['code']==c)[k], 'after':v} for k,v in patch.items()} for c,patch in CATALOG_PATCHES.items()},
                  alias_diff={k:{'before':review['aliases_before'][k], 'after':v} for k,v in ALIAS_PATCHES.items()},
                  recipe_status=status, canonical=canonical, canonical_id_drift=0, representative_drift=0,
                  row_outcomes={rid:dict(cohort=pins[rid]['cohort'],before=pins[rid]['before'],after=expected[rid]) for rid in sorted(pins)},
                  cohorts={}, combined_nutrition=nutrient_report([pins[rid]['before'] for rid in sorted(pins)], [expected[rid] for rid in sorted(pins)]),
                  deprecation=dict(marker=DEPRECATED_CATALOG_IDENTITIES['20079'],row_retained=True,processed_rows=0,alias_targets=0,query_normalization_collisions=0),
                  exclusions=['Other 9 extension duplicate pairs','Other corrupted display-name codes','Tail weight estimation','Tim Heo Xào Măng Tây','Global stale cleaned_name','New catalog identities','Historical/interim data'])
    recipe_before = index(recipes_json)
    recipe_after = index(new_recipes_json)
    report['recipe_outcomes'] = {rid: {'before': recipe_before[rid], 'after': recipe_after[rid]}
                                 for rid in sorted(recipes_affected)}
    report['alias_map_size'] = len(new_aliases)
    for cohort in COHORTS:
        ids = sorted(rid for rid in pins if pins[rid]['cohort']==cohort)
        report['cohorts'][cohort] = dict(row_count=len(ids),recipe_count=len({expected[rid]['recipe_id'] for rid in ids}),row_ids=ids,
                                       nutrition=nutrient_report([pins[rid]['before'] for rid in ids],[expected[rid] for rid in ids]))
    return files, before_files, report


def replay(matcher):
    result = {}
    batch = matcher.match_batch(list(PROBES))
    for (query, code), batched in zip(PROBES.items(), batch):
        single = matcher.match(query)
        for value in (single, batched):
            require((value['matched_item'] or {}).get('code') == code, f'Matcher replay failed: {query}: {value}')
        result[query] = {'code':code,'single_method':single['method'],'batch_method':batched['method']}
    require(all(matcher.catalog[i]['code'] != '20079' for i in matcher.normalized_to_index.values()), 'Deprecated exact surface')
    require(all(matcher.catalog[i]['code'] != '20079' for i in matcher.alias_dict.values()), 'Deprecated alias surface')
    require(all(matcher.catalog[i]['code'] != '20079' for _,_,_,i in matcher.catalog_subphrase_items), 'Deprecated subphrase surface')
    for query in ('pig tail', DEPRECATED_CATALOG_IDENTITIES['20079']):
        for value in (matcher.match(query), matcher.match_batch([query])[0]):
            require((value['matched_item'] or {}).get('code') != '20079', 'Deprecated neural result')
            require(all(c.get('code') != '20079' for c in value['top_candidates']), 'Deprecated neural candidate')
        result[query] = {'code': (value['matched_item'] or {}).get('code'), 'method': value['method'], 'deprecated_candidate': False}
    return result


def write_report(report, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'applied_fix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines = ['# Catalog integrity repair', '', 'Policy: USE_7038_CANONICAL. 72 ingredient rows / 61 source recipes.', '',
             'Catalog nutrition, categories and codes are unchanged. 20079 remains available for historical code resolution but is excluded from all active retrieval surfaces.', '',
             '## Exact catalog changes', '', '| Code | Field | Before | After |', '|---|---|---|---|']
    for code, fields in report['catalog_diff'].items():
        for field, change in fields.items():
            lines.append(f"| {code} | {field} | {change['before']} | {change['after'] or '(blank)'} |")
    lines += ['', '## Exact alias changes', '', '| Alias | Before | After |', '|---|---|---|']
    for alias, change in report['alias_diff'].items():
        lines.append(f"| {alias} | {change['before']} | {change['after'] or 'removed'} |")
    lines += ['', 'The existing đuôi lợn tươi → 7038 alias and all beef-tail aliases are unchanged. No tim gà alias was added.', '',
             '## Processed rows and nutrition', '',
             'Nutrition sums below include known values only; missing values remain null. Exact before/after records for all ingredient rows and 61 named recipes are in [applied_fix.json](applied_fix.json).', '',
             '| Cohort | Rows | Recipes | kcal delta | Protein delta | Fat delta | Carbs known-sum delta |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for name,c in report['cohorts'].items():
        lines.append(f"| {name} | {c['row_count']} | {c['recipe_count']} | " + ' | '.join(c['nutrition'][f]['known_sum_delta'] for f in NUTRIENTS) + ' |')
    lines += ['', '| Cohort | Nutrient | Before known sum | After known sum | Delta | Nulls before → after |',
              '|---|---|---:|---:|---:|---:|']
    nutrients = {name:c['nutrition'] for name,c in report['cohorts'].items()}
    nutrients['combined'] = report['combined_nutrition']
    for cohort, fields in nutrients.items():
        for field, n in fields.items():
            lines.append(f"| {cohort} | {field} | {n['before_known_sum']} | {n['after_known_sum']} | {n['known_sum_delta']} | {n['before_null_count']} → {n['after_null_count']} |")
    lines += ['', 'All 17 tail carbohydrate values changed from real 0.0 to null. Nine chicken-fat rows have null code/name/confidence/nutrition and method UNMATCHED. Source text, parsed fields and weights are unchanged.', '',
              'Recipe status transitions: '+json.dumps(report['recipe_status'],ensure_ascii=False)+'.', '',
              '## Matcher and deprecation', '',
              'The narrow mỡ gà phrase guard prevents unsafe neural fallthrough. Deprecated 20079 is excluded from exact, cleaned-name, alias, subphrase, token-overlap and both neural ranking paths, including candidate lists. The retained display marker does not collide with current normalized raw/cleaned queries or aliases.', '',
              '| Query | Code | Single route | Batch route |', '|---|---|---|---|']
    for query, result in report.get('matcher_replay',{}).items():
        lines.append(f"| {query} | {result.get('code') or 'UNMATCHED'} | {result.get('single_method',result.get('method',''))} | {result.get('batch_method',result.get('method',''))} |")
    lines += ['', 'English pig tail and the marker are neural diagnostic probes: their candidates exclude 20079; no new English tail alias or broader neural correction is part of this repair.', '',
              '## Canonical propagation', '', '| Artifact | Changed logical records |', '|---|---:|']
    for name, values in report['canonical'].items():
        lines.append(f"| {name} | {values['changed_count']} |")
    lines += ['', 'Canonical ID drift = 0; representative drift = 0. Changes remain within the reviewed groups. The 71 canonical ingredients comprise 17 tails + 52 previously matched corruption-scope rows + 2 newly matched chicken hearts. Mapping changes are selection/quality metrics, not membership or representative changes.', '',
              '## Embeddings and validation', '',
              'Embeddings: '+json.dumps(report.get('embeddings',{}),ensure_ascii=False), '',
              'Validation: '+json.dumps({k:v for k,v in report.get('validation',{}).items() if k != 'changed_logical_records'},ensure_ascii=False), '',
              'Tests: '+json.dumps(report.get('tests',{}),ensure_ascii=False), '',
              'Prior-test adjustments: removed the synthetic mỡ gà preservation fixture; updated both historical alias-count checks from 4676 to 4674 and pinned the two removals. Unrelated drift guards remain intact.', '',
              'Excluded: '+ '; '.join(report['exclusions'])+'.', '', 'No commit or push.']
    if 'git' in report:
        lines += ['', '## Git validation and changed files', '',
                  'git diff --check: '+report['git']['diff_check']+'.', '',
                  'Branch: '+report['git']['branch']+'. All changes remain unstaged.', '',
                  '```text', *report['git']['status_short'], '```']
    (out/'applied_fix.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def run(apply=False, root=ROOT, out=OUT):
    files, before_files, report = plan(root)
    if not apply:
        return report
    changed = [p for p in files if (files[p] != before_files[p] if p.suffix == '.json' else [logical(r) for r in files[p]] != [logical(r) for r in before_files[p]])]
    prior = out/'applied_fix.json'
    cache = (root/CAT).with_name('catalog_embeddings_bkai.pt')
    tracked = subprocess.run(['git','ls-files','--',str(cache.relative_to(root))],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
    require(not tracked, 'Embedding cache unexpectedly tracked; review version-control policy')
    if not changed and prior.exists():
        previous = read_json(prior)
        if previous.get('validation',{}).get('complete') and cache.exists():
            require(hashlib.sha256(cache.read_bytes()).hexdigest() == previous['embeddings']['sha256'], 'Embedding cache drift')
            require(embedding_input_digest(files[CAT]) == previous['embeddings']['input_sha256'], 'Embedding catalog-input drift')
            verify_canonical(root)
            return dict(previous,rows_pending=0,idempotent=True)
        # Resume a completed processed write without losing its original before/
        # after canonical radius or recipe status transitions.
        report = dict(previous, rows_pending=0)
    interim_before = {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'data/interim').rglob('*') if p.is_file()}
    # All semantic, parity and canonical checks above have succeeded before writing.
    for path in changed:
        if path.suffix == '.csv':
            write_csv(root/path,files[path],list(files[path][0]))
        else:
            write_json(root/path,files[path])
    report['status'] = 'processed_applied_validation_pending'
    write_report(report,out)
    import torch
    matcher = VietnameseIngredientMatcher(root/CAT)
    cache.unlink(missing_ok=True)
    # Constructor has loaded the corrected catalog; model initialization builds
    # its complete 750-row tensor, including the retained historical row.
    matcher._init_model()
    tensor = torch.load(cache,map_location=matcher.device,weights_only=True)
    require(tensor.shape[0] == len(matcher.catalog) == 750, 'Embedding shape drift')
    require(torch.equal(tensor,matcher.catalog_embeddings), 'Cache differs from generated embeddings')
    digest = hashlib.sha256(cache.read_bytes()).hexdigest()
    matcher.catalog_embeddings = None
    matcher._compute_catalog_embeddings()
    require(torch.equal(tensor,matcher.catalog_embeddings) and hashlib.sha256(cache.read_bytes()).hexdigest()==digest, 'Cache not reusable')
    report['embeddings'] = dict(rebuilt=True,tracked=False,shape=list(tensor.shape),sha256=digest,next_load_equal=True,
        input_sha256=embedding_input_digest(matcher.catalog),
        build_inputs={r['code']:f"{r['name_vi']} ({r['category_vi']})" for r in matcher.catalog if r['code'] in CATALOG_PATCHES})
    report['matcher_replay'] = replay(matcher)
    for command in (['scripts/canonicalize_recipes.py'],['scripts/export_canonical_json.py']):
        subprocess.run([sys.executable,*command],cwd=root,check=True)
    verify_canonical(root)
    require(interim_before == {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'data/interim').rglob('*') if p.is_file()}, 'Historical/interim data changed')
    require(plan(root)[2]['rows_pending']==0, 'Processed repair failed read-back')
    report['status']='applied'
    report['validation'] = dict(complete=True,processed_parity=True,canonical_parity=True,canonical_check=True,canonical_determinism=True,interim_unchanged=True)
    write_report(report,out)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args = parser.parse_args()
    report = run(apply=args.apply)
    print(json.dumps({k:v for k,v in report.items() if k not in ('row_outcomes','recipe_outcomes','affected_recipe_ids','matcher_replay','canonical')},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
