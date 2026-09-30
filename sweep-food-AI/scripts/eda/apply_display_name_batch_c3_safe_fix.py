"""C3: ID-pinned stored cabbage repair. Dry-run by default; parser deliberately unchanged."""

import argparse
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition
from scripts.eda.apply_display_name_batch_c1_safe_fix import (
    CAT, ALIASES, DATA, NUTRIENTS, require, logical, index, parity, write_csv,
    nutrient_report, nutrition_status, interim_digest, verify_canonical,
    read_csv, read_json, write_json, recompute_recipe_rollups, _apply_rollups,
    _new_totals, _recompute_status, compose_reviewed_aliases,
)

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('display_name_batch_c3_reviewed_state.json')
OUT = ROOT / 'reports/eda/display_name_batch_c3_fix'
BASE_HEAD = 'c026388'
COHORT_IDS = {
    '4013_alias': '0911b36e 0d40e2cf 55177d78 565dbd90 caf2c630 e3ac98c7'.split(),
    '4013_cleaned': '''002efe78 14034367 15bb337c 15ed16f0 1baa3a77 2744ded8
2a1e7f63 2b6b4937 2ca3bf57 2faf1481 3078cfcc 320e38f1 34a58373 364d6c95
37c7a533 3a13daf0 3b097f7b 3ddbf18a 402670b6 42c6149c 44004ef1 4d02257c
4e3cb192 51698227 523f8658 573f2002 5a98b8c7 64294f89 699c9636 6b2e2f16
6c2d1cb0 761aabe4 77b545ff 7a3dcf88 7d84c4b0 7f21b5ef 82c30adc 84d5bac5
943d858f a212f17a a31b1798 a35a2e4e b145e806 b2d1f53a ba354ef1 ba6ee13d
bae8642f cc7e20c3 d01abdc5 d0619f93 d40e2197 d5bb478a d8762468 dbda0b31
dfc53506 e1845f9c e2c390e1 efb93a87 f6cfa765 f854d9ec fa230fe1 fc79ab5a'''.split(),
    '4021_alias': '0f410e8f d0856061 db305e2c'.split(),
    '4021_cleaned': '''011c4996 0a8ab1db 0dda7a70 273e879e 2a23d6fa 4ed3d02b
5948b66a 6b7c177b 76e004fa 7fcd9a01 adb32285 aeb5402e b25d0179 bb19b599
df49260d fc5e0ee6'''.split(),
    'UNMATCHED': '9df17229 d3191592 f421514c 0d39ff61'.split(),
}
KEEP_UNMATCHED = '''db378d63 eee05df7 24f47b37 fe596f36 e8da7381 dc56ccf1
90acbdb8 020f668d eb72aab4 a7875aed 05067998 58276236 8a71fe23'''.split()
REPOINTS = {'cải bào': '4013', 'cải bào mỏng': '4013',
            'cải trắng bào': '4021', 'cải trắng xắt sợi': '4021'}
ADDITIONS = ['bắp cải tròn', 'lá bắp cải', 'rau bắp cải', 'bắp cải tim']
RECOVERY_RAW = dict(zip(COHORT_IDS['UNMATCHED'],
                       ['Bắp cải tròn 80g', '1-2 lá bắp cải', '1/4 Rau bắp cải', '1/4 bắp cải tim']))
BEFORE_POP = {'4010': 14, '4011': 0, '4012': 5, '4013': 122, '4021': 147,
              '20035': 33, '4109': 73, '4115': 1, 'UNMATCHED': 8499}
AFTER_POP = dict(BEFORE_POP, **{'4010': 105, '4013': 54, '4021': 128, 'UNMATCHED': 8495})
BEFORE_NULLS = dict(zip(NUTRIENTS, [8499, 16957, 20262, 17458]))
AFTER_NULLS = dict(zip(NUTRIENTS, [8495, 16953, 20190, 17454]))
DELTAS = {'4013': ['1214.10', '17.09', '7.72', '261.82'],
          '4021': ['124.70', '3.98', '0.22', '24.72'],
          'UNMATCHED': ['100.80', '5.05', '0.25', '19.35'],
          'total': ['1439.60', '26.12', '8.19', '305.89']}
