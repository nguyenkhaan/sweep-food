"""DISPLAY_NAME_BATCH_A: reviewed 1,188-row / 1,104-recipe repair; dry-run by default.

Four catalog rows carry a Vietnamese display name belonging to a different food,
so early alias and exact matching resolved 1,176 rows onto the wrong identity.
name_vi is repaired first (name_en, category, code and nutrition are untouched),
then the displaced aliases are repointed onto the codes whose English identity
they always meant, then the pinned rows are moved.

The adjacent JSON is a frozen review manifest, never discovered or refreshed at
runtime: it carries the complete before record of every one of the 1,188 rows,
its reviewed cohort and its reviewed target. Rows are never selected by current
code alone -- the 4073/4055 cohorts split by semantics, not by source code, and
each row must equal its reviewed before or its computed after state.

Coriander seed/powder has no catalog identity at all, so its two aliases are
removed and the four coded rows are cleared; the matcher guard added alongside
this fix is what makes that durable (see nlp.entity_matcher).

Catalog, aliases, processed rows and rollups are planned before any writes, and
the resulting populations, nutrition delta, null transitions and canonical
radius are all checked against the reviewed figures first. --apply writes in
that order, rebuilds the untracked embedding cache, exports canonical CSV/JSON
and runs canonical --check. A completed rerun writes nothing.
"""

import argparse
from copy import deepcopy
import csv
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

