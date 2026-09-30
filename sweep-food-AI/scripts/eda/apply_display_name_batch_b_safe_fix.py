"""DISPLAY_NAME_BATCH_B: reviewed 118-row / 110-recipe repair; dry-run by default.

Batch A repaired four displaced display names. The 4121 -> 4050 -> 4055 chain is
the remainder: 4121 (`Onion shallot, scallion, pickled with salt`) carries
4050's Vietnamese name, and 4050 (`Bamboo shoot, fermented, raw`) carries 4055's.
Each replacement is the identity the row's own name_en already asserts, so
name_vi is the only column that moves -- code, name_en, category and every
nutrition column are asserted unchanged.

4050 becomes `Măng chua, măng tre` and 4121 becomes `Kiệu muối`. The punctuation
is reviewed, not incidental: the matcher's subphrase stage indexes
`normalize_vietnamese_text(name_vi.split(',')[0])`, so the comma in 4050's name
publishes `măng chua` as a retrieval head -- which is what recovers the reviewed
`măng chua ớt` row -- while 4121 stays comma-less on purpose. A raw
`Kiệu, muối` would publish a bare `kiệu` head and hand every ambiguous kiệu row
a 0.95 subphrase match onto a pickle identity nobody reviewed.

The adjacent JSON is a frozen review manifest, never discovered or refreshed at
runtime: it carries the complete before record of all 118 rows plus the reviewed
before values of the two catalog rows, the nine repointed aliases, the three
reviewed keeps and the eleven 20077 aliases this batch must not touch. Rows are
never selected by current code alone -- each pinned row must equal its reviewed
before state or its computed after state.

117 rows are identity remaps that preserve their existing match provenance.
The 118th is the reviewed UNMATCHED recovery 545ef564 `Măng chua ớt 500 gr`,
whose match_method/match_confidence are not preserved but measured: --apply
re-runs the real matcher against the repaired catalog and aliases and requires
the pinned SUBPHRASE_CATALOG_MATCH / 0.95 / 4050 verdict on both routes.

4121 vs 20077 is NOT resolved here. 20077, its 29 rows, its 11 aliases and the
18 UNMATCHED kiệu rows are asserted untouched and recorded as
`4121_vs_20077_duplicate_resolution = DEFERRED_NEEDS_DOMAIN_REVIEW`.

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

from nlp.entity_matcher import VietnameseIngredientMatcher, normalize_vietnamese_text
from nlp.matching_integrity import stage_qwen_update
from scripts.eda.apply_qwen_safe_fix import (
    read_csv, read_json, write_json, recompute_recipe_rollups, _apply_rollups, _new_totals,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
from scripts.canonicalize_recipes import compose_reviewed_aliases

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('display_name_batch_b_reviewed_state.json')
OUT = ROOT / 'reports/eda/display_name_batch_b_fix'
CAT = Path('data/processed/viendinhduong/master_ingredients_nutrition.csv')
ALIASES = CAT.with_name('ingredient_alias_map.json')
DATA = Path('data/processed/recipes')
NUTRIENTS = ('calories', 'protein_g', 'fat_g', 'carbs_g')

# name_vi only. 4050 is `Bamboo shoot, fermented, raw`; 4121 is `Onion shallot,
# scallion, pickled with salt`. 4055 already reads `Mướp đắng` after Batch A and
# is deliberately NOT touched here.
CATALOG_PATCHES = {
    '4050': {'name_vi': 'Măng chua, măng tre'},
    '4121': {'name_vi': 'Kiệu muối'},
}
# The reviewed subphrase heads these names publish. 4050 wants `măng chua` as a
# retrieval surface; 4121 must not publish a bare `kiệu` one.
EXPECTED_SUBPHRASE_HEADS = {'4050': 'măng chua', '4121': 'kiệu muối'}
FORBIDDEN_SUBPHRASE_HEAD = 'kiệu'

SOUR_BAMBOO_ALIASES = ('măng chua', 'măng muối', 'măng le chua')
BITTER_GOURD_ALIASES = ('khổ qua', 'khổ qua bào', 'trái khổ qua', 'quả mướp đắng',
                        'ăn kèm khổ qua', 'mướp đắng')
ALIAS_PATCHES = {
    **{k: '4050' for k in SOUR_BAMBOO_ALIASES},
    **{k: '4055' for k in BITTER_GOURD_ALIASES},
}
# Reviewed aliases that were always correct against name_en and stay put.
ALIAS_KEEPS = {'kiệu muối': '4121', 'măng chua măng tre': '4050', 'mướp đắng tươi': '4055'}
# The frozen manifest recorded 4672 -- the live size when this batch was reviewed.
# DISPLAY_NAME_BATCH_C2 later removed 3 celery/fragment keys and added 5 white-cabbage
# keys (4672 -> 4674), and DISPLAY_NAME_BATCH_C1 then removed the 2 spinach/kale keys
# and added 8 mustard-green/napa/kimchi keys (4674 -> 4680), so the live map is 4680.
# This batch still adds and removes nothing, and that is what the assertions below
# state: they are checked against the LIVE size, with the historical reviewed size
# asserted separately, so neither figure is weakened.
# C3 repaired parser-damaged white-cabbage rows and added four aliases.
ALIAS_MAP_SIZE = 4684
REVIEWED_ALIAS_MAP_SIZE = 4672
# cohort -> (source code, target code, reviewed row count)
COHORTS = {
    'sour_bamboo_4121_to_4050': ('4121', '4050', 61),
    'bitter_gourd_4050_to_4055': ('4050', '4055', 56),
    'sour_bamboo_chilli_recovery': (None, '4050', 1),
}
RECOVERY_ROW_ID = '545ef564-0e83-4df7-ba4c-871629598ae0'
RECOVERY_RAW_TEXT = 'Măng chua ớt 500 gr'
# Measured against the repaired catalog/alias state at --apply, not asserted from
# memory: `măng chua ớt` has no alias, so it reaches 4050 through the new
# `măng chua` subphrase head.
RECOVERY_QUERY = 'măng chua ớt'
RECOVERY_MATCH = {'code': '4050', 'method': 'SUBPHRASE_CATALOG_MATCH', 'confidence': 0.95}
RECOVERY_NUTRITION = {'calories': '140.0', 'protein_g': '7.0', 'fat_g': None, 'carbs_g': '27.5'}

# C3 repaired parser-damaged white-cabbage rows; own reviewed row sets remain unchanged.
EXPECTED_POPULATIONS = {
    '4121': 0, '4050': 62, '4055': 57, '20077': 29,
    # Sibling bamboo/gourd identities this batch must not disturb. The three bamboo
    # counts were 4048: 21, 4051: 49, 4053: 2 when Batch B ran; BAMBOO_SHOOT_ALIAS_FIX
    # later repointed `măng khô` off 4048 and `măng tươi` / `măng tươi bào` off 4051
    # onto 4053, which is what moved them. Batch B's own 118 rows are unaffected.
    '4048': 1, '4051': 34, '4053': 37, '4054': 70,
    # UNMATCHED was superseded again by DISPLAY_NAME_BATCH_C1: 35 clears minus 5
    # mustard-green recoveries is a net +30. Batch B's own 118 rows are unaffected.
    'UNMATCHED': 8495,
}
EXPECTED_NUTRITION_DELTA = {
    'calories': '-952.1', 'protein_g': '-36.8', 'fat_g': '0', 'carbs_g': '-197.8',
}
# The 117 identity remaps alone, excluding the approved recovery.
EXPECTED_BASE_NUTRITION_DELTA = {
    'calories': '-1092.1', 'protein_g': '-43.8', 'fat_g': '0', 'carbs_g': '-225.3',
}
# The pre-implementation review estimated carbs_g -224.9 / -197.4. That estimate
# rounded 4.1 g/100 g exactly; the project scales with nlp.nutrition.scale_nutrition,
# i.e. float round(value * weight / 100, 1). Four of the 56 khổ qua rows weigh
# 150 g, where 4.1 * 1.5 == 6.15 straddles the boundary: the live pipeline (and
# the live corpus) produce 6.1, exact rounding produces 6.2, for 4 * 0.1 = 0.4.
# The measured figure above is the one the data actually takes.
REVIEW_ESTIMATE_NUTRITION_DELTA = {
    'base_117': {'calories': '-1092.1', 'protein_g': '-43.8', 'fat_g': '0', 'carbs_g': '-224.9'},
    'total_118': {'calories': '-952.1', 'protein_g': '-36.8', 'fat_g': '0', 'carbs_g': '-197.4'},
    'divergence': {'carbs_g': '-0.4'},
    'cause': ('4 khổ qua rows at 150 g: 4.1 * 1.5 = 6.15 rounds to 6.1 under the '
              "project's float scaler and to 6.2 under exact decimal rounding."),
}
EXPECTED_NULL_TRANSITIONS = {
    'calories': (1, 0), 'protein_g': (1, 0), 'fat_g': (118, 118), 'carbs_g': (1, 0),
}
# The 117 identity remaps make no null transition at all; only the recovery does.
EXPECTED_BASE_NULL_TRANSITIONS = {
    'calories': (0, 0), 'protein_g': (0, 0), 'fat_g': (117, 117), 'carbs_g': (0, 0),
}
# fat_g moved 20239 -> 20219 when BAMBOO_SHOOT_ALIAS_FIX repointed `măng khô` off
# 4048 (no fat value) onto 4051 (2.1 g/100 g).
# UNMATCHED and the corpus null counts were superseded by DISPLAY_NAME_BATCH_C2,
# which cleared 6 multi-identity cabbage/celery rows to UNMATCHED and recovered 2
# stored-UNMATCHED white-cabbage rows: 8465 - 2 + 6 = 8469, and the same net +4 on
# each nutrient's null count. Batch B's own 118 rows are unaffected.
# Superseded once more by DISPLAY_NAME_BATCH_C1: net +30 on every nutrient from its
# 35 clears and 5 recoveries, plus a further +9 on fat_g alone, because the eight
# fresh-napa rows (4109) and the one salted-napa row (4115) move onto identities that
# publish no fat_g value. Batch B's own 118 rows are unaffected.
EXPECTED_CORPUS_NULLS = {
    'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454,
}
EXPECTED_ROWS = 118
EXPECTED_RECIPES = 110
EXPECTED_CANONICAL = {
    'canonical_recipe_ingredients.csv': 112,
    'canonical_recipes.csv': 104,
    'recipe_canonical_mapping.csv': 1,
}
# The recovery is the only row whose UNMATCHED/coded state changes, so it is the
# only recipe whose missing_nutrition_count moves. 2 of 11 rows missing calories
# becomes 1 of 11: both sides are below the 0.3 INCOMPLETE threshold, so the
# label stays PARTIAL and no status transition is expected anywhere.
RECOVERY_RECIPE_ID = '32a39c4a-c638-49c0-b90a-9d010017146e'
EXPECTED_MISSING_COUNT_RECIPES = {RECOVERY_RECIPE_ID}
EXPECTED_STATUS_LABEL_TRANSITIONS = {}

# Repaired identities, the reviewed alias repoints, and the sibling identities
# that must not move.
PROBES = {
    # Corrected by this batch.
    'măng chua': '4050', 'măng muối': '4050', 'măng le chua': '4050',
    'măng chua tươi': '4050', 'măng chua ớt': '4050',
    'khổ qua': '4055', 'khổ qua bào': '4055', 'trái khổ qua': '4055',
    'quả mướp đắng': '4055', 'ăn kèm khổ qua': '4055', 'mướp đắng': '4055',
    # Reviewed keeps.
    'kiệu muối': '4121', 'măng chua măng tre': '4050', 'mướp đắng tươi': '4055',
    # Unchanged siblings: bamboo, gourd and the deferred 20077 pickle.
    # `măng khô` and `măng tươi` were 4048 and 4051 here, and Batch B deferred both;
    # BAMBOO_SHOOT_ALIAS_FIX repaired them. Bare `măng` is still deferred on 4051.
    'măng tre': '4053', 'măng tre tươi': '4053', 'măng khô': '4051',
    'măng': '4051', 'măng tươi': '4053', 'măng tây': '20033',
    'khổ qua rừng': '4054', 'mướp': '4054', 'mướp hương': '4054', 'mướp nhật bản': '4056',
    'kiệu chua': '20077', 'dưa kiệu': '20077', 'củ kiệu chua ngọt': '20077',
    'dưa kiệu chua': '20077', 'củ kiệu muối': '20077',
    'hành củ muối': '4120', 'dưa giá đậu xanh': '4119',
}
# Pre-existing match()/match_batch() structural divergence, explicitly out of
# scope. Both already diverge on the live data. This batch does not fix them and
# does not move any stored row for them, but bare `kiệu` does change which code
# the SINGLE route reaches (4101 -> 4121) because `Kiệu muối` becomes a subphrase
# head; the batch route stays on 20077. Pinned so the shift cannot go unnoticed.
KNOWN_ROUTE_DIVERGENCE = {
    'kiệu': {'single_before': '4101', 'single_after': '4121', 'batch': '20077'},
    'củ kiệu': {'single_before': '4101', 'single_after': '4101', 'batch': '20077'},
}
# Catalog display names that already collide and stay deferred (Batch A baseline).
# `cần tây` left this set in DISPLAY_NAME_BATCH_C2, which repaired 4010 from the
# duplicated celery name to `Cải bắp trắng`. The invariant is kept, not weakened:
# the remaining two collisions are still deferred and still asserted exactly.
DEFERRED_DUPLICATE_NAMES = {'nấm kim châm', 'thịt trâu, đùi'}

DEFERRAL_KEY = '4121_vs_20077_duplicate_resolution'
DEFERRAL = {
    'status': 'DEFERRED_NEEDS_DOMAIN_REVIEW',
    '4121_raw_authority': ('4121 is a raw Vien Dinh Duong catalog row: code, name_en '
                           '"Onion shallot, scallion, pickled with salt", category and all '
                           'nutrition columns come from the source table. Only its Vietnamese '
                           'display name was corrupted, and only that is repaired here.'),
    '20077_authored_provenance': ('20077 "Củ kiệu muối (Dưa kiệu chua ngọt)" is a project-authored '
                                  'master extension, not a source-table row. It was added to carry '
                                  'the sweet-sour Tet pickle and owns 11 aliases and 29 processed rows.'),
    'preparation_ambiguity': ('The two are not obviously the same food: 4121 is salt-pickled '
                              'scallion/shallot bulb, 20077 is the sweetened chua ngọt preparation. '
                              'Vietnamese usage collapses both under "củ kiệu"/"kiệu", and the corpus '
                              'contains fresh kiệu, bare kiệu, nước củ kiệu and compound rows that '
                              'belong to neither without a human reading of each recipe.'),
    'nutrition_difference': ('Per 100 g: 4121 is 29 kcal / 1.3 g protein / null fat / 5.9 g carbs; '
                             '20077 is 55 kcal / 1.2 g protein / 0.1 g fat / 12.0 g carbs. Roughly '
                             'double the energy and carbohydrate, consistent with added sugar. '
                             'Merging either way would silently restate 29 or 61 rows of nutrition.'),
    'reason_no_automatic_merge': ('No mechanical signal separates them: same category, adjacent '
                                  'semantics, and lexical similarity alone is exactly the evidence '
                                  'AGENTS.md section 5 rejects. Choosing a survivor also decides '
                                  'which nutrition profile 29 reviewed rows inherit and whether 11 '
                                  'aliases move, so it needs a domain decision, not a code change.'),
    'preserved': {'catalog_name_vi': 'Củ kiệu muối (Dưa kiệu chua ngọt)', 'rows': 29, 'aliases': 11,
                  'unmatched_kieu_rows_left_deferred': 18},
}
# Left UNMATCHED on purpose: 11 sweet-sour kiệu rows, 2 fresh kiệu, 3 bare/
# ambiguous kiệu, 1 nước củ kiệu, 1 compound row.
EXPECTED_UNMATCHED_KIEU_ROWS = 18

EXCLUSIONS = [
    '4121 vs 20077 duplicate resolution', '11 UNMATCHED sweet-sour kiệu rows',
    'fresh kiệu and bare/ambiguous kiệu rows', 'nước củ kiệu row', 'compound kiệu row',
    'măng khô -> 4048', 'măng / măng tươi -> 4051', 'khổ qua rừng -> 4054',
    'match()/match_batch() structural divergence for kiệu and củ kiệu',
    'd6f83055 stale match_method/confidence', '4010 / 4016',
    'other duplicate-extension pairs', 'parser behaviour', 'stale code-space contamination',
]


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


def subphrase_head(name_vi):
    """The retrieval surface the matcher indexes for a catalog display name."""
    return normalize_vietnamese_text(name_vi.split(',')[0])


def expected_row(reviewed, catalog):
    """Row-level identity repair against the repaired catalog.

    The 117 remaps preserve their existing match provenance: this batch corrects
    which catalog identity a reviewed link points at, it does not re-run the
    matcher per row. The single reviewed recovery is the exception and carries an
    explicit `match_after`, which --apply verifies against the real matcher.
    """
    row = deepcopy(reviewed['before'])
    code = reviewed['target_code']
    match = reviewed.get('match_after') or {
        'match_method': row['match_method'], 'match_confidence': row['match_confidence']}
    patch = stage_qwen_update(row, catalog, float(row['estimated_weight_g']), {
        'master_ingredient_code': code, 'master_ingredient_name': catalog[code]['name_vi'], **match})
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
            'value_to_null': sum(x.get(f) not in (None, '') and y.get(f) in (None, '') for x, y in zip(before, after)),
            'null_to_value': sum(x.get(f) in (None, '') and y.get(f) not in (None, '') for x, y in zip(before, after)),
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
    require({r['original_recipe_id']: r['canonical_recipe_id'] for r in mapping} ==
            read_json(root/DATA/'recipe_canonical_mapping.json'), 'Canonical mapping JSON drift')


def plan(root=ROOT):
    review = read_json(REVIEW)
    cat = read_csv(root / CAT)
    require(len(cat) == review['catalog_count'] == 750, 'Catalog row count drift')
    by_code = index(cat, 'code')
    new_cat = deepcopy(cat)
    new_by_code = index(new_cat, 'code')
    require({r['code'] for r in review['catalog_before']} == set(CATALOG_PATCHES), 'Reviewed catalog scope drift')
    for before in review['catalog_before']:
        code = before['code']
        after = dict(before, **CATALOG_PATCHES[code])
        require(by_code.get(code) in (before, after), f'Catalog drift: {code}')
        require({k: v for k, v in before.items() if k != 'name_vi'} ==
                {k: v for k, v in after.items() if k != 'name_vi'}, f'Non-name catalog change: {code}')
        new_by_code[code].update(after)
    # 4055 is Batch A's repair and is explicitly out of this batch's catalog scope.
    require(new_by_code['4055'] == by_code['4055'] and by_code['4055']['name_vi'] == 'Mướp đắng',
            '4055 must not be modified by Batch B')

    def duplicates(rows):
        names = [normalize_vietnamese_text(r['name_vi']) for r in rows]
        return {n for n in names if names.count(n) > 1}
    before_dups, after_dups = duplicates(cat), duplicates(new_cat)
    require(after_dups <= before_dups, f'New duplicate catalog name: {after_dups - before_dups}')
    require(after_dups == DEFERRED_DUPLICATE_NAMES, f'Deferred duplicate drift: {after_dups}')
    # The reviewed punctuation, asserted through the matcher's own indexing rule.
    heads = {code: subphrase_head(new_by_code[code]['name_vi']) for code in CATALOG_PATCHES}
    require(heads == EXPECTED_SUBPHRASE_HEADS, f'Subphrase head drift: {heads}')
    require(not any(subphrase_head(r['name_vi']) == FORBIDDEN_SUBPHRASE_HEAD for r in new_cat),
            f'Repaired name publishes a bare {FORBIDDEN_SUBPHRASE_HEAD!r} retrieval head')

    aliases = read_json(root / ALIASES)
    require(len(aliases) == ALIAS_MAP_SIZE and review['alias_map_size'] == REVIEWED_ALIAS_MAP_SIZE,
            'Alias map size drift')
    new_aliases = dict(aliases)
    for key, before in review['aliases_before'].items():
        after = ALIAS_PATCHES.get(key, before)
        require(aliases.get(key) in (before, after), f'Alias drift: {key}')
        new_aliases[key] = after
    require(set(ALIAS_PATCHES) <= set(review['aliases_before']), 'Repointed alias missing from the manifest')
    for key, code in ALIAS_KEEPS.items():
        require(review['aliases_before'][key] == code and new_aliases[key] == code,
                f'Reviewed alias keep drift: {key}')
    deferred = {k: v for k, v in review['aliases_before'].items() if v == '20077'}
    require(len(deferred) == 11, f'Deferred 20077 alias count drift: {len(deferred)}')
    for key, code in deferred.items():
        require(aliases.get(key) == code and new_aliases.get(key) == code, f'Deferred 20077 alias changed: {key}')
    require({k for k in aliases.keys() | new_aliases.keys() if aliases.get(k) != new_aliases.get(k)}
            <= ALIAS_PATCHES.keys(), 'Unrelated alias change')
    require(len(new_aliases) == len(aliases) == ALIAS_MAP_SIZE, 'Alias map size changed')
    # Unlike Batch A, this chain moves aliases ONTO a repaired code as well as off
    # one, so "no alias targets a repaired code" is the wrong invariant here. What
    # must hold is that every alias left on a repaired code is reviewed: either a
    # keep that always meant that identity, or a patch that names it explicitly.
    reviewed_on_patched = {k for k, v in ALIAS_KEEPS.items() if v in CATALOG_PATCHES} | \
                          {k for k, v in ALIAS_PATCHES.items() if v in CATALOG_PATCHES}
    stale = {k: v for k, v in new_aliases.items() if v in CATALOG_PATCHES and k not in reviewed_on_patched}
    require(stale == {}, f'Unreviewed alias targets a repaired display identity: {stale}')
    # And nothing that the review moved may still sit on its old target.
    left_behind = {k: v for k, v in new_aliases.items()
                   if k in ALIAS_PATCHES and v != ALIAS_PATCHES[k]}
    require(left_behind == {}, f'Repointed alias not applied: {left_behind}')

    ingredients = read_csv(root / DATA / 'recipe_ingredients.csv')
    ingredients_json = read_json(root / DATA / 'recipe_ingredients.json')
    parity(ingredients, ingredients_json)
    live = index(ingredients)
    pins = {x['before']['id']: x for x in review['rows']}
    require(len(pins) == len(review['rows']) == EXPECTED_ROWS, 'Review manifest row count drift')
    expected = {rid: expected_row(pin, new_by_code) for rid, pin in pins.items()}
    for rid, pin in pins.items():
        require(rid in live and logical(live[rid]) in (logical(pin['before']), logical(expected[rid])),
                f'Row drift: {rid}')

    for cohort, (source, target, count) in COHORTS.items():
        pinned = {rid for rid, pin in pins.items() if pin['cohort'] == cohort}
        require(len(pinned) == count, f'Reviewed cohort count drift: {cohort}')
        require(all(pins[rid]['target_code'] == target for rid in pinned), f'Reviewed target drift: {cohort}')
        for rid in pinned:
            before = pins[rid]['before']
            if source is None:
                require(before['match_method'] == 'UNMATCHED'
                        and not (before['master_ingredient_code'] or '').strip(),
                        f'Reviewed recovery source drift: {rid}')
            else:
                require(before['master_ingredient_code'] == source, f'Reviewed source drift: {cohort}')
                require(before['match_method'] == 'PRESET_ALIAS_MATCH' and before['match_confidence'] == '0.98',
                        f'Reviewed provenance drift: {rid}')
                require(expected[rid]['match_method'] == before['match_method']
                        and expected[rid]['match_confidence'] == before['match_confidence'],
                        f'Match provenance not preserved: {rid}')
    # The reviewed khổ qua cohort is a semantic set, not "everything on 4050".
    recovery = pins[RECOVERY_ROW_ID]
    require(recovery['cohort'] == 'sour_bamboo_chilli_recovery'
            and recovery['before']['raw_text'] == RECOVERY_RAW_TEXT, 'Reviewed recovery row drift')
    require(recovery['match_after'] == {'match_method': RECOVERY_MATCH['method'],
                                        'match_confidence': str(RECOVERY_MATCH['confidence'])},
            'Reviewed recovery match verdict drift')
    require({k: expected[RECOVERY_ROW_ID][k] for k in NUTRIENTS} == RECOVERY_NUTRITION,
            f"Recovery nutrition drift: {[expected[RECOVERY_ROW_ID][k] for k in NUTRIENTS]}")
    gourd = {rid for rid, pin in pins.items() if pin['cohort'] == 'bitter_gourd_4050_to_4055'}
    require({pins[rid]['before']['cleaned_name'] for rid in gourd}
            == {'khổ qua', 'khổ qua bào', 'ăn kèm khổ qua'}, 'Reviewed khổ qua cohort drift')
    bamboo = {rid for rid, pin in pins.items() if pin['cohort'] == 'sour_bamboo_4121_to_4050'}
    require({pins[rid]['before']['cleaned_name'] for rid in bamboo} == {'măng chua'},
            'Reviewed măng chua cohort drift')
    # Never select by code alone: the pins must exhaust each source population.
    for code in ('4121', '4050'):
        require({r['id'] for r in ingredients if r['master_ingredient_code'] == code} <= pins.keys(),
                f'Unreviewed rows on source code {code}')
    require({rid for rid in pins if pins[rid]['before']['master_ingredient_code'] == '20077'} == set(),
            '20077 row pinned by Batch B')

    def transform(rows):
        mutable = set(NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name',
                                    'match_method', 'match_confidence'}
        return [dict(r, **{k: v for k, v in expected[r['id']].items() if k in mutable})
                if r['id'] in expected else dict(r) for r in rows]
    new_ing, new_ing_json = transform(ingredients), transform(ingredients_json)
    parity(new_ing, new_ing_json)

    populations = {code: sum(1 for r in new_ing if (r['master_ingredient_code'] or '') == code)
                   for code in EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in new_ing if r['match_method'] == 'UNMATCHED')
    require(populations == EXPECTED_POPULATIONS, f'Final population drift: {populations}')
    require(populations['UNMATCHED'] == sum(1 for r in new_ing if not (r['master_ingredient_code'] or '').strip()),
            'UNMATCHED/blank-code mismatch')
    corpus_nulls = {f: sum(1 for r in new_ing if r[f] in (None, '')) for f in NUTRIENTS}
    require(corpus_nulls == EXPECTED_CORPUS_NULLS, f'Corpus null drift: {corpus_nulls}')
    deferral = deferred_kieu_state(new_ing, new_aliases, new_by_code)

    ordered = sorted(pins)
    combined = nutrient_report([pins[rid]['before'] for rid in ordered], [expected[rid] for rid in ordered])
    require({f: combined[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_NUTRITION_DELTA,
            f"Nutrition delta drift: {[combined[f]['known_sum_delta'] for f in NUTRIENTS]}")
    require({f: (combined[f]['before_null_count'], combined[f]['after_null_count']) for f in NUTRIENTS}
            == EXPECTED_NULL_TRANSITIONS, 'Null transition drift')
    base = [rid for rid in ordered if rid != RECOVERY_ROW_ID]
    base_report = nutrient_report([pins[rid]['before'] for rid in base], [expected[rid] for rid in base])
    require({f: base_report[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_BASE_NUTRITION_DELTA,
            f"Base nutrition delta drift: {[base_report[f]['known_sum_delta'] for f in NUTRIENTS]}")
    require({f: (base_report[f]['before_null_count'], base_report[f]['after_null_count']) for f in NUTRIENTS}
            == EXPECTED_BASE_NULL_TRANSITIONS, 'Base null transition drift')
    require(all(base_report[f]['value_to_null'] == base_report[f]['null_to_value'] == 0 for f in NUTRIENTS),
            'The 117 identity remaps must make no null transition')
    # Missing fat stays missing on every repaired row; it is never coerced to zero.
    require(all(expected[rid]['fat_g'] is None for rid in ordered), 'Missing fat coerced on a repaired row')

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
    transitions = {rid: {'before': baseline_status[rid], 'after': new_status[rid]}
                   for rid in sorted(recipes_affected) if baseline_status[rid] != new_status[rid]}
    labels = {rid for rid, t in transitions.items() if t['before'][0] != t['after'][0]}
    status = {'recipes_with_changed_missing_count': len(transitions),
              'recipes_with_status_label_changed': len(labels),
              'missing_count_transitions': {rid: {'before': t['before'][1], 'after': t['after'][1]}
                                            for rid, t in transitions.items()},
              'status_transitions': {rid: f"{t['before'][0]} -> {t['after'][0]}" for rid, t in transitions.items()
                                     if rid in labels}}
    require(set(transitions) == EXPECTED_MISSING_COUNT_RECIPES, f'missing_nutrition_count radius drift: {status}')
    require(status['status_transitions'] == EXPECTED_STATUS_LABEL_TRANSITIONS, f'Status transition drift: {status}')
    require(transitions[RECOVERY_RECIPE_ID]['before'][1] == 2
            and transitions[RECOVERY_RECIPE_ID]['after'][1] == 1, 'Recovery missing count drift')
    require(index(new_recipes_json)[RECOVERY_RECIPE_ID]['missing_nutrition_count'] == 1
            and index(new_recipes_json)[RECOVERY_RECIPE_ID]['nutrition_status'] == 'PARTIAL',
            'Recovery recipe record drift')
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
            # Only the recovery changes a quality column: it is the one row whose
            # UNMATCHED state moves. The 117 identity remaps swap one valid code
            # for another, so no mapping counter moves for them.
            require(set(changed) <= {RECOVERY_RECIPE_ID}, f'Unexpected canonical mapping change: {changed}')
            canonical_groups = len({before[rid]['canonical_recipe_id'] for rid in recipes_affected})
            canonical[name] = {'changed_count': len(changed),
                               'mapping_rows_for_affected_recipes': len(recipes_affected & before.keys()),
                               'canonical_groups_involved': canonical_groups}
            require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')
            continue
        if name == 'canonical_recipe_ingredients.csv':
            require(set(changed) <= pins.keys(), 'Unrelated canonical ingredients changed')
        else:
            require(set(changed) <= recipes_affected, 'Unrelated canonical recipe changed')
        require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')
        canonical[name] = {'changed_count': len(changed)}

    files = {CAT: new_cat, ALIASES: new_aliases,
             DATA/'recipe_ingredients.csv': new_ing, DATA/'recipe_ingredients.json': new_ing_json,
             DATA/'recipes.csv': new_recipes, DATA/'recipes.json': new_recipes_json}
    before_files = {CAT: cat, ALIASES: aliases, DATA/'recipe_ingredients.csv': ingredients,
                    DATA/'recipe_ingredients.json': ingredients_json, DATA/'recipes.csv': recipes,
                    DATA/'recipes.json': recipes_json}
    changed_now = [rid for rid in pins if logical(live[rid]) != logical(expected[rid])]
    catalog_before = {r['code']: r for r in review['catalog_before']}
    report = dict(
        policy='DISPLAY_NAME_BATCH_B',
        root_cause=('The 4121 -> 4050 -> 4055 display-name chain: 4121 (Onion shallot, scallion, '
                    'pickled with salt) carried 4050\'s Vietnamese name and 4050 (Bamboo shoot, '
                    'fermented, raw) carried 4055\'s, so nine aliases and 117 rows resolved onto '
                    'the wrong identity and măng chua ớt had no retrieval head to reach.'),
        rows_repaired=EXPECTED_ROWS, rows_pending=len(changed_now), recipes_affected=EXPECTED_RECIPES,
        catalog_count=750,
        catalog_diff={c: {k: {'before': catalog_before[c][k], 'after': v} for k, v in patch.items()}
                      for c, patch in CATALOG_PATCHES.items()},
        catalog_subphrase_heads=heads,
        alias_diff={k: {'before': review['aliases_before'][k], 'after': v}
                    for k, v in sorted(ALIAS_PATCHES.items())},
        alias_keeps=ALIAS_KEEPS, alias_map_size=len(new_aliases),
        populations=populations, corpus_nulls=corpus_nulls,
        combined_nutrition=combined, base_117_nutrition=base_report,
        review_estimate_nutrition_delta=REVIEW_ESTIMATE_NUTRITION_DELTA,
        recipe_status=status, canonical=canonical,
        canonical_id_drift=0, representative_drift=0,
        known_route_divergence=KNOWN_ROUTE_DIVERGENCE,
        affected_recipe_ids=sorted(recipes_affected),
        row_outcomes={rid: dict(cohort=pins[rid]['cohort'], before=pins[rid]['before'], after=expected[rid])
                      for rid in ordered},
        cohorts={}, exclusions=EXCLUSIONS)
    report[DEFERRAL_KEY] = dict(DEFERRAL, measured=deferral)
    recipe_before, recipe_after = index(recipes_json), index(new_recipes_json)
    report['recipe_outcomes'] = {rid: {'before': recipe_before[rid], 'after': recipe_after[rid]}
                                 for rid in sorted(recipes_affected)}
    for cohort, (source, target, _count) in COHORTS.items():
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        report['cohorts'][cohort] = dict(
            source_code=source, target_code=target, row_count=len(ids),
            recipe_count=len({expected[rid]['recipe_id'] for rid in ids}), row_ids=ids,
            nutrition=nutrient_report([pins[rid]['before'] for rid in ids], [expected[rid] for rid in ids]))
    return files, before_files, report


def deferred_kieu_state(rows, aliases, catalog):
    """Prove the 4121/20077 deferral held, measured rather than asserted."""
    require(catalog['20077']['name_vi'] == DEFERRAL['preserved']['catalog_name_vi'], '20077 renamed')
    on_20077 = [r for r in rows if (r['master_ingredient_code'] or '') == '20077']
    require(len(on_20077) == DEFERRAL['preserved']['rows'], f'20077 population drift: {len(on_20077)}')
    targeting = sorted(k for k, v in aliases.items() if v == '20077')
    require(len(targeting) == DEFERRAL['preserved']['aliases'], f'20077 alias drift: {len(targeting)}')
    unmatched = [r for r in rows if r['match_method'] == 'UNMATCHED'
                 and 'kiệu' in normalize_vietnamese_text(f"{r['raw_text']} {r['cleaned_name']}")]
    require(len(unmatched) == EXPECTED_UNMATCHED_KIEU_ROWS, f'Deferred kiệu row drift: {len(unmatched)}')
    require(all(not (r['master_ingredient_code'] or '').strip() and r['match_confidence'] in (None, '')
                and all(r[f] in (None, '') for f in NUTRIENTS) for r in unmatched),
            'Deferred kiệu row violates the UNMATCHED contract')
    return {'rows_on_20077': len(on_20077), 'aliases_on_20077': targeting,
            'unmatched_kieu_rows': len(unmatched),
            'unmatched_kieu_row_ids': sorted(r['id'] for r in unmatched)}


def replay(matcher):
    """Every reviewed identity, on both the single and batched route."""
    result = {}
    batch = matcher.match_batch(list(PROBES), raw_contexts=list(PROBES))
    for (query, code), batched in zip(PROBES.items(), batch):
        single = matcher.match(query, raw_context=query)
        for value in (single, batched):
            require((value['matched_item'] or {}).get('code') == code, f'Matcher replay failed: {query}: {value}')
        result[query] = {'code': code, 'single_method': single['method'], 'batch_method': batched['method'],
                         'single_confidence': single['confidence'], 'batch_confidence': batched['confidence']}
    # The reviewed recovery verdict is measured here, not assumed by the manifest.
    recovery = result[RECOVERY_QUERY]
    require(recovery['code'] == RECOVERY_MATCH['code']
            and recovery['single_method'] == recovery['batch_method'] == RECOVERY_MATCH['method']
            and recovery['single_confidence'] == recovery['batch_confidence'] == RECOVERY_MATCH['confidence'],
            f'Reviewed recovery verdict not reproduced: {recovery}')
    # Pre-existing divergence stays pre-existing and stays unfixed.
    divergence = {}
    for query, pinned in KNOWN_ROUTE_DIVERGENCE.items():
        single = matcher.match(query, raw_context=query)
        batched = matcher.match_batch([query], raw_contexts=[query])[0]
        observed = {'single': (single['matched_item'] or {}).get('code'),
                    'batch': (batched['matched_item'] or {}).get('code')}
        require(observed == {'single': pinned['single_after'], 'batch': pinned['batch']},
                f'Route divergence drift outside the reviewed set: {query}: {observed}')
        divergence[query] = dict(pinned, observed=observed, still_divergent=observed['single'] != observed['batch'])
    require(all(d['still_divergent'] for d in divergence.values()), 'Batch B silently fixed a deferred divergence')
    return result, divergence


def write_report(report, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'applied_fix.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = ['# Display-name corruption repair, Batch B', '',
             f"Policy: DISPLAY_NAME_BATCH_B. {report['rows_repaired']} ingredient rows "
             f"/ {report['recipes_affected']} source recipes.", '',
             'The 4121 → 4050 → 4055 chain. Only `name_vi` changes in the catalog: codes, `name_en`, '
             'categories and all nutrition columns are untouched, and each replacement is the identity '
             "the row's own `name_en` already asserts. 4055 is Batch A's repair and is not modified here.", '',
             '## Exact catalog changes', '', '| Code | Field | Before | After | name_en (unchanged) | Subphrase head |',
             '|---|---|---|---|---|---|']
    for code, fields in report['catalog_diff'].items():
        for field, change in fields.items():
            lines.append(f"| {code} | {field} | {change['before']} | {change['after']} | "
                         f"{report['catalog_name_en'][code]} | `{report['catalog_subphrase_heads'][code]}` |")
    lines += ['', 'The punctuation is reviewed. The matcher indexes '
              '`normalize_vietnamese_text(name_vi.split(",")[0])` as a subphrase retrieval head, so the '
              'comma in 4050 publishes `măng chua` — which is exactly what recovers `Măng chua ớt 500 gr` '
              'at SUBPHRASE_CATALOG_MATCH 0.95. 4121 is deliberately comma-less: a raw `Kiệu, muối` would '
              'publish a bare `kiệu` head and hand every ambiguous kiệu row a 0.95 match onto a pickle '
              'identity nobody reviewed.', '',
              '## Exact alias changes', '', f"Alias map size {report['alias_map_size']} (unchanged; "
              'nothing added, nothing removed).', '', '| Alias | Before | After |', '|---|---|---|']
    for alias, change in report['alias_diff'].items():
        lines.append(f"| {alias} | {change['before']} | {change['after']} |")
    lines += ['', 'Reviewed aliases that were always correct against `name_en` and stay put: ' +
              ', '.join(f'`{k}` → {v}' for k, v in report['alias_keeps'].items()) + '.', '',
              'All 11 aliases targeting 20077 are unchanged.', '',
              '## Processed rows and nutrition', '',
              'Nutrition sums include known values only; missing values remain null. Exact before/after records '
              f"for all {report['rows_repaired']} ingredient rows and {report['recipes_affected']} recipes are in "
              '[applied_fix.json](applied_fix.json).', '',
              '| Cohort | Source | Target | Rows | Recipes | kcal delta | Protein delta | Fat delta | Carbs delta |',
              '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for name, c in report['cohorts'].items():
        lines.append(f"| {name} | {c['source_code'] or 'UNMATCHED'} | {c['target_code']} | {c['row_count']} | "
                     f"{c['recipe_count']} | " + ' | '.join(c['nutrition'][f]['known_sum_delta'] for f in NUTRIENTS) + ' |')
    lines += ['', '| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |', '|---|---:|---:|---:|---:|']
    for field, n in report['combined_nutrition'].items():
        lines.append(f"| {field} | {n['before_known_sum']} | {n['after_known_sum']} | {n['known_sum_delta']} | "
                     f"{n['before_null_count']} → {n['after_null_count']} |")
    base = report['base_117_nutrition']
    lines += ['', 'The 117 identity remaps alone: ' +
              ', '.join(f"{f} {base[f]['known_sum_delta']}" for f in NUTRIENTS) +
              ', with no null transition in either direction. The recovery of 545ef564 supplies the whole '
              'null → value movement (calories, protein and carbs each 1 → 0); `fat_g` stays null on all 118 '
              'rows because neither 4050 nor 4055 carries a fat value, and missing fat is never coerced to zero.', '',
              '### Divergence from the pre-implementation review estimate', '',
              'The review estimated `carbs_g` ' +
              report['review_estimate_nutrition_delta']['base_117']['carbs_g'] + ' for the base 117 and ' +
              report['review_estimate_nutrition_delta']['total_118']['carbs_g'] + ' in total. The measured '
              'figures are ' + base['carbs_g']['known_sum_delta'] + ' and ' +
              report['combined_nutrition']['carbs_g']['known_sum_delta'] + '. ' +
              report['review_estimate_nutrition_delta']['cause'] +
              ' calories, protein and fat match the estimate exactly. The measured values are pinned because '
              'they are what `nlp.nutrition.scale_nutrition` — and therefore the live corpus — actually produces.', '',
              'Corpus-wide null counts after: ' + json.dumps(report['corpus_nulls']) + '.', '',
              'Recipe rollups: ' + json.dumps(report['recipe_status'], ensure_ascii=False) + '.', '',
              '## Final populations', '', '| Code | Rows |', '|---|---:|']
    for code, count in report['populations'].items():
        lines.append(f'| {code} | {count} |')
    lines += ['', '## Matcher replay', '', '| Query | Code | Single route | Batch route |', '|---|---|---|---|']
    for query, result in report.get('matcher_replay', {}).items():
        lines.append(f"| {query} | {result['code']} | {result['single_method']} {result['single_confidence']} "
                     f"| {result['batch_method']} {result['batch_confidence']} |")
    if report.get('route_divergence'):
        lines += ['', 'Pre-existing `match()` / `match_batch()` divergence, deliberately not fixed:', '',
                  '| Query | Single before | Single after | Batch | Still divergent |', '|---|---|---|---|---|']
        for query, d in report['route_divergence'].items():
            lines.append(f"| {query} | {d['single_before']} | {d['single_after']} | {d['batch']} | "
                         f"{'yes' if d['still_divergent'] else 'no'} |")
        lines += ['', 'Bare `kiệu` changes which code its single route reaches (4101 → 4121) because `Kiệu muối` '
                  'is now a subphrase head, but it stays divergent from the batch route and no stored row moves '
                  'for it. Both queries remain reviewed deferrals.']
    deferral = report[DEFERRAL_KEY]
    lines += ['', '## 4121 vs 20077 — ' + deferral['status'], '',
              f"`{DEFERRAL_KEY} = {deferral['status']}`", '',
              '- **4121 raw authority.** ' + deferral['4121_raw_authority'],
              '- **20077 authored provenance.** ' + deferral['20077_authored_provenance'],
              '- **Preparation ambiguity.** ' + deferral['preparation_ambiguity'],
              '- **Nutrition difference.** ' + deferral['nutrition_difference'],
              '- **Why no automatic merge.** ' + deferral['reason_no_automatic_merge'], '',
              'Verified preserved: ' + json.dumps(
                  {k: v for k, v in deferral['measured'].items() if k != 'unmatched_kieu_row_ids'},
                  ensure_ascii=False) + '.', '',
              '## Canonical propagation', '', '| Artifact | Changed logical records |', '|---|---:|']
    for name, values in report['canonical'].items():
        lines.append(f"| {name} | {values['changed_count']} |")
    mapping = report['canonical'].get('recipe_canonical_mapping.csv', {})
    lines += ['', f"Mapping rows belonging to the {report['recipes_affected']} affected recipes: "
              f"{mapping.get('mapping_rows_for_affected_recipes')}, spanning "
              f"{mapping.get('canonical_groups_involved')} canonical groups; only "
              f"{mapping.get('changed_count')} changes content, because the 117 identity remaps swap one valid "
              'code for another and move no quality counter. Canonical ID drift = 0; representative drift = 0.', '',
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
            require(hashlib.sha256(cache.read_bytes()).hexdigest() == previous['embeddings']['sha256'],
                    'Embedding cache drift')
            require(embedding_input_digest(files[CAT]) == previous['embeddings']['input_sha256'],
                    'Embedding catalog-input drift')
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
    require(list(tensor.shape) == [750, 768] and len(matcher.catalog) == 750, f'Embedding shape drift: {tensor.shape}')
    require(torch.equal(tensor, matcher.catalog_embeddings), 'Cache differs from generated embeddings')
    digest = hashlib.sha256(cache.read_bytes()).hexdigest()
    matcher.catalog_embeddings = None
    matcher._compute_catalog_embeddings()
    require(torch.equal(tensor, matcher.catalog_embeddings)
            and hashlib.sha256(cache.read_bytes()).hexdigest() == digest, 'Cache not reusable')
    report['embeddings'] = dict(rebuilt=True, tracked=False, shape=list(tensor.shape), sha256=digest,
                                next_load_equal=True, input_sha256=embedding_input_digest(matcher.catalog),
                                build_inputs={r['code']: f"{r['name_vi']} ({r['category_vi']})"
                                              for r in matcher.catalog if r['code'] in CATALOG_PATCHES})
    report['matcher_replay'], report['route_divergence'] = replay(matcher)
    # Canonical regeneration runs only after the processed rows verify.
    require(plan(root)[2]['rows_pending'] == 0, 'Processed repair failed read-back')
    report['rows_pending'] = 0  # The report describes the applied state, not the plan.
    for command in (['scripts/canonicalize_recipes.py'], ['scripts/export_canonical_json.py']):
        subprocess.run([sys.executable, *command], cwd=root, check=True)
    verify_canonical(root)
    require(interim_before == {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (root/'data/interim').rglob('*') if p.is_file()},
            'Historical/interim data changed')
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
    require(len(aliases_before) == len(aliases_after) == ALIAS_MAP_SIZE, 'Alias map size changed vs HEAD')
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
                      if k not in ('row_outcomes', 'recipe_outcomes', 'affected_recipe_ids',
                                   'matcher_replay', 'cohorts')},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