PARSER_FILES = ('nlp/llm_cleaner.py', 'nlp/ingredient_parser.py')
PROBES = {
    'bắp cải': '4010', 'bắp cải trắng': '4010', 'cải bắp': '4010', 'cải bắp trắng': '4010',
    'cải bắp trắng khô': '4012', 'cải khô': '4012', 'dưa cải bắp': '4115',
    'kim chi bắp cải': '20034', 'cải thảo': '4109', 'cải cúc': '4013',
    'tần ô': '4013', 'rau tần ô': '4013', 'củ cải trắng': '4021',
    'bắp cải tím': '20035', 'cải tím': '20035', 'rau cải tím': '20035',
}
ROOT_CAUSE = {
    'function': 'nlp.llm_cleaner.VietnameseLLMIngredientCleaner._parse_single_item',
    'behavior': 'bắp is unit BAP; leading bắp may be stripped; bắp cải is not a protected multiword noun',
    'examples': {'Bắp cải': 'cải', 'Bắp cải trắng': 'cải trắng', 'Bắp cải tím': 'cải tím'},
    'PARSER_BAP_CAI_FIX_NEEDED': True, 'PARSER_DURABILITY_GAP': 82,
    'stored_matcher_replay_expected': 91, 'raw_parser_replay_expected': 9,
    'parser_fix_in_scope': False,
}
DEFERRED_ALIAS_POLICY = {
    'cải': 'Retained -> 4013; 17 remaining users are radish parser defects. Removal yields match() -> 4013 and match_batch() -> 4094. 4094 display-name corruption is out of scope.',
    'cải trắng': 'Retained -> 4021; protects 119 genuine white-radish rows.',
    'curated_divergences': ['a7875aed', '58276236'],
    'keep_unmatched_reasons': 'Brussels sprouts; sprouts; Savoy/crinkled; red/self-substituting; multi-option; dish title; compound/either-or. No broad abstention guard.',
}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def row_digest(rows):
    return digest([logical(r) for r in rows])


def populations(rows):
    counts = Counter(r['master_ingredient_code'] or 'UNMATCHED' for r in rows)
    return {k: counts[k] for k in BEFORE_POP}


def nulls(rows):
    return {f: sum(r[f] in (None, '') for r in rows) for f in NUTRIENTS}


def expected_row(pin, target):
    row = deepcopy(pin['before'])
    row.update(cleaned_name=pin['cleaned_name_after'], master_ingredient_code='4010',
               master_ingredient_name=target['name_vi'], match_method='PRESET_ALIAS_MATCH',
               match_confidence=0.98)
    for field, column in NUTRITION_FIELDS.items():
        row[field] = scale_nutrition(target[column], float(row['estimated_weight_g']) / 100)
    return row


def safety(root, review):
    for name, sha in review['protected_files'].items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, f'Protected file drift: {name}')
    require(interim_digest(root) == review['interim'], 'data/interim drift')