from nlp.entity_matcher import (
    CORIANDER_SEED_POWDER_GUARD_REASON, VietnameseIngredientMatcher,
    is_coriander_seed_powder_text, normalize_vietnamese_text,
)
from nlp.matching_integrity import stage_qwen_update
from scripts.eda.apply_qwen_safe_fix import (
    read_csv, read_json, write_json, clear_row, recompute_recipe_rollups, _apply_rollups, _new_totals,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
from scripts.canonicalize_recipes import compose_reviewed_aliases

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('display_name_batch_a_reviewed_state.json')
OUT = ROOT / 'reports/eda/display_name_batch_a_fix'
CAT = Path('data/processed/viendinhduong/master_ingredients_nutrition.csv')
ALIASES = CAT.with_name('ingredient_alias_map.json')
DATA = Path('data/processed/recipes')
NUTRIENTS = ('calories', 'protein_g', 'fat_g', 'carbs_g')

# name_vi only. Each replacement is the identity the row's own name_en already
# asserts: 4073 Amaranth sp. Red, 4055 Balsam-pear/Bitter gourd, 5047 Tangerine,
# 8050 Shrimp fresh water tiny DRIED (8052 is the raw one and keeps "Tôm đồng").
CATALOG_PATCHES = {
    '4073': {'name_vi': 'Rau giền đỏ'},
    '4055': {'name_vi': 'Mướp đắng'},
    '5047': {'name_vi': 'Quít'},
    '8050': {'name_vi': 'Tép khô'},
}
CORIANDER_LEAF_ALIASES = (
    'ngò', 'ngò ri', 'ngò rí', 'ngò rí cắt nhỏ', 'ngò rí rau nêm',
    'ngò rí rau nêm cắt nhỏ', 'rau nêm ngò', 'rau nêm ngò rí',
    'rau nêm ngò rí cắt nhỏ', 'vài cọng ngò rí', 'vài nhánh ngò rí', 'ăn kèm ngò rí',
    # Displaced onto 4055 rather than 4073, same coriander-leaf identity.
    'rễ ngò', 'gốc ngò rí', 'ngò rí cắt nhuyễn',
)
CULANTRO_ALIASES = (
    'mùi tàu', 'ngò gai', 'ngò gai cắt nhỏ', 'ngò gai cắt nhỏ lá', 'ngò gai lá',
    'lá ngò gai', 'lá ngò gai lá', 'rau nêm ngò gai', 'rau nêm ngò gai cắt nhỏ',
    'vài nhánh ngò gai', 'ăn kèm ngò gai',
)
QUAT_TAC_ALIASES = (
    'quất', 'tắc', 'quả tắc', 'quả quất', 'trái tắc', 'nước cốt tắc',
    'tắc cắt lát', 'tắc tươi', 'tắc 1',
)
TOM_DAT_ALIASES = ('tôm đất', 'tôm sông', 'tôm đất tươi', 'tôm đất xay')
ALIAS_PATCHES = {
    **{k: '4081' for k in CORIANDER_LEAF_ALIASES},
    **{k: '4082' for k in CULANTRO_ALIASES},
    **{k: '5046' for k in QUAT_TAC_ALIASES},
    **{k: '8052' for k in TOM_DAT_ALIASES},
    'tép đồng': '8049',          # tiny freshwater shrimp, fresh -> Tép gạo.
    'bột rau mùi': None,         # No coriander seed/powder identity exists.
    'hạt rau mùi': None,
}
# Reviewed raw aliases that were always correct against name_en and stay put.
ALIAS_KEEPS = {
    'rau giền đỏ tươi': '4073', 'mướp đắng tươi': '4055',
    'quít tươi': '5047', 'tép khô sống': '8050',
}
# cohort -> (source code, target code, reviewed row count)
COHORTS = {
    'coriander_leaf_4073_to_4081': ('4073', '4081', 785),
    'culantro_4073_to_4082': ('4073', '4082', 43),
    'parsley_4073_to_20036': ('4073', '20036', 2),
    'coriander_leaf_4055_to_4081': ('4055', '4081', 21),
    'culantro_4055_to_4082': ('4055', '4082', 215),
    'quat_tac_5047_to_5046': ('5047', '5046', 76),
    'tom_dat_8050_to_8052': ('8050', '8052', 33),
    'seed_powder_to_unmatched': (None, None, 4),
    'bitter_gourd_4050_to_4055': ('4050', '4055', 1),
    'tep_kho_5029_to_8050': ('5029', '8050', 8),
}
SEED_POWDER_ROW_IDS = (
    '56552972-650b-47f3-9523-b2fd85c54abe', '698905a2-6e8f-4dd1-83dc-b484930a45f3',
    '981b791a-b4c1-48e0-8535-14900e11b6d8', '0cafb8e3-39d6-4067-84e1-ea7f09c1ea91',
)
BITTER_GOURD_ROW_ID = 'd6f83055-4f09-4e24-8b28-b5e99bab7a52'
# 4050/4055/UNMATCHED were superseded by DISPLAY_NAME_BATCH_B, which repointed the
# khổ qua aliases onto 4055, moved the 56 khổ qua rows there and recovered one
# UNMATCHED row onto 4050. Everything else is still Batch A's own measured radius.
# C3 repaired parser-damaged white-cabbage rows; own reviewed row sets remain unchanged.
EXPECTED_POPULATIONS = {
    '4073': 0, '4055': 57, '5047': 0, '8050': 8, '4081': 904, '4082': 265,
    # UNMATCHED was superseded again by DISPLAY_NAME_BATCH_C1, which cleared 35
    # rows (27 spinach, 4 kale, 3 collision, 1 dried salted napa) and recovered 5
    # stored-UNMATCHED mustard-green rows: 8469 + 35 - 5 = 8499. Batch A's own
    # 1188 rows are unaffected and none of its codes moved.
    '5046': 80, '8052': 33, '20036': 48, '5029': 2, '4050': 62, 'UNMATCHED': 8495,
}
EXPECTED_NUTRITION_DELTA = {
    'calories': '-16063.0', 'protein_g': '-1723.8', 'fat_g': '115.1', 'carbs_g': '-2510.6',
}
EXPECTED_NULL_TRANSITIONS = {
    'calories': (0, 4), 'protein_g': (0, 4), 'fat_g': (321, 81), 'carbs_g': (0, 37),
}
# Also shifted by Batch B's single UNMATCHED -> 4050 recovery (fat stays null:
# neither 4050 nor 4055 carries a fat value).
# fat_g moved 20239 -> 20219 when BAMBOO_SHOOT_ALIAS_FIX repointed `măng khô` off
# 4048 (no fat value) onto 4051 (2.1 g/100 g). Batch A's own 1188 rows are unaffected.
# UNMATCHED and the corpus null counts were superseded by DISPLAY_NAME_BATCH_C2,
# which cleared 6 multi-identity cabbage/celery rows to UNMATCHED and recovered 2
# stored-UNMATCHED white-cabbage rows: 8465 - 2 + 6 = 8469, and the same net +4 on
# each nutrient's null count. Batch A's own 1188 rows are unaffected.
# Superseded once more by DISPLAY_NAME_BATCH_C1: 35 clears minus 5 recoveries is a
# net +30 on every nutrient, and fat_g gains a further 9 because the eight
# fresh-napa rows (4109) and the one salted-napa row (4115) move onto catalog
# identities that publish no fat_g value at all. Batch A's own rows are unaffected.
EXPECTED_CORPUS_NULLS = {
    'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454,
}
EXPECTED_ROWS = 1188
EXPECTED_RECIPES = 1104
EXPECTED_CANONICAL = {'canonical_recipe_ingredients.csv': 1146, 'canonical_recipes.csv': 1065}
STATUS_TRANSITION_RECIPE = '63d790f2-b87b-40b1-8794-60923b9edd12'
# Repaired identities, the reviewed alias repoints, and the sibling identities
# that must not move. None means the reviewed verdict is UNMATCHED.
PROBES = {
    'rau giền đỏ': '4073', 'mướp đắng': '4055', 'quít': '5047', 'tép khô': '8050',
    'rau giền đỏ tươi': '4073', 'mướp đắng tươi': '4055', 'quít tươi': '5047',
    'tép khô sống': '8050',
    'ngò rí': '4081', 'ngò': '4081', 'rau nêm ngò rí': '4081', 'rễ ngò': '4081',
    'gốc ngò rí': '4081', 'ngò rí cắt nhuyễn': '4081', 'rau mùi': '4081',
    'rễ và gốc rau mùi': '4081', 'rau mùi thái nhỏ': '4081',
    'ngò gai': '4082', 'mùi tàu': '4082', 'lá ngò gai': '4082', 'rau mùi tàu': '4082',
    'ngò tây': '20036', 'mùi tây': '20036', 'parsley': '20036',
    'tắc': '5046', 'quất': '5046', 'nước cốt tắc': '5046', 'quất chín': '5046',
    'tôm đất': '8052', 'tôm sông': '8052', 'tôm đồng': '8052', 'tép đồng': '8049',
    'tép gạo': '8049', 'tôm biển': '8051', 'tôm khô': '8053',
    'hạt rau mùi': None, 'bột rau mùi': None, 'bột và hạt rau mùi corriander': None,
    'hạt ngò': None, 'bột hạt ngò': None, 'hạt mùi': None, 'bột ngò ta': None,
    'coriander seeds': None, 'coriander powder': None,
    'rau giền cơm': '4072', 'rau giền trắng': '4074', 'khổ qua': '4055',  # 4050 until Batch B
    'mít khô': '5029', 'măng tre': '4053',
}
# Deliberately unchanged by this batch (reviewed deferrals). `mướp đắng` and
# `khổ qua` were deferred here on 4050 and have since been repointed onto 4055 by
# DISPLAY_NAME_BATCH_B, so they moved to BATCH_B_ALIASES_ON_REPAIRED_CODES below.
UNTOUCHED_ALIASES = {'khô': '5029', 'tôm đồng': '8052', 'tôm đồng tươi': '8052',
                     'tép gạo': '8049'}
# Batch B's reviewed bitter-gourd repoints. They sit on 4055 -- a code Batch A
# repaired -- which is correct: 4055's name_en was always Balsam-pear/Bitter
# gourd. They are listed so the "no alias still carries a displaced meaning"
# check below stays a real check rather than being widened to all of 4055.
BATCH_B_ALIASES_ON_REPAIRED_CODES = {
    'khổ qua': '4055', 'khổ qua bào': '4055', 'trái khổ qua': '4055',
    'quả mướp đắng': '4055', 'ăn kèm khổ qua': '4055', 'mướp đắng': '4055',
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
    """Row-level identity repair: the existing match provenance is preserved.

    match_method/match_confidence are NOT re-derived. This batch corrects which
    catalog identity a reviewed link points at; it does not re-run the matcher
    per row, and asserting PRESET_ALIAS_MATCH for a Qwen-extracted multi-
    ingredient line would claim a route that row never took.
    """
    row = deepcopy(reviewed['before'])
    code = reviewed['target_code']
    if code is None:
        return clear_row(row)
    patch = stage_qwen_update(row, catalog, float(row['estimated_weight_g']), {
        'master_ingredient_code': code, 'master_ingredient_name': catalog[code]['name_vi'],
        'match_method': row['match_method'], 'match_confidence': row['match_confidence'],
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
            'null_to_value': sum(x.get(f) in (None, '') and y.get(f) not in (None, '') for x,y in zip(before,after)),
        }
    return result


def nutrition_status(ingredient_rows, recipe_rows):
    """Recipe nutrition label and missing count, using the project's own rule.

    Computed from ingredient rows alone rather than read back from the recipe
    records, so the reviewed transition is measured against the manifest's
    before state on a first apply and on an idempotent replay alike.
    """
    counts, missing = {}, {}
    for row in ingredient_rows:
        rid = row.get('recipe_id')
        if not rid:
            continue
        counts[rid] = counts.get(rid, 0) + 1
        if row.get('calories') in (None, ''):
            missing[rid] = missing.get(rid, 0) + 1
    result = {}
    for record in recipe_rows:
        rid = record['id']
        total = counts.get(rid) or int(record.get('ingredients_count') or 1)
        absent = missing.get(rid, 0)
        label = 'COMPLETE' if absent == 0 else ('PARTIAL' if absent / max(total, 1) < 0.3 else 'INCOMPLETE')
        result[rid] = (label, absent)
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
        after = dict(before, **CATALOG_PATCHES[code])
        require(by_code.get(code) in (before, after), f'Catalog drift: {code}')
        require({k: v for k, v in before.items() if k != 'name_vi'} ==
                {k: v for k, v in after.items() if k != 'name_vi'}, f'Non-name catalog change: {code}')
        new_by_code[code].update(after)
    # Each repaired name must be unique, and no PRE-EXISTING duplicate pair may
    # grow. Repairing 8050 also resolves the 8050/8052 "Tôm đồng" collision; the
    # three unrelated pairs below are reviewed deferrals, not Batch A scope.
    def duplicates(rows):
        names = [normalize_vietnamese_text(r['name_vi']) for r in rows]
        return {n for n in names if names.count(n) > 1}
    before_dups, after_dups = duplicates(cat), duplicates(new_cat)
    require(after_dups <= before_dups, f'New duplicate catalog name: {after_dups - before_dups}')
    # `cần tây` left this set in DISPLAY_NAME_BATCH_C2, which repaired 4010 from the
    # duplicated celery name to `Cải bắp trắng`. The invariant is kept, not weakened:
    # the remaining two collisions are still deferred and still asserted exactly.
    require(after_dups == {'nấm kim châm', 'thịt trâu, đùi'}, f'Deferred duplicate drift: {after_dups}')
    require(not any(normalize_vietnamese_text(p['name_vi']) in after_dups for p in CATALOG_PATCHES.values()),
            'Repaired catalog name collides')

    aliases = read_json(root / ALIASES)
    new_aliases = dict(aliases)
    for key, before in review['aliases_before'].items():
        after = ALIAS_PATCHES.get(key, before)
        require(aliases.get(key) in (before, after), f'Alias drift: {key}')
        if after is None:
            new_aliases.pop(key, None)
        else:
            new_aliases[key] = after
    for key, code in ALIAS_KEEPS.items():
        require(review['aliases_before'][key] == code and new_aliases[key] == code, f'Reviewed alias keep drift: {key}')
    for key, code in UNTOUCHED_ALIASES.items():
        require(aliases.get(key) == code and new_aliases.get(key) == code, f'Deferred alias changed: {key}')
    require({k for k in aliases.keys() | new_aliases.keys() if aliases.get(k) != new_aliases.get(k)} <= ALIAS_PATCHES.keys(), 'Unrelated alias change')
    reviewed_on_patched = set(ALIAS_KEEPS) | set(BATCH_B_ALIASES_ON_REPAIRED_CODES)
    require(not any(v in CATALOG_PATCHES and k not in reviewed_on_patched for k, v in new_aliases.items()),
            'Alias still targets a repaired display identity')
    for key, code in BATCH_B_ALIASES_ON_REPAIRED_CODES.items():
        require(new_aliases.get(key) == code, f'Batch B alias repoint drifted: {key}')
    require(not any(is_coriander_seed_powder_text(k) for k in new_aliases), 'Coriander seed/powder alias remains')

    ingredients = read_csv(root / DATA / 'recipe_ingredients.csv')
    ingredients_json = read_json(root / DATA / 'recipe_ingredients.json')
    parity(ingredients, ingredients_json)
    live = index(ingredients)
    pins = {x['before']['id']: x for x in review['rows']}
    require(len(pins) == len(review['rows']) == EXPECTED_ROWS, 'Review manifest row count drift')
    expected = {rid: expected_row(pin, new_by_code) for rid, pin in pins.items()}
    for rid, pin in pins.items():
        require(rid in live and logical(live[rid]) in (logical(pin['before']), logical(expected[rid])), f'Row drift: {rid}')

    for cohort, (source, target, count) in COHORTS.items():
        pinned = {rid for rid, pin in pins.items() if pin['cohort'] == cohort}
        require(len(pinned) == count, f'Reviewed cohort count drift: {cohort}')
        require(all(pins[rid]['target_code'] == target for rid in pinned), f'Reviewed target drift: {cohort}')
        if source is not None:
            require(all(pins[rid]['before']['master_ingredient_code'] == source for rid in pinned), f'Reviewed source drift: {cohort}')
    require({rid for rid, pin in pins.items() if pin['cohort'] == 'seed_powder_to_unmatched'} == set(SEED_POWDER_ROW_IDS), 'Seed/powder row pins drift')
    require({rid for rid, pin in pins.items() if pin['cohort'] == 'bitter_gourd_4050_to_4055'} == {BITTER_GOURD_ROW_ID}, 'Bitter gourd row pin drift')
    require({r['id'] for r in ingredients if r['master_ingredient_code'] in CATALOG_PATCHES} <= pins.keys(), 'Additional rows on repaired codes')
    # Holds before and after the repair: no coriander seed/powder row outside the
    # reviewed four may carry a code. After the clear, this set is empty.
    coded_guarded = {r['id'] for r in ingredients
                     if (r['master_ingredient_code'] or '').strip()
                     and is_coriander_seed_powder_text(r['raw_text'], r['cleaned_name'])}
    require(coded_guarded <= set(SEED_POWDER_ROW_IDS), f'Unreviewed coded coriander seed/powder rows: {sorted(coded_guarded - set(SEED_POWDER_ROW_IDS))}')

    def transform(rows):
        mutable = set(NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name', 'match_method', 'match_confidence'}
        return [dict(r, **{k: v for k, v in expected[r['id']].items() if k in mutable})
                if r['id'] in expected else dict(r) for r in rows]
    new_ing, new_ing_json = transform(ingredients), transform(ingredients_json)
    parity(new_ing, new_ing_json)

    populations = {code: sum(1 for r in new_ing if (r['master_ingredient_code'] or '') == code)
                   for code in EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in new_ing if r['match_method'] == 'UNMATCHED')
    require(populations == EXPECTED_POPULATIONS, f'Final population drift: {populations}')
    require(populations['UNMATCHED'] == sum(1 for r in new_ing if not (r['master_ingredient_code'] or '').strip()), 'UNMATCHED/blank-code mismatch')
    corpus_nulls = {f: sum(1 for r in new_ing if r[f] in (None, '')) for f in NUTRIENTS}
    require(corpus_nulls == EXPECTED_CORPUS_NULLS, f'Corpus null drift: {corpus_nulls}')

    ordered = sorted(pins)
    combined = nutrient_report([pins[rid]['before'] for rid in ordered], [expected[rid] for rid in ordered])
    require({f: combined[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_NUTRITION_DELTA,
            f"Nutrition delta drift: {[combined[f]['known_sum_delta'] for f in NUTRIENTS]}")
    require({f: (combined[f]['before_null_count'], combined[f]['after_null_count']) for f in NUTRIENTS} == EXPECTED_NULL_TRANSITIONS,
            'Null transition drift')

    recipes_affected = {expected[rid]['recipe_id'] for rid in pins}
    require(len(recipes_affected) == EXPECTED_RECIPES, f'Recipe radius drift: {len(recipes_affected)}')
    recipes = read_csv(root / DATA / 'recipes.csv')
    recipes_json = read_json(root / DATA / 'recipes.json')
    parity(recipes, recipes_json)
    new_recipes, new_recipes_json = deepcopy(recipes), deepcopy(recipes_json)
    rollups = recompute_recipe_rollups(new_ing)
    affected_rollups = {k: v for k, v in rollups.items() if k in recipes_affected}
    _apply_rollups(new_recipes, affected_rollups)
    _apply_rollups(new_recipes_json, affected_rollups)
    # Radius is measured against the reviewed BEFORE state, reconstructed from the
    # manifest, so the figures are identical on a first apply and on a replay.
    baseline_ing = [dict(pins[r['id']]['before']) if r['id'] in pins else dict(r) for r in ingredients]
    baseline_rollups = recompute_recipe_rollups(baseline_ing)
    changed_rollups = {rid for rid in rollups if _new_totals(baseline_rollups[rid]) != _new_totals(rollups[rid])}
    require(changed_rollups == recipes_affected, f'Rollup radius drift: {len(changed_rollups)}')
    _recompute_status([r for r in new_recipes_json if r['id'] in recipes_affected], new_ing_json)
    baseline_status, new_status = nutrition_status(baseline_ing, recipes_json), nutrition_status(new_ing, recipes_json)
    transitions = {}
    for rid in sorted(recipes_affected):
        if baseline_status[rid] != new_status[rid]:
            transitions[rid] = {'before': baseline_status[rid], 'after': new_status[rid]}
    labels = {rid for rid, t in transitions.items() if t['before'][0] != t['after'][0]}
    status = {'recipes_with_changed_missing_count': len(transitions),
              'recipes_with_status_label_changed': len(labels),
              'status_transitions': {rid: f"{t['before'][0]} -> {t['after'][0]}" for rid, t in transitions.items()
                                     if rid in labels}}
    require(status['recipes_with_changed_missing_count'] == 4, f'missing_nutrition_count radius drift: {status}')
    require(labels == {STATUS_TRANSITION_RECIPE}
            and status['status_transitions'][STATUS_TRANSITION_RECIPE] == 'COMPLETE -> PARTIAL', f'Status transition drift: {status}')
    require(index(new_recipes_json)[STATUS_TRANSITION_RECIPE]['nutrition_status'] == 'PARTIAL', 'Reviewed status transition recipe drift')
    parity(new_recipes, new_recipes_json)

    relationships = read_json(root / DATA / 'recipe_name_alias_decisions.json')['relationships']
    outputs, _ = compose_reviewed_aliases(new_recipes, new_ing, new_cat, relationships)
    # Canonical radius is also measured against the composed BEFORE state, for the
    # same replay reason. Identity stability is still checked against the live files.
    baseline_cat = deepcopy(new_cat)
    baseline_by_code = index(baseline_cat, 'code')
    for record in review['catalog_before']:
        baseline_by_code[record['code']].update(record)
    baseline_recipes = deepcopy(recipes)
    _apply_rollups(baseline_recipes, {k: v for k, v in baseline_rollups.items() if k in recipes_affected})
    baseline_outputs, _ = compose_reviewed_aliases(baseline_recipes, baseline_ing, baseline_cat, relationships)
    canonical = {}
    for name in ('canonical_recipes.csv', 'canonical_recipe_ingredients.csv', 'recipe_canonical_mapping.csv'):
        old_rows = read_csv(root / DATA / name)
        key = 'original_recipe_id' if name == 'recipe_canonical_mapping.csv' else 'id'
        before, after = index(baseline_outputs[name], key), index(outputs[name], key)
        require(index(old_rows, key).keys() == after.keys() == before.keys(), f'Canonical ID drift: {name}')
        changed = [rid for rid in before if logical(before[rid]) != logical(after[rid])]
        if name == 'recipe_canonical_mapping.csv':
            stable = ('canonical_recipe_id', 'phase1_canonical_recipe_id', 'selected_source_url',
                      'canonical_group_id', 'canonical_dish_name', 'duplicate_group_size')
            require(all(all(logical(before[rid])[f] == logical(after[rid])[f] for f in stable) for rid in before),
                    'Canonical mapping / representative drift')
            affected_groups = {r['canonical_recipe_id'] for rid, r in before.items() if rid in recipes_affected}
            require(all(before[rid]['canonical_recipe_id'] in affected_groups for rid in changed),
                    'Unrelated canonical mapping group changed')
        elif name == 'canonical_recipe_ingredients.csv':
            require(set(changed) <= pins.keys(), 'Unrelated canonical ingredients changed')
        else:
            require(set(changed) <= recipes_affected, 'Unrelated canonical recipe changed')
        if name in EXPECTED_CANONICAL:
            require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')
        canonical[name] = {'changed_count': len(changed)}

    files = {CAT: new_cat, ALIASES: new_aliases,
             DATA/'recipe_ingredients.csv': new_ing, DATA/'recipe_ingredients.json': new_ing_json,
             DATA/'recipes.csv': new_recipes, DATA/'recipes.json': new_recipes_json}
    before_files = {CAT: cat, ALIASES: aliases, DATA/'recipe_ingredients.csv': ingredients,
                    DATA/'recipe_ingredients.json': ingredients_json, DATA/'recipes.csv': recipes,
                    DATA/'recipes.json': recipes_json}
    changed_now = [rid for rid in pins if logical(live[rid]) != logical(expected[rid])]
    report = dict(
        policy='DISPLAY_NAME_BATCH_A',
        root_cause='Four catalog rows carried a Vietnamese display name belonging to a different food, so alias and exact matching resolved 1,176 rows onto the wrong identity.',
        rows_repaired=EXPECTED_ROWS, rows_pending=len(changed_now), recipes_affected=EXPECTED_RECIPES,
        catalog_count=750,
        catalog_diff={c: {k: {'before': next(r for r in review['catalog_before'] if r['code'] == c)[k], 'after': v}
                          for k, v in patch.items()} for c, patch in CATALOG_PATCHES.items()},
        alias_diff={k: {'before': review['aliases_before'][k], 'after': v} for k, v in sorted(ALIAS_PATCHES.items())},
        alias_keeps=ALIAS_KEEPS, alias_map_size=len(new_aliases),
        guard=dict(reason=CORIANDER_SEED_POWDER_GUARD_REASON, routes=['match', 'match_batch'],
                   coded_rows_cleared=sorted(SEED_POWDER_ROW_IDS),
                   reviewed_phrases_blocked=sum(1 for r in ingredients if is_coriander_seed_powder_text(r['raw_text'], r['cleaned_name'])),
                   aliases_removed=['bột rau mùi', 'hạt rau mùi']),
        populations=populations, corpus_nulls=corpus_nulls,
        combined_nutrition=combined, recipe_status=status, canonical=canonical,
        canonical_id_drift=0, representative_drift=0,
        affected_recipe_ids=sorted(recipes_affected),
        row_outcomes={rid: dict(cohort=pins[rid]['cohort'], before=pins[rid]['before'], after=expected[rid]) for rid in ordered},
        cohorts={}, exclusions=[
            '56 khổ qua rows on 4050 (Batch B)', 'khổ qua rừng rows', 'broad khô alias',
            'broad đồng alias', 'parsley misroutes outside this classification',
            'generic rau dền', 'beetroot / galangal false textual matches', 'mandarin peel rows',
            'recipe-title rows', '4010 / 4016', '4050 / 4121 chain beyond d6f83055',
            'duplicate extension pairs', 'catalog gaps', 'dangling 13038',
            'global stale cleaned_name', 'parser fixes',
        ])
    recipe_before, recipe_after = index(recipes_json), index(new_recipes_json)
    report['recipe_outcomes'] = {rid: {'before': recipe_before[rid], 'after': recipe_after[rid]} for rid in sorted(recipes_affected)}
    for cohort, (source, target, _count) in COHORTS.items():
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        report['cohorts'][cohort] = dict(
            source_code=source, target_code=target, row_count=len(ids),
            recipe_count=len({expected[rid]['recipe_id'] for rid in ids}), row_ids=ids,
            nutrition=nutrient_report([pins[rid]['before'] for rid in ids], [expected[rid] for rid in ids]))
    return files, before_files, report


def replay(matcher):
    """Every reviewed identity, on both the single and batched route."""
    result = {}
    batch = matcher.match_batch(list(PROBES), raw_contexts=list(PROBES))
    for (query, code), batched in zip(PROBES.items(), batch):
        single = matcher.match(query, raw_context=query)
        for value in (single, batched):
            require((value['matched_item'] or {}).get('code') == code, f'Matcher replay failed: {query}: {value}')
            if code is None:
                require(value['method'] == 'UNMATCHED' and value['confidence'] is None, f'Guard verdict drift: {query}')
        result[query] = {'code': code or 'UNMATCHED', 'single_method': single['method'],
                         'batch_method': batched['method'], 'guard': single.get('guard')}
    require(all(r['guard'] == CORIANDER_SEED_POWDER_GUARD_REASON for q, r in result.items() if PROBES[q] is None), 'Guard reason drift')
    return result


def write_report(report, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'applied_fix.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = ['# Display-name corruption repair, Batch A', '',
             f"Policy: DISPLAY_NAME_BATCH_A. {report['rows_repaired']} ingredient rows / {report['recipes_affected']} source recipes.", '',
             'Only `name_vi` changes in the catalog. Codes, `name_en`, categories and all nutrition columns are untouched; each replacement is the identity the row\'s own `name_en` already asserts.', '',
             '## Exact catalog changes', '', '| Code | Field | Before | After | name_en (unchanged) |', '|---|---|---|---|---|']
    for code, fields in report['catalog_diff'].items():
        for field, change in fields.items():
            lines.append(f"| {code} | {field} | {change['before']} | {change['after']} | {report['catalog_name_en'][code]} |")
    lines += ['', '## Exact alias changes', '', f"Alias map size {report['alias_map_size']}.", '',
              '| Alias | Before | After |', '|---|---|---|']
    for alias, change in report['alias_diff'].items():
        lines.append(f"| {alias} | {change['before']} | {change['after'] or 'removed'} |")
    lines += ['', 'Reviewed aliases that were always correct against `name_en` and stay put: ' +
              ', '.join(f'`{k}` → {v}' for k, v in report['alias_keeps'].items()) + '.', '',
              'Deliberately unchanged: the broad `khô` → 5029 and `đồng` aliases, and `mướp đắng`/`khổ qua` → 4050 (Batch B).', '',
              '## Coriander seed/powder guard', '',
              f"Guard reason `{report['guard']['reason']}`, applied on both `{'` and `'.join(report['guard']['routes'])}`. "
              f"The catalog has no coriander seed or powder identity, and removing the two aliases alone does not reach UNMATCHED: "
              f"`rau mùi` is a catalog subphrase head, so both phrases fall through to SUBPHRASE_CATALOG_MATCH 4081 at 0.95. "
              f"The guard blocks {report['guard']['reviewed_phrases_blocked']} reviewed rows; only the "
              f"{len(report['guard']['coded_rows_cleared'])} that carried a code change state.", '',
              '## Processed rows and nutrition', '',
              'Nutrition sums include known values only; missing values remain null. Exact before/after records for all '
              f"{report['rows_repaired']} ingredient rows and {report['recipes_affected']} recipes are in [applied_fix.json](applied_fix.json).", '',
              '| Cohort | Source | Target | Rows | Recipes | kcal delta | Protein delta | Fat delta | Carbs delta |',
              '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for name, c in report['cohorts'].items():
        lines.append(f"| {name} | {c['source_code'] or '-'} | {c['target_code'] or 'UNMATCHED'} | {c['row_count']} | {c['recipe_count']} | "
                     + ' | '.join(c['nutrition'][f]['known_sum_delta'] for f in NUTRIENTS) + ' |')
    lines += ['', '| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |', '|---|---:|---:|---:|---:|']
    for field, n in report['combined_nutrition'].items():
        lines.append(f"| {field} | {n['before_known_sum']} | {n['after_known_sum']} | {n['known_sum_delta']} | {n['before_null_count']} → {n['after_null_count']} |")
    lines += ['', 'Corpus-wide null counts after: ' + json.dumps(report['corpus_nulls']) + '.', '',
              'Recipe status transitions: ' + json.dumps(report['recipe_status'], ensure_ascii=False) + '.', '',
              '## Final populations', '', '| Code | Rows |', '|---|---:|']
    for code, count in report['populations'].items():
        lines.append(f'| {code} | {count} |')
    lines += ['', '## Matcher replay', '', '| Query | Code | Single route | Batch route |', '|---|---|---|---|']
    for query, result in report.get('matcher_replay', {}).items():
        lines.append(f"| {query} | {result['code']} | {result['single_method']} | {result['batch_method']} |")
    lines += ['', '## Canonical propagation', '', '| Artifact | Changed logical records |', '|---|---:|']
    for name, values in report['canonical'].items():
        lines.append(f"| {name} | {values['changed_count']} |")
    lines += ['', 'Canonical ID drift = 0; representative drift = 0.', '',
              '## Embeddings and validation', '',
              'Embeddings: ' + json.dumps(report.get('embeddings', {}), ensure_ascii=False), '',
              'Validation: ' + json.dumps(report.get('validation', {}), ensure_ascii=False), '',
              'Tests: ' + json.dumps(report.get('tests', {}), ensure_ascii=False), '',
              'Excluded: ' + '; '.join(report['exclusions']) + '.', '', 'No commit or push.']
    if 'git' in report:
        lines += ['', '## Git validation and changed files', '',
                  'git diff --check: ' + report['git']['diff_check'] + '.', '',
                  'Branch: ' + report['git']['branch'] + '. All changes remain unstaged.', '',
                  '```text', *report['git']['status_short'], '```']
    (out/'applied_fix.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def run(apply=False, root=ROOT, out=OUT, tests=None):
    files, before_files, report = plan(root)
    report['catalog_name_en'] = {r['code']: r['name_en'] for r in files[CAT] if r['code'] in CATALOG_PATCHES}
    if not apply:
        return report
    changed = [p for p in files if (files[p] != before_files[p] if p.suffix == '.json'
                                    else [logical(r) for r in files[p]] != [logical(r) for r in before_files[p]])]
    prior = out/'applied_fix.json'
    cache = (root/CAT).with_name('catalog_embeddings_bkai.pt')
    tracked = subprocess.run(['git', 'ls-files', '--', str(cache.relative_to(root))], cwd=root,
                             capture_output=True, text=True, check=True).stdout.strip()
    require(not tracked, 'Embedding cache unexpectedly tracked; review version-control policy')
    if not changed and prior.exists():
        previous = read_json(prior)
        if previous.get('validation', {}).get('complete') and cache.exists():
            require(hashlib.sha256(cache.read_bytes()).hexdigest() == previous['embeddings']['sha256'], 'Embedding cache drift')
            require(embedding_input_digest(files[CAT]) == previous['embeddings']['input_sha256'], 'Embedding catalog-input drift')
            verify_canonical(root)
            previous = dict(previous, rows_pending=0, idempotent=True)
            # A replay re-verifies the blast radius and refreshes the recorded
            # git state / test summary without touching any data file.
            previous['validation'] = dict(previous['validation'], **git_blast_radius(root))
            previous['git'] = git_state(root)
            if tests:
                previous['tests'] = tests
            write_report(previous, out)
            return previous
        report = dict(previous, rows_pending=0)
    interim_before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (root/'data/interim').rglob('*') if p.is_file()}
    # Catalog first, then aliases, then processed rows and rollups.
    for path in (CAT, ALIASES, DATA/'recipe_ingredients.csv', DATA/'recipe_ingredients.json',
                 DATA/'recipes.csv', DATA/'recipes.json'):
        if path not in changed:
            continue
        if path.suffix == '.csv':
            write_csv(root/path, files[path], list(files[path][0]))
        else:
            write_json(root/path, files[path])
    report['status'] = 'processed_applied_validation_pending'
    write_report(report, out)
    import torch
    matcher = VietnameseIngredientMatcher(root/CAT)
    cache.unlink(missing_ok=True)
    matcher._init_model()
    tensor = torch.load(cache, map_location=matcher.device, weights_only=True)
    require(tensor.shape[0] == len(matcher.catalog) == 750, 'Embedding shape drift')
    require(torch.equal(tensor, matcher.catalog_embeddings), 'Cache differs from generated embeddings')
    digest = hashlib.sha256(cache.read_bytes()).hexdigest()
    matcher.catalog_embeddings = None
    matcher._compute_catalog_embeddings()
    require(torch.equal(tensor, matcher.catalog_embeddings) and hashlib.sha256(cache.read_bytes()).hexdigest() == digest, 'Cache not reusable')
    report['embeddings'] = dict(rebuilt=True, tracked=False, shape=list(tensor.shape), sha256=digest,
                                next_load_equal=True, input_sha256=embedding_input_digest(matcher.catalog),
                                build_inputs={r['code']: f"{r['name_vi']} ({r['category_vi']})"
                                              for r in matcher.catalog if r['code'] in CATALOG_PATCHES})
    report['matcher_replay'] = replay(matcher)
    for command in (['scripts/canonicalize_recipes.py'], ['scripts/export_canonical_json.py']):
        subprocess.run([sys.executable, *command], cwd=root, check=True)
    verify_canonical(root)
    require(interim_before == {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (root/'data/interim').rglob('*') if p.is_file()}, 'Historical/interim data changed')
    require(plan(root)[2]['rows_pending'] == 0, 'Processed repair failed read-back')
    report['status'] = 'applied'
    report['validation'] = dict(complete=True, processed_parity=True, canonical_parity=True,
                                canonical_check=True, canonical_determinism=True, interim_unchanged=True,
                                **git_blast_radius(root))
    report['git'] = git_state(root)
    if tests:
        report['tests'] = tests
    write_report(report, out)
    return report


def git_blast_radius(root):
    """Independent check: diff the live files against their pre-fix git blobs."""
    def head(path):
        out = subprocess.run(['git', 'show', f'HEAD:{path}'], cwd=root, capture_output=True, check=True).stdout
        return out.decode('utf-8-sig')

    def parse(text):
        return list(csv.DictReader(io.StringIO(text)))

    def diff(path, key='id'):
        before = index(parse(head(path)), key)
        after = index(read_csv(root / path), key)
        require(before.keys() == after.keys(), f'Record identity drift vs HEAD: {path}')
        return {rid for rid in before if before[rid] != after[rid]}

    rows = diff(str(DATA/'recipe_ingredients.csv').replace('\\', '/'))
    pinned = {x['before']['id'] for x in read_json(REVIEW)['rows']}
    require(rows == pinned, f'Rows changed vs HEAD are not the reviewed set: {len(rows)}')
    recipes = diff(str(DATA/'recipes.csv').replace('\\', '/'))
    require(len(recipes) == EXPECTED_RECIPES, f'Recipes changed vs HEAD: {len(recipes)}')
    catalog = diff(str(CAT).replace('\\', '/'), 'code')
    require(catalog == set(CATALOG_PATCHES), f'Catalog rows changed vs HEAD: {catalog}')
    aliases_before = json.loads(head(str(ALIASES).replace('\\', '/')))
    aliases_after = read_json(root / ALIASES)
    keys = {k for k in aliases_before.keys() | aliases_after.keys()
            if aliases_before.get(k) != aliases_after.get(k)}
    require(keys == set(ALIAS_PATCHES), f'Alias keys changed vs HEAD: {len(keys)}')
    return dict(rows_changed_vs_git_head=len(rows), recipes_changed_vs_git_head=len(recipes),
                catalog_rows_changed_vs_git_head=len(catalog), alias_keys_changed_vs_git_head=len(keys),
                unexpected_rows_changed=0,
                canonical_changed_vs_git_head={
                    name: len(diff(str(DATA/name).replace('\\', '/'),
                                   'original_recipe_id' if 'mapping' in name else 'id'))
                    for name in ('canonical_recipe_ingredients.csv', 'canonical_recipes.csv',
                                 'recipe_canonical_mapping.csv')})


def git_state(root):
    def run_git(*args):
        return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=True).stdout
    check = run_git('diff', '--check')
    return dict(diff_check='passed' if not check.strip() else check.strip(),
                branch=run_git('rev-parse', '--abbrev-ref', 'HEAD').strip(),
                status_short=[line for line in run_git('status', '--short').splitlines() if line])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--tests', help='JSON summary of the validation test run, recorded in the report')
    args = parser.parse_args()
    report = run(apply=args.apply, tests=json.loads(args.tests) if args.tests else None)
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ('row_outcomes', 'recipe_outcomes', 'affected_recipe_ids', 'matcher_replay', 'cohorts')},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