def plan(root=ROOT):
    review = read_json(REVIEW)
    require(review['root_cause'] == ROOT_CAUSE, 'Root-cause record drift')
    safety(root, review)
    cat = read_csv(root / CAT)
    require(len(cat) == 750 and row_digest(cat) == review['catalog_digest'], 'Catalog drift')
    target = index(cat, 'code')['4010']
    require(target['name_vi'] == 'Cải bắp trắng', '4010 identity drift')
    aliases = read_json(root / ALIASES)
    before_aliases = review['aliases_before']
    require(len(before_aliases) == 4680, 'Alias baseline size drift')
    after_aliases = dict(before_aliases)
    for key, code in REPOINTS.items():
        require(before_aliases[key] == code, f'Alias baseline drift: {key}')
        after_aliases[key] = '4010'
    for key in ADDITIONS:
        require(key not in before_aliases, f'Alias was not absent: {key}')
        after_aliases[key] = '4010'
    require(len(after_aliases) == 4684 and aliases in (before_aliases, after_aliases), 'Live alias map drift')
    ingredients = read_csv(root / DATA / 'recipe_ingredients.csv')
    ing_json = read_json(root / DATA / 'recipe_ingredients.json')
    parity(ingredients, ing_json)
    pins = {p['before']['id']: p for p in review['rows']}
    require(len(pins) == 91, 'Manifest must contain exactly 91 full IDs')
    for cohort, ids in COHORT_IDS.items():
        require({p['before']['id'][:8] for p in pins.values() if p['cohort'] == cohort} == set(ids),
                f'Cohort ID drift: {cohort}')
    expected = {}
    for rid, pin in pins.items():
        b = pin['before']
        require(pin['raw_text'] == b['raw_text'] and pin['cleaned_name_before'] == b['cleaned_name'],
                f'Raw/cleaned pin drift: {rid}')
        cohort = pin['cohort']
        source = cohort.split('_')[0]
        require((b['master_ingredient_code'] or 'UNMATCHED') == source, f'Source drift: {rid}')
        wanted = {'4013_cleaned': ('cải', 'bắp cải'), '4021_cleaned': ('cải trắng', 'bắp cải trắng')}
        if cohort in wanted:
            require((b['cleaned_name'], pin['cleaned_name_after']) == wanted[cohort], f'Cleaned repair drift: {rid}')
        else:
            require(pin['cleaned_name_after'] == b['cleaned_name'], f'Unapproved cleaned repair: {rid}')
        if source == 'UNMATCHED':
            require(b['raw_text'] == RECOVERY_RAW[rid[:8]], f'Recovery raw drift: {rid}')
            require(b['cleaned_name'] in ADDITIONS and b['match_method'] == 'UNMATCHED'
                    and all(b[f] in ('', None) for f in (*NUTRIENTS, 'master_ingredient_name', 'match_confidence')),
                    f'Recovery before contract drift: {rid}')
        expected[rid] = expected_row(pin, target)
    before = [pins[r['id']]['before'] if r['id'] in pins else r for r in ingredients]
    after = [expected.get(r['id'], r) for r in ingredients]
    require(row_digest(before) == review['ingredients_before_digest'], 'Unreviewed ingredient or before-record drift')
    require(row_digest(ingredients) in (row_digest(before), row_digest(after)), 'Partial or unexpected stored state')
    require(populations(before) == BEFORE_POP and nulls(before) == BEFORE_NULLS, 'Post-C1 baseline drift')
    require(populations(after) == AFTER_POP and nulls(after) == AFTER_NULLS, 'C3 final population/null drift')
    live = index(ingredients)
    for rid in pins:
        require(logical(live[rid]) in (logical(pins[rid]['before']), logical(expected[rid])), f'Complete before record drift: {rid}')
    changed = {a['id'] for a, b in zip(after, before) if logical(a) != logical(b)}
    require(changed == pins.keys(), 'Changed row set is not exactly the manifest')
    require(sum(a['cleaned_name'] != b['cleaned_name'] for a, b in zip(after, before)) == 78, 'Cleaned radius drift')
    for key in (*REPOINTS, *ADDITIONS):
        users = [r for r in before if r['cleaned_name'] == key]
        require({r['id'] for r in users} == set(review['alias_uses'][key]), f'Alias use drift: {key}')
        require(all(r['id'] in pins for r in users), f'Unreviewed alias use: {key}')
        if key in ADDITIONS:
            require(len(users) == 1, f'New alias is not one-use: {key}')
    for name, count, code in [('cải', 17, '4013'), ('cải trắng', 119, '4021')]:
        users = [r for r in after if r['cleaned_name'] == name]
        require(len(users) == count and all(r['master_ingredient_code'] == code for r in users), f'Broad alias population drift: {name}')
        require({r['id'] for r in users} == set(review['broad_alias_users_after'][name]), f'Broad alias IDs drift: {name}')
        require(after_aliases[name] == code, f'Broad alias repointed: {name}')
    require({r['id'][:8] for r in review['keep_unmatched']} == set(KEEP_UNMATCHED), 'Exclusion ID drift')
    for row in review['keep_unmatched']:
        require(logical(live[row['id']]) == logical(row) and row['match_method'] == 'UNMATCHED', 'KEEP_UNMATCHED drift')
    nutrition = {}
    for group, delta in DELTAS.items():
        ids = sorted(rid for rid, p in pins.items() if group == 'total' or p['cohort'].split('_')[0] == group)
        n = nutrient_report([pins[rid]['before'] for rid in ids], [expected[rid] for rid in ids])
        require([Decimal(n[f]['known_sum_delta']) for f in NUTRIENTS] == list(map(Decimal, delta)), f'Nutrition delta drift: {group}: {n}')
        require(all(n[f]['value_to_null'] == 0 for f in NUTRIENTS), 'Value -> null forbidden')
        nutrition[group] = n
    require(nutrition['4013']['fat_g']['null_to_value'] == 68, '68 fat transitions drift')
    require(all(nutrition['UNMATCHED'][f]['null_to_value'] == 4 for f in NUTRIENTS), 'Recovery null transitions drift')
    recipes = read_csv(root / DATA / 'recipes.csv')
    recipes_json = read_json(root / DATA / 'recipes.json')
    parity(recipes, recipes_json)
    affected = {p['before']['recipe_id'] for p in pins.values()}
    require(len(affected) == 86, 'Recipe radius drift')
    baseline_recipes = [review['recipes_before'][r['id']] if r['id'] in affected else r for r in recipes]
    require(row_digest(baseline_recipes) == review['recipes_before_digest'], 'Unreviewed recipe drift')
    next_recipes, next_json = deepcopy(baseline_recipes), deepcopy(recipes_json)
    rollups = recompute_recipe_rollups(after)
    old_rollups = recompute_recipe_rollups(before)
    require({rid for rid in rollups if _new_totals(rollups[rid]) != _new_totals(old_rollups[rid])} == affected, 'Nutrition rollup radius drift')
    scoped_rollups = {rid: rollups[rid] for rid in affected}
    _apply_rollups(next_recipes, scoped_rollups)
    _apply_rollups(next_json, scoped_rollups)
    _recompute_status([r for r in next_json if r['id'] in affected], after)
    parity(next_recipes, next_json)
    require(row_digest(recipes) in (row_digest(baseline_recipes), row_digest(next_recipes)), 'Recipe before-record drift')
    old_status, new_status = nutrition_status(before, recipes), nutrition_status(after, recipes)
    missing_changes = {rid: {'before': old_status[rid], 'after': new_status[rid]} for rid in affected if old_status[rid] != new_status[rid]}
    require(len(missing_changes) == 4 and all(t['before'][0] == t['after'][0] for t in missing_changes.values()), 'Recipe status drift')
    relationships = read_json(root / DATA / 'recipe_name_alias_decisions.json')['relationships']
    canonical_before, _ = compose_reviewed_aliases(baseline_recipes, before, cat, relationships)
    canonical_after, _ = compose_reviewed_aliases(next_recipes, after, cat, relationships)
    canonical = {}
    for name, count in [('canonical_recipe_ingredients.csv', 88), ('canonical_recipes.csv', 84), ('recipe_canonical_mapping.csv', 67)]:
        key = 'original_recipe_id' if name == 'recipe_canonical_mapping.csv' else 'id'
        b, a = index(canonical_before[name], key), index(canonical_after[name], key)
        current = index(read_csv(root / DATA / name), key)
        require(b.keys() == a.keys() == current.keys(), f'Canonical ID drift: {name}')
        require(row_digest(canonical_before[name]) == review['canonical_before_digests'][name], f'Canonical baseline drift: {name}')
        require(row_digest(list(current.values())) in (row_digest(list(b.values())), row_digest(list(a.values()))), f'Unexpected canonical state: {name}')
        changes = [rid for rid in b if logical(b[rid]) != logical(a[rid])]
        require(len(changes) == count, f'Canonical radius drift: {name}: {len(changes)}')
        require(set(changes) <= (pins.keys() if 'ingredients' in name else affected), f'Unrelated canonical change: {name}')
        if name == 'recipe_canonical_mapping.csv':
            stable = ('canonical_recipe_id', 'phase1_canonical_recipe_id', 'selected_source_url', 'canonical_group_id', 'canonical_dish_name', 'duplicate_group_size', 'resolution_status', 'candidate_rank')
            require(all(all(b[rid][f] == a[rid][f] for f in stable) for rid in b), 'Canonical representative/group/name drift')
            # Two affected source recipes are nonrepresentatives. Their groups
            # are involved, but their canonical content is unchanged.
            require(len({b[rid]['canonical_recipe_id'] for rid in affected}) == 86, 'Canonical source-group radius drift')
            require(len(affected & index(canonical_after['canonical_recipes.csv']).keys()) == 84,
                    'Canonical content-group radius drift')
        canonical[name] = {'changed_count': count, 'changed_ids': changes, 'row_count': len(a)}
    ing_json_after = [dict(r, **{k: expected[r['id']][k] for k in (*NUTRIENTS, 'cleaned_name', 'master_ingredient_code', 'master_ingredient_name', 'match_method', 'match_confidence')}) if r['id'] in expected else r for r in ing_json]
    parity(after, ing_json_after)
    files = {ALIASES: after_aliases, DATA / 'recipe_ingredients.csv': after,
             DATA / 'recipe_ingredients.json': ing_json_after, DATA / 'recipes.csv': next_recipes,
             DATA / 'recipes.json': next_json}
    report = dict(status='dry_run', rows_pending=sum(logical(live[rid]) != logical(expected[rid]) for rid in pins),
                  rows_changed=91, cleaned_name_repairs=78, processed_recipes_touched=86,
                  recipes_with_nutrition_changes=86, missing_nutrition_count_changes=4,
                  nutrition_status_label_transitions=0, populations=AFTER_POP, corpus_nulls=AFTER_NULLS,
                  nutrition=nutrition, canonical=canonical, canonical_groups_touched=84,
                  canonical_source_groups_involved=86,
                  canonical_id_drift=0, representative_drift=0, canonical_group_id_changes=0,
                  canonical_dish_name_changes=0, root_cause=ROOT_CAUSE,
                  PARSER_BAP_CAI_FIX_NEEDED=True, PARSER_DURABILITY_GAP=82,
                  DEFERRED_ALIAS_POLICY=DEFERRED_ALIAS_POLICY, keep_unmatched=review['keep_unmatched'],
                  parser_files_unchanged=True, interim=review['interim'],
                  alias_actions={k: {'before': before_aliases.get(k), 'after': '4010'} for k in (*REPOINTS, *ADDITIONS)},
                  alias_uses=review['alias_uses'], alias_map_size=4684,
                  row_outcomes=[dict(pins[rid], after=expected[rid]) for rid in sorted(pins)],
                  recipe_outcomes=[{'id': rid, 'before': review['recipes_before'][rid], 'after': index(next_recipes)[rid]} for rid in sorted(affected)],
                  missing_count_transitions=missing_changes)
    return files, report


def replay(report, root=ROOT, alias_updates=None):
    from nlp.entity_matcher import VietnameseIngredientMatcher, normalize_vietnamese_text
    from nlp.llm_cleaner import VietnameseLLMIngredientCleaner
    matcher = VietnameseIngredientMatcher(root / CAT)
    if alias_updates is not None:
        code_indexes = {r['code']: i for i, r in enumerate(matcher.catalog)}
        for key in (*REPOINTS, *ADDITIONS):
            matcher.alias_dict[normalize_vietnamese_text(key)] = code_indexes[alias_updates[key]]
    rows = [p['after'] for p in report['row_outcomes']]
    def brief(result):
        return {'master_ingredient_code': (result['matched_item'] or {}).get('code'),
                'match_method': result['method'], 'match_confidence': result['confidence']}
    batch = matcher.match_batch([r['cleaned_name'] for r in rows], raw_contexts=[r['raw_text'] for r in rows])
    stored = []
    for row, result in zip(rows, batch):
        single = matcher.match(row['cleaned_name'], raw_context=row['raw_text'])
        want = {'master_ingredient_code': '4010', 'match_method': 'PRESET_ALIAS_MATCH', 'match_confidence': 0.98}
        require(brief(single) == brief(result) == want, f'Stored replay drift: {row["id"]}: {single}')
        stored.append({'id': row['id'], 'single': brief(single), 'batch': brief(result)})
    cleaner = VietnameseLLMIngredientCleaner()
    examples = {raw: cleaner._parse_single_item(raw)['name'] for raw in ROOT_CAUSE['examples']}
    require(examples == ROOT_CAUSE['examples'], 'Recorded parser root cause changed')
    parsed = [cleaner._parse_single_item(r['raw_text']) for r in rows]
    raw_batch = matcher.match_batch([p['name'] for p in parsed], raw_contexts=[r['raw_text'] for r in rows])
    raw_results = []
    for row, p, result in zip(rows, parsed, raw_batch):
        single = matcher.match(p['name'], raw_context=row['raw_text'])
        raw_results.append({'id': row['id'], 'parsed': p, 'single': brief(single), 'batch': brief(result)})
    counts = {route: sum(r[route]['master_ingredient_code'] == '4010' for r in raw_results) for route in ('single', 'batch')}
    require(counts == {'single': 9, 'batch': 9}, f'Raw durability measurement drift: {counts}')
    probes = {}
    for query, code in PROBES.items():
        single, batch_result = matcher.match(query), matcher.match_batch([query])[0]
        require(brief(single)['master_ingredient_code'] == brief(batch_result)['master_ingredient_code'] == code, f'Boundary drift: {query}')
        probes[query] = {'single': brief(single), 'batch': brief(batch_result)}
    # Removal is simulated only in memory; the broad alias remains in the file.
    aliases = matcher.alias_dict
    saved = aliases.pop('cải')
    try:
        divergence = {'single': brief(matcher.match('cải')), 'batch': brief(matcher.match_batch(['cải'])[0])}
    finally:
        aliases['cải'] = saved
    require(divergence['single']['master_ingredient_code'] == '4013'
            and divergence['batch']['master_ingredient_code'] == '4094', 'Deferred alias fallthrough changed')
    return dict(stored_count=91, raw_count=counts, PARSER_DURABILITY_GAP=82,
                stored=stored, raw=raw_results, parser_examples=examples, probes=probes,
                broad_alias_removal_simulation=divergence)


def write_report(report, out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / 'applied_fix.json', report)
    lines = ['# Batch C3 applied stored-data repair', '',
             '68 rows 4013 -> 4010; 19 rows 4021 -> 4010; 4 UNMATCHED recoveries. Exactly 91 reviewed rows across 86 recipes.',
             '78 cleaned-name repairs: 62 `cải` -> `bắp cải`, 16 `cải trắng` -> `bắp cải trắng`. The other 13 names are preserved.',
             'Four alias repoints and four additions; 4680 -> 4684 keys. All eight aliases are audited by exact corpus use.', '',
             '## Deliberately unresolved parser damage', '',
             '`nlp.llm_cleaner.VietnameseLLMIngredientCleaner._parse_single_item` treats `bắp` as unit BAP and may strip it. `bắp cải` is not protected as a multiword noun.',
             '`Bắp cải` -> `cải`; `Bắp cải trắng` -> `cải trắng`; `Bắp cải tím` -> `cải tím`.',
             '**PARSER_BAP_CAI_FIX_NEEDED = true. PARSER_DURABILITY_GAP = 82.**',
             'Stored-cleaned replay: 91/91 -> 4010, PRESET_ALIAS_MATCH / 0.98 on both routes. Raw -> parser -> matcher: only 9/91 return to 4010. 82 repairs are not durable against fresh raw parsing. No parser-level reproducibility is claimed.',
             'No parser files, CANONICAL_UNIT_MAP, protected_multiword_nouns, or parser architecture changed.', '',
             '## Deferred boundaries', '',
             'DEFERRED_ALIAS_POLICY: `cải` remains -> 4013 for 17 damaged radish rows. Removing it gives match() -> 4013 and match_batch() -> 4094; corrupted 4094 remains out of scope.',
             '`cải trắng` remains -> 4021 for 119 genuine white-radish rows. Red, dried, pickled, kimchi, napa and crown-daisy probes remain unchanged.',
             'KEEP_UNMATCHED: ' + ', '.join(KEEP_UNMATCHED) + '.',
             DEFERRED_ALIAS_POLICY['keep_unmatched_reasons'],
             'a7875aed and 58276236 remain curated divergences: existing `bắp cải` alias may claim them at 0.98.', '',
             '## Measured outcomes', '',
             'Nutrition delta: +1439.60 kcal; +26.12 g protein; +8.19 g fat; +305.89 g carbs. 68 fat null -> measured transitions plus four recoveries in all macros; no value -> null transitions or zero-fill.',
             'Final populations: ' + json.dumps(report['populations']) + '.',
             'Final nulls: ' + json.dumps(report['corpus_nulls']) + '.',
             '86 recipe totals change, four missing counts change, zero nutrition-status labels change.',
             'Canonical: 88 ingredient rows, 84 recipe rows/groups, 67 mapping rows; zero ID, representative, group-ID or dish-name drift; row counts unchanged.',
             'Prior A/B/bamboo/C2/C1 live population/null/alias constants are updated for C3 without changing their own reviewed row sets.', '',
             'Full exact IDs, raw text, complete before/after records, alias uses, cohort nutrition and replay results: [applied_fix.json](applied_fix.json).',
             'Validation: ' + json.dumps(report.get('validation', {})) + '.',
             'Tests: ' + json.dumps(report.get('tests', {})) + '.',
             'No commit or push.']
    (out / 'applied_fix.md').write_text('\n\n'.join(lines) + '\n', encoding='utf-8')


def run(apply=False, root=ROOT, out=OUT):
    files, report = plan(root)
    if not apply:
        return report
    prior = out / 'applied_fix.json'
    if report['rows_pending'] == 0 and prior.exists():
        previous = read_json(prior)
        require(previous.get('validation', {}).get('complete'), 'Incomplete prior application')
        verify_canonical(root)
        return dict(previous, rows_pending=0, idempotent=True)
    require(report['rows_pending'] == 91, 'Apply requires the complete post-C1 baseline')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    require(head == read_json(REVIEW)['head'] and head.startswith(BASE_HEAD), 'HEAD differs from reviewed post-C1 checkpoint')
    report['matcher_replay'] = replay(report, root, files[ALIASES])
    for path, contents in files.items():
        if path.suffix == '.csv':
            write_csv(root / path, contents, list(contents[0]))
        else:
            write_json(root / path, contents)
    require(plan(root)[1]['rows_pending'] == 0, 'Processed read-back failed')
    for script in ('scripts/canonicalize_recipes.py', 'scripts/export_canonical_json.py'):
        subprocess.run([sys.executable, script], cwd=root, check=True)
    verify_canonical(root)
    require(plan(root)[1]['rows_pending'] == 0, 'Final validation failed')
    report.update(status='applied', rows_pending=0,
                  validation=dict(complete=True, processed_parity=True, canonical_parity=True,
                                  canonical_check=True, interim_unchanged=True, parser_files_unchanged=True))
    write_report(report, out)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    result = run(apply=args.apply)
    print(json.dumps({k: result[k] for k in ('status', 'rows_pending', 'populations', 'corpus_nulls')}, indent=2))
