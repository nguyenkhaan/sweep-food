"""DISPLAY_NAME_BATCH_C1: reviewed 345-row / 333-recipe repair; dry-run by default.

Catalog code 4016 is the raw Viện Dinh Dưỡng row `Mustard greens, raw`, but its
Vietnamese display name reads `Dưa chuột (dưa leo)` -- cucumber -- which is
4027's identity, and 4027 already carries `Dưa chuột`. Two codes therefore
published one vegetable, and the one that published it wrongly is the one the
alias map leaned on: three cucumber alias keys and 248 processed cucumber rows
were organised around 4016 as if it were a cucumber, while the genuine mustard
greens sat on 4011 `Cải bắp đỏ` (red cabbage) and 4015 `Cải thìa (cải trắng)`
(bok choy), and five more sat stored-UNMATCHED.

The repair is `name_vi` only: 4016 becomes `Cải xanh`. Code, `name_en`, both
category columns and every nutrition column are asserted byte-for-byte
unchanged, so the identity being published is the one the source row already
asserts and no nutrition is restated by the rename itself.

`Cải bẹ trắng (cải thìa/thảo)` is deliberately NOT the chosen name.
`_QWEN_MAPPER_RULES` carries a disabled rule
`(("cải con", "cải mầm", "cải thìa"),) -> 4016 "Cải bẹ trắng (cải thìa/thảo)"`,
and build_mapper_rules() reactivates a rule the moment the catalog's live
`name_vi` equals the hard-coded name. That exact string would switch a Qwen
rule back on as a side effect of a display-name repair, and would re-publish
the bok-choy/napa identity this batch is removing from 4016. `Cải xanh` states
the mustard-green identity the row's own `name_en` asserts, leaves the two
pre-existing colliding display names untouched, and keeps the Qwen mapper at
29 active / 20 disabled with that rule still disabled. The batch asserts all
three, before and after.

The alias plan is exactly 20 actions. Three cucumber keys (`dưa leo`, `ăn kèm
dưa leo`, `dưa leo cắt sợi`) are repointed off 4016 onto 4027, where their own
words already pointed. Seven mustard-green keys (`cải xanh`, `cải bẹ xanh`,
`rau cải xanh`, `rau cải bẹ xanh`, `ăn kèm cải bẹ xanh`, `cải canh`, `cải bẹ`)
are repointed off red cabbage 4011 onto the repaired 4016. Six narrow
mustard-green keys are added, including one long parser-damaged key that
corresponds to exactly one reviewed row; `lá cải thảo` -> 4109 and `kimchi cải
thảo` -> 20034 are added for the napa and kimchi rows. Two keys are removed
outright (`cải cải bó xôi`, `cải xoăn`): spinach and kale have no catalog
identity at all, and 4016 was never one. 4674 - 2 + 8 = 4680. Generic `cải` ->
4013, `cải trắng` -> 4021, the `cải thìa` family and every 4094 key are
asserted unchanged, and NO NEW ALIAS TARGETS 4094.

345 rows change identity and 10 more only refresh a stale display name, all
pinned by id with a complete before record and never selected by code alone.
248 cucumber rows go to 4027, 40 genuine mustard-green rows come back from
4011 and five more from 4015, five stored-UNMATCHED mustard rows are recovered,
eight fresh napa rows go to 4109 and two kimchi rows to 20034. One row moves to
4010 and one to 4115 as reviewed non-reproducible corrections, and 35 rows are
cleared to UNMATCHED.

The 35 clears are the batch's centre of gravity, not its residue. 27 spinach
and four kale rows are cleared because no spinach or kale identity exists in
the catalog at all; removing their aliases would merely hand them to 4010 via
BERT, so the clears are ID-pinned and the fallthrough is recorded rather than
adopted. Three rows whose cleaned text collides with the new `Cải xanh` head
(two broccoli, one mizuna) are cleared for the same reason, and no alias is
added to 4094 to catch them. The 36th candidate, `1 muỗng cải thảo muối khô`,
was deferred by the audit and is CLEARED here by explicit reviewer decision:
its semantic identity is dried salted napa, no exact catalog identity exists,
and the repaired 4016 is definitely wrong, so AGENTS.md section 2's preference
for UNMATCHED over a known-wrong identity applies. That single change is why
every figure the audit quoted -- changed rows, clears, final 4016 population,
UNMATCHED count, nutrition delta, canonical radius and Qwen audit counts -- is
re-measured here rather than carried forward.

Blast radius is measured against the manifest-reconstructed before state, never
against git HEAD: a version-control diff is only an invariant while the batch is
unstaged and inverts the moment it lands. --apply writes catalog, aliases, the
downstream cucumber hard-code, processed rows and rollups in that order,
rebuilds the untracked embedding cache, replays the real matcher in production
shape, exports canonical CSV/JSON and runs canonical --check. A completed rerun
writes nothing.
"""

import argparse
from copy import deepcopy
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from nlp.entity_matcher import VietnameseIngredientMatcher, normalize_vietnamese_text
from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition
from nlp.qwen_matching import (
    _QWEN_MAPPER_RULES, _REVIEWED_NO_CATALOG_TARGET_RAW, build_mapper_rules,
    map_clean_to_master, qwen_candidate_eligibility,
)
from scripts.eda.apply_qwen_safe_fix import (
    read_csv, read_json, write_json, recompute_recipe_rollups, _apply_rollups, _new_totals,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
from scripts.canonicalize_recipes import compose_reviewed_aliases

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('display_name_batch_c1_reviewed_state.json')
OUT = ROOT / 'reports/eda/display_name_batch_c1_fix'
CAT = Path('data/processed/viendinhduong/master_ingredients_nutrition.csv')
ALIASES = CAT.with_name('ingredient_alias_map.json')
DATA = Path('data/processed/recipes')
NUTRIENTS = ('calories', 'protein_g', 'fat_g', 'carbs_g')

# name_vi only. 4016's name_en is `Mustard greens,   raw` (the source row's own
# internal spacing, preserved byte-for-byte); the display name it carries today
# describes 4027 `Cucumber, raw`, which still holds `Dưa chuột`.
CATALOG_PATCHES = {'4016': {'name_vi': 'Cải xanh'}}
CATALOG_NAME_VI_BEFORE = 'Dưa chuột (dưa leo)'
CATALOG_NAME_VI_AFTER = 'Cải xanh'
CATALOG_NAME_EN = 'Mustard greens,   raw'
# The name the repair must NOT use, and why. `_QWEN_MAPPER_RULES` carries a
# disabled rule ("cải con", "cải mầm", "cải thìa") -> 4016
# "Cải bẹ trắng (cải thìa/thảo)"; build_mapper_rules() reactivates a rule as
# soon as the live catalog name_vi equals the hard-coded name, so this exact
# string would switch a Qwen rule back on as a side effect of a rename -- and
# would republish the bok-choy/napa identity this batch removes from 4016.
FORBIDDEN_CATALOG_NAME = 'Cải bẹ trắng (cải thìa/thảo)'
QWEN_RULE_MUST_STAY_DISABLED = (('cải con', 'cải mầm', 'cải thìa'), '4016',
                                'Cải bẹ trắng (cải thìa/thảo)')
EXPECTED_QWEN_RULE_COUNTS = {'active': 29, 'disabled': 20}
# Catalog display names that already collide and stay deferred. C1 neither adds
# to nor removes from this set: `Cải xanh` is unique in the catalog after the
# rename, and `Dưa chuột (dưa leo)` was never a duplicate of `Dưa chuột`.
EXPECTED_DUPLICATE_NAMES = {'nấm kim châm', 'thịt trâu, đùi'}

# --- the 20 reviewed alias actions -----------------------------------------
# A. Three cucumber keys off 4016 onto 4027, and seven mustard-green keys off
#    red cabbage 4011 onto the repaired 4016.
ALIAS_REPOINTS = {
    'dưa leo': '4027', 'ăn kèm dưa leo': '4027', 'dưa leo cắt sợi': '4027',
    'cải xanh': '4016', 'cải bẹ xanh': '4016', 'rau cải xanh': '4016',
    'rau cải bẹ xanh': '4016', 'ăn kèm cải bẹ xanh': '4016', 'cải canh': '4016',
    'cải bẹ': '4016',
}
# B. Two keys with no catalog identity behind them at all. Spinach (`cải bó
#    xôi`) and kale (`cải xoăn`) are absent from the 750-row catalog; 4016 was
#    never either of them, before or after the rename.
ALIAS_REMOVALS = ('cải cải bó xôi', 'cải xoăn')
# C. Six narrow mustard-green keys the repaired identity earns, plus the napa
#    leaf and kimchi keys. `cải bẹ xanh 1 2cm để riêng phần cọng và lá` is
#    deliberate and deliberately long: it is the parser-damaged cleaned text of
#    exactly one reviewed row (fb5b5853), and a broad generic key in its place
#    would claim rows nobody reviewed.
ALIAS_ADDITIONS = {
    'lá cải xanh': '4016', 'rau cải canh': '4016', 'cải bẹ xanh con': '4016',
    'cải bẹ xanh nhỏ': '4016', 'cải bẹ xanh to': '4016',
    'cải bẹ xanh 1 2cm để riêng phần cọng và lá': '4016',
    'lá cải thảo': '4109', 'kimchi cải thảo': '20034',
}
LONG_REVIEWED_ALIAS = 'cải bẹ xanh 1 2cm để riêng phần cọng và lá'
LONG_REVIEWED_ALIAS_ROW = 'fb5b5853'
# D. Reviewed keeps: valid today, valid after, and asserted both times. Generic
#    `cải` -> 4013, `cải trắng` -> 4021, the whole `cải thìa` family and every
#    4094 key are listed deliberately -- this batch must prove it left them alone.
ALIAS_KEEPS = {
    'cải xanh tươi': '4016',
    'cải thảo': '4109', 'rau cải thảo': '4109',
    'kim chi cải thảo': '20034', 'cải thảo kim chi': '20034',
    'cải thìa': '4135',
    'dưa chuột': '4027', 'dưa chuột tươi': '4027',
    'dưa chuột muối': '4118', 'dưa leo baby': '4034', 'dưa cải bẹ': '4116',
    'cải': '4013', 'cải trắng': '4021', 'cải mầm': '20050', 'mầm cải': '20050',
    'bông cải xanh': '4094', 'bông cải xanh cắt nhỏ': '4094',
    'ăn kèm bông cải xanh': '4094', 'súp lơ': '4094',
}
EXPECTED_ALIAS_ACTIONS = 20
ALIAS_MAP_SIZE_BEFORE = 4674
ALIAS_MAP_SIZE_AFTER = 4680
# C3 adds four narrow cabbage aliases; C1 own arithmetic stays above.
ALIAS_MAP_SIZE_LIVE = 4684
# Explicit invariant: 4094 `Súp lơ (bông cải xanh)` is itself display-name
# corrupted (its name_en is `Mint leaves, raw`) and is C4's problem. The three
# rows this batch clears would otherwise be candidates for it. No alias action
# in this batch may target 4094.
NO_NEW_ALIAS_TO = '4094'

# cohort -> (source code or None for UNMATCHED, target code or None for a clear,
#            reviewed row count, provenance policy)
COHORTS = {
    'cucumber_4016_to_4027': ('4016', '4027', 248, 'preserved'),
    'mustard_alias_4011_to_4016': ('4011', '4016', 35, 'preserved'),
    'mustard_exact_4011_to_4016': ('4011', '4016', 5, 'measured'),
    'mustard_leaf_4015_to_4016': ('4015', '4016', 5, 'measured'),
    'mustard_unmatched_recovery_to_4016': (None, '4016', 5, 'measured'),
    'green_cabbage_4011_to_4010': ('4011', '4010', 1, 'preserved'),
    'fresh_napa_4016_to_4109': ('4016', '4109', 8, 'measured'),
    'salted_napa_4016_to_4115': ('4016', '4115', 1, 'preserved'),
    'kimchi_4016_to_20034': ('4016', '20034', 2, 'measured'),
    'spinach_clear_to_unmatched': ('4016', None, 27, 'cleared'),
    'kale_clear_to_unmatched': ('4016', None, 4, 'cleared'),
    'collision_clear_to_unmatched': ('4015', None, 3, 'cleared'),
    'dried_salted_napa_clear_to_unmatched': ('4016', None, 1, 'cleared'),
    # Not a changed row: code and nutrition are byte-identical and only the stale
    # stored display name is refreshed.
    'residual_qwen_keep_4016': ('4016', '4016', 10, 'name_refresh'),
}
NAME_REFRESH_COHORT = 'residual_qwen_keep_4016'
EXPECTED_ROWS = 355
EXPECTED_CHANGED_ROWS = 345
EXPECTED_NAME_REFRESH_ROWS = 10
EXPECTED_RECIPES = 340
EXPECTED_CHANGED_ROW_RECIPES = 333
EXPECTED_CLEARS = 35
# Matcher replay classes over the 345 changed rows: 308 reproduce exactly, two
# are reviewed non-reproducible repairs and 35 are curated clears the matcher
# would claim. 308 + 2 + 35 = 345.
EXPECTED_REPRODUCIBLE_ROWS = 308
EXPECTED_CURATED_DIVERGENCE_ROWS = 2

# The single reviewer decision that supersedes every figure the audit quoted.
DRIED_SALTED_NAPA_ROW = '2c660d89'
DRIED_SALTED_NAPA_RAW = '1 muỗng cải thảo muối khô'
REVIEWER_OVERRIDE = {
    'row': DRIED_SALTED_NAPA_ROW, 'raw_text': DRIED_SALTED_NAPA_RAW,
    'audit_disposition': 'DEFER on repaired 4016',
    'reviewed_disposition': 'CLEAR_TO_UNMATCHED',
    'reason': ('Semantic identity is dried salted napa. No exact catalog identity exists, and '
               'the repaired 4016 is fresh mustard greens, so keeping the row on 4016 would '
               'knowingly preserve a wrong identity. AGENTS.md section 2 prefers UNMATCHED to a '
               'known-wrong target, so the audit deferral is superseded by an explicit clear.'),
    'consequences': ('Changed rows 344 -> 345, clears 34 -> 35, final 4016 population 61 -> 60, '
                     'UNMATCHED 8498 -> 8499, one more corpus null per nutrient, one fewer '
                     'QWEN_LLM_MATCH row, and a macro delta that is no longer the audit figure.'),
}
# The audit's pre-override macro delta, recorded so the difference is auditable
# rather than asserted. Superseded: it did not clear 2c660d89.
SUPERSEDED_AUDIT_NUTRITION_DELTA = {
    'calories': '-6697.3', 'protein_g': '-377.8', 'fat_g': '-26.2', 'carbs_g': '-1218.5',
}
# The two reviewed non-reproducible identity repairs, pinned by exact id and raw
# text with the matcher verdict they knowingly diverge from.
GREEN_CABBAGE_ROW = '633ea6e1'
GREEN_CABBAGE_RAW = 'Bắp cải xanh 1/2 cái'
SALTED_NAPA_ROW = '89749d54'
SALTED_NAPA_RAW = 'Cải thảo muối 100 gr'
# Reviewed rows that this batch deliberately does not change.
KEEP_CURRENT_ROW = 'e9b2ce8d'
KEEP_CURRENT_CODE = '20086'
CURATED_UNMATCHED_ROW = '6ce0333f'

# C3 repaired parser-damaged white-cabbage rows; own reviewed row sets remain unchanged.
EXPECTED_POPULATIONS = {
    '4010': 105, '4011': 0, '4015': 11, '4016': 60, '4027': 270, '4109': 73, '4115': 1,
    '20034': 75,
    # Siblings this batch must not disturb: 4094 (itself corrupted, C4's), the
    # bok-choy duplicate 4135, C2's repaired identities, C3's codes and the
    # okra identity the KEEP_CURRENT row sits on.
    '4094': 106, '4135': 59, '4018': 177, '20035': 33, '4013': 54, '4021': 128,
    '20086': 101,
    'UNMATCHED': 8495,
}
# Measured over the reviewed 345 changed rows. The 10 name-refresh rows move no
# nutrient at all, so the 355-row figure is identical.
EXPECTED_NUTRITION_DELTA = {
    'calories': '-6700.7', 'protein_g': '-378.1', 'fat_g': '-26.2', 'carbs_g': '-1219.1',
}
EXPECTED_COHORT_NUTRITION_DELTA = {
    'collision_clear_to_unmatched': {
        'calories': '-43.2', 'protein_g': '-2.5', 'fat_g': '-0.3', 'carbs_g': '-7.6'},
    'cucumber_4016_to_4027': {
        'calories': '-1282.5', 'protein_g': '-237.9', 'fat_g': '-5.0', 'carbs_g': '-41.9'},
    'dried_salted_napa_clear_to_unmatched': {
        'calories': '-3.4', 'protein_g': '-0.3', 'fat_g': '0.0', 'carbs_g': '-0.6'},
    'fresh_napa_4016_to_4109': {
        'calories': '-490.0', 'protein_g': '-43.6', 'fat_g': '-7.6', 'carbs_g': '-64.8'},
    'green_cabbage_4011_to_4010': {
        'calories': '-6.2', 'protein_g': '0.0', 'fat_g': '-0.1', 'carbs_g': '-1.5'},
    'kale_clear_to_unmatched': {
        'calories': '-218.5', 'protein_g': '-16.1', 'fat_g': '-1.3', 'carbs_g': '-35.8'},
    'kimchi_4016_to_20034': {
        'calories': '-5.0', 'protein_g': '-0.4', 'fat_g': '0.2', 'carbs_g': '-1.4'},
    'mustard_alias_4011_to_4016': {
        'calories': '-3275.6', 'protein_g': '-16.8', 'fat_g': '-5.6', 'carbs_g': '-796.3'},
    'mustard_exact_4011_to_4016': {
        'calories': '-421.8', 'protein_g': '-2.1', 'fat_g': '-0.8', 'carbs_g': '-102.6'},
    'mustard_leaf_4015_to_4016': {
        'calories': '-33.2', 'protein_g': '9.9', 'fat_g': '0.0', 'carbs_g': '-16.6'},
    'mustard_unmatched_recovery_to_4016': {
        'calories': '108.1', 'protein_g': '8.0', 'fat_g': '0.6', 'carbs_g': '17.8'},
    # Code unchanged and catalog nutrition unchanged, so the display-name refresh
    # moves nothing. Asserted, not narrated.
    'residual_qwen_keep_4016': {
        'calories': '0.0', 'protein_g': '0.0', 'fat_g': '0.0', 'carbs_g': '0.0'},
    'salted_napa_4016_to_4115': {
        'calories': '1.0', 'protein_g': '-0.5', 'fat_g': '-0.1', 'carbs_g': '1.1'},
    'spinach_clear_to_unmatched': {
        'calories': '-1030.4', 'protein_g': '-75.8', 'fat_g': '-6.2', 'carbs_g': '-168.9'},
}
# 35 clears take four values to null each; the five UNMATCHED recoveries take
# four nulls to a value each. fat_g moves nine further values to null, and those
# nine are real missing catalog data, not a coerced zero: 4109 `Rau cải thảo`
# and 4115 `Dưa cải bắp` publish no fat_g column at all, so the eight fresh-napa
# rows and the one salted-napa row correctly store null fat (AGENTS.md section 9).
EXPECTED_NULL_TRANSITIONS = {
    'calories': (5, 35), 'protein_g': (5, 35), 'fat_g': (5, 44), 'carbs_g': (5, 35),
}
EXPECTED_VALUE_TO_NULL = {'calories': 35, 'protein_g': 35, 'fat_g': 44, 'carbs_g': 35}
EXPECTED_NULL_TO_VALUE = {f: 5 for f in NUTRIENTS}
FAT_NULL_TARGETS = ('4109', '4115')
EXPECTED_FAT_NULL_FROM_MISSING_TARGET = 9
EXPECTED_CORPUS_NULLS = {
    'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454,
}

EXPECTED_MISSING_COUNT_TRANSITIONS = {
    '1255416d-3473-4ff9-bd9e-9e397343fb4b': (5, 6),
    '125b927e-89b6-43a5-9882-8a7cf13a5d98': (5, 6),
    '155ea08c-0452-445d-ad1f-01ca91ad8a11': (2, 3),
    '1882f6c3-8b09-4157-9113-a906672819ed': (7, 8),
    '1d9af8a2-4382-4d61-b56d-04a832862c08': (1, 2),
    '2625c011-4f68-4035-800b-7a1f6c9dcd62': (5, 4),
    '33721267-1134-4123-9229-a9da95aba9ee': (1, 2),
    '49cd7c7f-0488-4d01-80de-d8dfec43ab84': (0, 1),
    '4c223d52-f837-4cb7-bada-cbc33bab15a6': (3, 4),
    '5a0cca89-e457-418d-9217-02a63a629e8d': (1, 2),
    '5dfa1739-0a8e-4326-80d5-2a591dbbfdb2': (2, 3),
    '6589b994-855b-40a5-8668-152b79d69cc0': (2, 3),
    '6b73fcd3-70e8-4ebe-ae60-46be7e57969a': (0, 1),
    '78c77620-8392-40c2-9bf0-94129192a7be': (1, 2),
    '8042eedb-1093-4231-aabf-d74d0c3c3573': (3, 2),
    '8e8a668d-205e-4827-a57a-c788a9ac0852': (3, 2),
    '915e9f5f-2189-4a3b-9669-66107237237d': (0, 1),
    '917bcbe4-8321-4c3b-9bb7-87fd62561e3a': (2, 3),
    '9afefa30-149e-43b1-806f-2e69edb2bcec': (1, 2),
    '9c30c0bb-b2cb-443a-8833-12fd1d8a6780': (0, 1),
    'ab161f92-9f5c-4f34-8531-0cc612cab27c': (0, 1),
    'acf2949d-806f-472e-a05b-acbc181da061': (1, 2),
    'ae3d7c77-804a-4d26-95a1-ca30acf64b21': (2, 3),
    'beaa0c12-0a00-468e-acbc-4d08faa69f68': (0, 1),
    'c0c5ff0f-7666-4fef-86d7-dfd968b8a8a3': (1, 2),
    'ca611bdf-c7cd-4d4d-8c6f-68dc77a9dda6': (1, 0),
    'cf7d529c-1ea6-4f0c-a19a-53c39438a9d1': (2, 3),
    'd0440fb9-e2a8-4029-8eed-9009278147af': (0, 1),
    'd354782b-0879-4547-ab59-3ceed8b5db87': (0, 1),
    'da6c59b2-0f2b-4f68-a0bb-ef796bcb572b': (6, 8),
    'dac42905-9e77-48ff-9093-ba205035113c': (0, 1),
    'e22addbe-be2b-4462-a9ea-9ad6934b3c19': (1, 0),
    'ea85273a-4922-4bf8-81d1-3ae779607cf9': (2, 3),
    'ee22497b-ff45-46b1-b287-dc8367f6cd1c': (1, 2),
    'f0e9adf5-d673-4b01-8a81-dcb0e8eb3460': (2, 5),
    'f79f8699-8b4a-4402-b8d3-edb52f117719': (2, 3),
    'ffa23849-019f-4f13-897e-cb58db3fe060': (1, 2),
}
# Unlike C2, C1 does cross label thresholds: 35 clears are enough to push 14
# recipes down a band and the five recoveries pull two back up. Every one is
# measured from the ingredient rows and pinned, none is forced.
EXPECTED_STATUS_LABEL_TRANSITIONS = {
    '155ea08c-0452-445d-ad1f-01ca91ad8a11': 'PARTIAL -> INCOMPLETE',
    '49cd7c7f-0488-4d01-80de-d8dfec43ab84': 'COMPLETE -> PARTIAL',
    '4c223d52-f837-4cb7-bada-cbc33bab15a6': 'PARTIAL -> INCOMPLETE',
    '5a0cca89-e457-418d-9217-02a63a629e8d': 'PARTIAL -> INCOMPLETE',
    '6b73fcd3-70e8-4ebe-ae60-46be7e57969a': 'COMPLETE -> PARTIAL',
    '8042eedb-1093-4231-aabf-d74d0c3c3573': 'INCOMPLETE -> PARTIAL',
    '915e9f5f-2189-4a3b-9669-66107237237d': 'COMPLETE -> PARTIAL',
    '9c30c0bb-b2cb-443a-8833-12fd1d8a6780': 'COMPLETE -> PARTIAL',
    'ab161f92-9f5c-4f34-8531-0cc612cab27c': 'COMPLETE -> PARTIAL',
    'ae3d7c77-804a-4d26-95a1-ca30acf64b21': 'PARTIAL -> INCOMPLETE',
    'beaa0c12-0a00-468e-acbc-4d08faa69f68': 'COMPLETE -> PARTIAL',
    'ca611bdf-c7cd-4d4d-8c6f-68dc77a9dda6': 'PARTIAL -> COMPLETE',
    'd0440fb9-e2a8-4029-8eed-9009278147af': 'COMPLETE -> PARTIAL',
    'd354782b-0879-4547-ab59-3ceed8b5db87': 'COMPLETE -> PARTIAL',
    'dac42905-9e77-48ff-9093-ba205035113c': 'COMPLETE -> INCOMPLETE',
    'e22addbe-be2b-4462-a9ea-9ad6934b3c19': 'PARTIAL -> COMPLETE',
}

EXPECTED_CANONICAL = {
    'canonical_recipe_ingredients.csv': 351,
    'canonical_recipes.csv': 330,
    'recipe_canonical_mapping.csv': 52,
}
# 340 canonical groups are TOUCHED by the 355 pinned rows and 333 by the 345
# changed rows; 330 canonical_recipes.csv rows change content. The gap is the
# ten display-name refreshes: canonical_recipes.csv carries totals, not
# ingredient names, so their recipes are touched without changing content.
EXPECTED_CANONICAL_GROUPS = 340
EXPECTED_CANONICAL_GROUPS_CHANGED_ROWS = 333
# Four reviewed rows live in recipes that canonicalisation deduplicated away, so
# they have no canonical ingredient row: 351 = 355 - 4.
EXPECTED_CANONICAL_INGREDIENT_ROWS_ABSENT = 4
EXPECTED_CANONICAL_TOTALS = {'canonical_recipes.csv': 5479, 'recipe_canonical_mapping.csv': 5641}
EXPECTED_MAPPING_CHANGED_FIELDS = {
    'candidate_score', 'selection_score', 'unmatched_count', 'valid_master_match_count',
    'valid_match_rate', 'qwen_match_count', 'nutrition_anomaly_count',
    'negative_nutrition_anomaly_rate', 'negative_unmatched_rate',
    'negative_recipe_nutrition_anomalies',
}
# The audit quoted 332 recipes / 340 canonical ingredient rows / 329 canonical
# groups / 332 canonical_recipes rows for its 344-row plan. All four are stale:
# the extra clear adds a row, and the audit's canonical figures did not separate
# the ten display-name refreshes from the identity changes. Recorded so the two
# readings can be compared instead of one silently replacing the other.
SUPERSEDED_AUDIT_CANONICAL = {
    'estimate': {'processed_recipes_touched': 332, 'canonical_ingredient_rows': 340,
                 'canonical_groups': 329, 'canonical_recipes_rows': 332,
                 'nutrition_status_transitions': 16},
    'measured': {'processed_ingredient_rows_changed': EXPECTED_CHANGED_ROWS,
                 'processed_rows_written': EXPECTED_ROWS,
                 'processed_recipes_touched': EXPECTED_CHANGED_ROW_RECIPES,
                 'processed_recipes_touched_including_name_refresh': EXPECTED_RECIPES,
                 'canonical_ingredient_rows': EXPECTED_CANONICAL['canonical_recipe_ingredients.csv'],
                 'canonical_groups': EXPECTED_CANONICAL_GROUPS,
                 'canonical_recipes_rows': EXPECTED_CANONICAL['canonical_recipes.csv'],
                 'recipe_canonical_mapping_rows': EXPECTED_CANONICAL['recipe_canonical_mapping.csv'],
                 'recipes_with_changed_missing_count': len(EXPECTED_MISSING_COUNT_TRANSITIONS),
                 'nutrition_status_transitions': len(EXPECTED_STATUS_LABEL_TRANSITIONS)},
}

# --- downstream hard-coded cucumber code ------------------------------------
# One live pantry entry buys `dưa chuột` -- cucumber -- at code 4016, which
# publishes `Mustard greens, raw`. The repaired 4027 is the identity it meant.
DOWNSTREAM_BEFORE = '("dưa chuột", "4016"'
DOWNSTREAM_AFTER = '("dưa chuột", "4027"'
DOWNSTREAM_FILES = {Path('src/recommendation/pantry_simulator.py'): 1}
EXPECTED_DOWNSTREAM_REPOINTS = 1
# Any other live cucumber hard-coding is drift: fail closed rather than repair
# something nobody reviewed.
DOWNSTREAM_SCAN = re.compile(r'\(\s*"(?:dưa chuột|dưa leo)"\s*,\s*"(\d+)"')
DOWNSTREAM_SCAN_ROOT = Path('src')

# --- audit evidence hygiene -------------------------------------------------
# scripts/eda/audit_qwen_matching.py keeps 4016 in its WRONG table: the code is
# still the wrong home for the rows that remain on it. Only the signature moves.
# The display name becomes the repaired one, and the synonym list narrows to the
# cleaned names the ten surviving reviewed rows actually carry. `cải thảo` and
# `lá cải thảo` leave it -- those rows are gone, and the one row that would have
# justified keeping `cải thảo` (2c660d89) is now cleared. `cải thìa chua` is
# deliberately absent: the existing compound/preparation logic already keeps it
# in class B, and widening this regex to catch it would relabel other rows.
AUDIT_WRONG_NAME = 'Cải xanh'
AUDIT_WRONG_SYNONYMS = 'cải con|cải thìa|cải thìa con'
AUDIT_WRONG_REASON = 'Bok-choy and sprout greens versus mustard greens'
AUDIT_RETIRED_SYNONYMS = ('cải thảo', 'lá cải thảo')
EXPECTED_AUDIT = {
    'qwen_rows': 643,
    'class_counts': {'A': 0, 'B': 549, 'C': 55, 'D': 39},
    'class_recipes': {'A': 0, 'B': 513, 'C': 55, 'D': 38},
}
# Pre-C1 audit figures, recorded so the delta is auditable. The audit itself
# quoted these as its post-C1 expectation; they are its measurement of the
# CURRENT corpus, and C1 moves 19 rows out of QWEN_LLM_MATCH.
SUPERSEDED_AUDIT_CLASSES = {'qwen_rows': 662, 'class_counts': {'A': 0, 'B': 568, 'C': 55, 'D': 39}}

# --- protecting the reviewed clear from a future Qwen pass -------------------
# Clearing 2c660d89 made it Qwen-eligible for the first time: it now has no
# master link, and `data/interim/qwen_extracted_map.json` carries a cached output
# for its raw line. Measured against the live pipeline before this was added, the
# recovery block produced a candidate for it -- 4109 `Rau cải thảo`, FRESH napa --
# so a Qwen pass would have silently restated the reviewed clear as a wrong match.
#
# The protection is production logic, not a test: the reviewed raw line is pinned
# in nlp.qwen_matching._REVIEWED_NO_CATALOG_TARGET_RAW and refused by
# qwen_candidate_eligibility(), the guard scripts/run_qwen_line_pipeline.py
# consults before it accepts any candidate. Asserted here so the clear and the
# thing that protects it cannot drift apart.
QWEN_EXCLUSION_RAW = DRIED_SALTED_NAPA_RAW
QWEN_EXCLUSION_REASON = 'DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET'
QWEN_EXCLUSION_WOULD_REACH = '4109'
# Fresh napa must stay recoverable: the guard sits downstream of the 4109 mapper
# rule and may not disturb it.
QWEN_EXCLUSION_MUST_STILL_ALLOW = (
    ('Cải thảo 2 lá', 'cải thảo'), ('Vài lá cải thảo', 'cải thảo'),
    ('3 lá cải thảo', 'lá cải thảo'), ('1 chén kimchi cải thảo', 'kimchi cải thảo'),
)

# The reviewed identities and every sibling that must not move. Asserted on the
# production route -- match_batch(cleaned_name, raw_contexts=raw_text).
PROBES = {
    # Cucumber, repointed by this batch.
    'dưa leo': '4027', 'ăn kèm dưa leo': '4027', 'dưa leo cắt sợi': '4027',
    'dưa chuột': '4027', 'dưa chuột tươi': '4027',
    # Mustard greens, recovered by this batch.
    'cải xanh': '4016', 'cải bẹ xanh': '4016', 'rau cải xanh': '4016',
    'rau cải bẹ xanh': '4016', 'ăn kèm cải bẹ xanh': '4016', 'cải canh': '4016',
    'cải bẹ': '4016', 'lá cải xanh': '4016', 'rau cải canh': '4016',
    'cải bẹ xanh con': '4016', 'cải bẹ xanh nhỏ': '4016', 'cải bẹ xanh to': '4016',
    LONG_REVIEWED_ALIAS: '4016', 'cải xanh tươi': '4016',
    # Napa and kimchi.
    'cải thảo': '4109', 'lá cải thảo': '4109', 'rau cải thảo': '4109',
    'kim chi cải thảo': '20034', 'kimchi cải thảo': '20034', 'cải thảo kim chi': '20034',
    # Siblings that must not move, including every 4094 key and generic `cải`.
    'cải thìa': '4135', 'cải': '4013', 'cải trắng': '4021', 'cải mầm': '20050',
    'mầm cải': '20050', 'bông cải xanh': '4094', 'bông cải xanh cắt nhỏ': '4094',
    'ăn kèm bông cải xanh': '4094', 'súp lơ': '4094', 'dưa chuột muối': '4118',
    'dưa leo baby': '4034', 'dưa cải bẹ': '4116',
    # C2's repaired identities, out of scope here and pinned so they cannot drift.
    'bắp cải': '4010', 'cần tây': '4018', 'bắp cải tím': '20035',
}
# Removing the spinach and kale aliases does not make those phrases unmatched:
# the matcher falls through to the neural stage and lands spinach on 4010
# `Cải bắp trắng` and kale straight back on the repaired 4016 `Cải xanh`.
# Recorded and NOT adopted -- that is precisely why the 31 rows are ID-pinned
# curated clears rather than an alias removal left to define behaviour. The
# kale case is the sharper one: removing the alias would move those four rows
# from a wrong 4016 to the same wrong 4016 by a different route.
#
# These figures are measured against the REBUILT embedding cache. Measuring
# them against the pre-C1 cache gives 4010 for kale, because the cache still
# holds the corrupt `Dưa chuột (dưa leo)` vector at index 4016 -- which is why
# --apply rebuilds the cache before it replays anything.
ALIAS_REMOVAL_FALLTHROUGH = {
    'cải cải bó xôi': {'before': '4016', 'after': '4010', 'stage': 'neural'},
    'cải xoăn': {'before': '4016', 'after': '4016', 'stage': 'neural'},
}

# Every reviewed row whose stored state deliberately differs from what the
# production matcher would produce, with the verdict it diverges from.
NON_REPRODUCIBLE = {
    GREEN_CABBAGE_ROW: {
        'stored': '4010', 'matcher_would_reach': '4016',
        'reason': ('`Bắp cải xanh 1/2 cái` is green HEAD CABBAGE, not mustard greens. Its '
                   'cleaned_name is parser-damaged to `cải xanh`, which the repaired catalog '
                   'now matches exactly, so the matcher reaches 4016 at EXACT_CATALOG_MATCH / '
                   '1.00. The reviewed target 4010 is stored anyway.')},
    SALTED_NAPA_ROW: {
        'stored': '4115', 'matcher_would_reach': '4109',
        'reason': ('`Cải thảo muối 100 gr` is salt-pickled napa. 4115 `Dưa cải bắp` (Cabbage '
                   'Chinese pickled with salt) is the reviewed preparation-correct identity; '
                   'the matcher still prefers fresh napa 4109 through the `cải thảo` alias.')},
    DRIED_SALTED_NAPA_ROW: {
        'stored': 'UNMATCHED', 'matcher_would_reach': '4109',
        'reason': ('Dried salted napa has no catalog identity. The matcher reaches fresh napa '
                   '4109 through the `cải thảo` alias, which is a different preparation and a '
                   'different nutrition profile.')},
    'spinach': {
        'stored': 'UNMATCHED', 'matcher_would_reach': '4010',
        'reason': ('27 rows. No spinach identity exists in the 750-row catalog. With the alias '
                   'removed the matcher falls through to the neural stage and reaches white '
                   'cabbage 4010, so the clears are ID-pinned rather than left to the removal.')},
    'kale': {
        'stored': 'UNMATCHED', 'matcher_would_reach': '4016',
        'reason': ('4 rows. No kale identity exists in the catalog. Removing the alias does not '
                   'help: the neural stage hands `cải xoăn` straight back to the repaired 4016, '
                   'so the rows would move from a wrong 4016 to the same wrong 4016 by another '
                   'route. ID-pinned clears, not an alias removal.')},
    'collision': {
        'stored': 'UNMATCHED', 'matcher_would_reach': '4016',
        'reason': ('3 rows -- two broccoli, one mizuna. The new `Cải xanh` head absorbs them at '
                   'EXACT or SUBPHRASE. 4094 is itself display-name corrupted, so there is no '
                   'trustworthy target and NO NEW ALIAS IS ADDED TO 4094.')},
}

DEFERRALS = {
    'residual_4016_qwen_rows': (
        'Ten rows stay on the repaired 4016 -- five `cải con` and five `cải thìa`-family -- and '
        'only refresh their stale stored display name. The bok-choy duplicate 4015 `Cải thìa '
        '(cải trắng)` vs 4135 `Rau cải chíp` is unresolved and `cải con` remains '
        'domain-ambiguous, so choosing a target for them is a separate reviewed decision.'),
    'keep_current_broccoli_compound': (
        'e9b2ce8d `Rau luộc ăn kèm (Cà rốt/bông cải xanh/bí chanh/đậu bắp 200 gram` stays on '
        '20086. After C1 the matcher would move it from 4007 to the new `cải xanh` head at '
        'SUBPHRASE_CATALOG_MATCH. KEEP_CURRENT / NEEDS_REVIEW, and a blast-radius exclusion.'),
    'curated_unmatched_compound': (
        '6ce0333f `Rau dền/rau má/cải xanh/giá…(rau tuỳ sở thích)` remains stored UNMATCHED. '
        'After C1 the matcher resolves it to 4016 by subphrase; that divergence is intentional '
        'and pinned. It is NOT counted as a changed processed row.'),
    'lá_cải_thảo_unreviewed_rows': (
        'Adding `lá cải thảo` -> 4109 for the one reviewed row also makes three stored-UNMATCHED '
        'rows carrying the same cleaned name matcher-claimable at 4109 (a176477b `1 chén lá cải '
        'thảo`, 47346974 `2-3 lá cải thảo`, d7f6dbcf `3 lá cải thảo`). Their IDENTITY audits '
        'clean -- plain fresh napa leaves, no preservation or preparation qualifier and no second '
        'ingredient -- but their parsed WEIGHT does not: the parser read the bare leaf counts as '
        '`phần ăn` servings at 150 g each, giving 300 g for `2-3 lá` and 450 g for `3 lá`. '
        'Linking them would write nutrition scaled by those weights, so KEEP_UNMATCHED / '
        'DEFERRED_REVIEW: they are recorded, pinned unchanged, and left for a batch that owns the '
        'weight question. Parser behaviour is not changed here.'),
    '4094_display_name_corruption': (
        '4094 publishes `Súp lơ (bông cải xanh)` over name_en `Mint leaves, raw`. That repair is '
        'a later batch. No alias action here targets 4094 and its 106 rows are asserted stable.'),
    'spinach_and_kale_catalog_gaps': (
        'Neither spinach nor kale exists in the catalog. Adding either identity is a catalog '
        'change, not an alias change, and is out of scope.'),
    '4015_vs_4135_bok_choy_duplicate': (
        '4015 `Cải thìa (cải trắng)` and 4135 `Rau cải chíp` are both bok choy. Their 11 and 59 '
        'rows are asserted stable; choosing a survivor is a separate domain decision.'),
}
EXCLUSIONS = [
    '4094 / 4096 display-name corruption', '4015 / 4135 bok-choy duplicate',
    '`cải con` target ambiguity', 'spinach and kale catalog gaps',
    'e9b2ce8d broccoli compound (KEEP_CURRENT / NEEDS_REVIEW)',
    '6ce0333f multi-option compound (curated UNMATCHED)',
    'three unreviewed `lá cải thảo` stored-UNMATCHED rows',
    'parser damage producing `cải xanh` from `Bắp cải xanh`',
    'match()/match_batch() architecture', 'general stale code-space contamination',
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


def duplicate_names(rows):
    names = [normalize_vietnamese_text(r['name_vi']) for r in rows]
    return {n for n in names if names.count(n) > 1}


def unmatched_row(before):
    """The full UNMATCHED contract, AGENTS.md section 4.

    Code, name, confidence and all four nutrients go blank; match_method becomes
    UNMATCHED. Confidence is blank, never 0.0 -- 0.0 is the explicit-rejection
    sentinel and means something else. Raw text, cleaned name, parsed
    quantity/unit, preparation note and estimated weight are preserved.
    """
    row = deepcopy(before)
    row.update({'master_ingredient_code': '', 'master_ingredient_name': '',
                'match_method': 'UNMATCHED', 'match_confidence': ''})
    for field in NUTRIENTS:
        row[field] = None
    return row


def expected_row(reviewed, catalog):
    """Row-level identity repair against the repaired catalog.

    A clear produces the UNMATCHED contract. Everything else keeps its existing
    provenance unless the manifest carries an explicit `match_after`, which
    --apply verifies against the real matcher rather than trusting the review.
    Weight is popped so the source value survives byte-for-byte; only the master
    identity, the provenance pair and the four nutrient columns move.
    """
    if reviewed['target_code'] is None:
        return unmatched_row(reviewed['before'])
    row = deepcopy(reviewed['before'])
    code = reviewed['target_code']
    match = reviewed.get('match_after') or {
        'match_method': row['match_method'], 'match_confidence': row['match_confidence']}
    patch = stage_qwen_update(row, catalog, float(row['estimated_weight_g']), {
        'master_ingredient_code': code, 'master_ingredient_name': catalog[code]['name_vi'], **match})
    patch.pop('estimated_weight_g')
    row.update(patch)
    return row


def nutrient_report(before, after):
    result = {}
    for f in NUTRIENTS:
        def total(rows):
            return sum((Decimal(str(r[f])) for r in rows if r.get(f) not in (None, '')), Decimal(0))
        b, a = total(before), total(after)
        result[f] = {
            'before_known_sum': str(b), 'after_known_sum': str(a), 'known_sum_delta': str(a - b),
            'before_null_count': sum(r.get(f) in (None, '') for r in before),
            'after_null_count': sum(r.get(f) in (None, '') for r in after),
            'value_to_null': sum(x.get(f) not in (None, '') and y.get(f) in (None, '')
                                 for x, y in zip(before, after)),
            'null_to_value': sum(x.get(f) in (None, '') and y.get(f) not in (None, '')
                                 for x, y in zip(before, after)),
        }
    return result


def nutrition_status(ingredient_rows, recipe_rows):
    """Recipe nutrition label and missing count, using the project's own rule.

    Computed from ingredient rows alone rather than read back from the recipe
    records, so the reviewed transition is measured against the manifest's before
    state on a first apply and on an idempotent replay alike.
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


def interim_digest(root):
    """One digest over every historical/interim file.

    Recorded in the applied report so the "interim is untouched" invariant can be
    re-verified later from the data alone, with no reference to git state.
    """
    manifest = {str(p.relative_to(root)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((root / 'data/interim').rglob('*')) if p.is_file()}
    blob = json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return {'files': len(manifest), 'sha256': hashlib.sha256(blob).hexdigest()}


def embedding_input_digest(catalog):
    texts = [f"{r['name_vi']} ({r['category_vi']})" for r in catalog]
    return hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode('utf-8')).hexdigest()


def verify_canonical(root):
    subprocess.run([sys.executable, 'scripts/canonicalize_recipes.py', '--check'], cwd=root, check=True)
    for name in ('canonical_recipes', 'canonical_recipe_ingredients'):
        parity(read_csv(root / DATA / (name + '.csv')), read_json(root / DATA / (name + '.json')))
    mapping = read_csv(root / DATA / 'recipe_canonical_mapping.csv')
    require({r['original_recipe_id']: r['canonical_recipe_id'] for r in mapping} ==
            read_json(root / DATA / 'recipe_canonical_mapping.json'), 'Canonical mapping JSON drift')


def qwen_rule_state(catalog_rows):
    """Active/disabled split and the one rule that must stay disabled."""
    masters = {r['code']: r for r in catalog_rows}
    active, disabled = build_mapper_rules(masters)
    terms, code, name = QWEN_RULE_MUST_STAY_DISABLED
    require((terms, code, name) in _QWEN_MAPPER_RULES, 'The guarded Qwen rule is no longer declared')
    require(not any(r[:3] == (terms, code, name) for r in active),
            'The `cải con`/`cải mầm`/`cải thìa` -> 4016 Qwen rule went active')
    require(any(r[:3] == (terms, code, name) for r in disabled),
            'The `cải con`/`cải mầm`/`cải thìa` -> 4016 Qwen rule vanished')
    for term in terms:
        require(map_clean_to_master(term, active) == (None, None),
                f'map_clean_to_master resolved `{term}` through the disabled 4016 rule')
    counts = {'active': len(active), 'disabled': len(disabled)}
    require(counts == EXPECTED_QWEN_RULE_COUNTS, f'Qwen mapper rule count drift: {counts}')
    return dict(counts, guarded_rule_disabled=True,
                map_clean_to_master_disabled_terms=list(terms))


def downstream_state(root, repair=False):
    """The one live cucumber hard-coding, planned or applied.

    Deterministic and idempotent: an already-repaired file reports zero pending
    occurrences and is not rewritten. A file that carries neither the reviewed
    before value nor the reviewed after value the expected number of times is
    drift, and fails closed rather than being partially rewritten.
    """
    measured, pending = {}, 0
    for path, count in DOWNSTREAM_FILES.items():
        text = (root / path).read_text(encoding='utf-8')
        before, after = text.count(DOWNSTREAM_BEFORE), text.count(DOWNSTREAM_AFTER)
        require(before + after == count,
                f'Downstream occurrence drift: {path} has {before + after}, want {count}')
        if repair and before:
            (root / path).write_text(text.replace(DOWNSTREAM_BEFORE, DOWNSTREAM_AFTER), encoding='utf-8')
            before, after = 0, count
        measured[str(path).replace('\\', '/')] = {'occurrences': count, 'on_4016': before, 'on_4027': after}
        pending += before
    # Search again rather than trust the table: any other live cucumber
    # hard-coding is unreviewed drift.
    found = {}
    for path in sorted((root / DOWNSTREAM_SCAN_ROOT).rglob('*.py')):
        for code in DOWNSTREAM_SCAN.findall(path.read_text(encoding='utf-8')):
            found.setdefault(code, []).append(str(path.relative_to(root)).replace('\\', '/'))
    require(set(found) <= {'4016', '4027'}, f'Unreviewed cucumber hard-coded code: {sorted(found)}')
    require(sum(len(v) for v in found.values()) == EXPECTED_DOWNSTREAM_REPOINTS,
            f'Cucumber hard-coding count drift: {found}')
    measured['pending'] = pending
    measured['scanned_codes'] = {k: sorted(set(v)) for k, v in found.items()}
    return measured


def audit_evidence_state(new_ing, catalog_rows):
    """The repaired 4016 WRONG signature, and the class counts it produces.

    WRONG["4016"] is NOT retired: the code is still the wrong home for the rows
    that remain on it. Only the display name and the synonym list move, and the
    resulting audit classification is re-measured against the repaired corpus.
    """
    from scripts.eda import audit_qwen_matching as audit
    require('4016' in audit.WRONG, 'WRONG["4016"] was retired; C1 keeps it')
    name, synonyms, reason = audit.WRONG['4016']
    require(name == AUDIT_WRONG_NAME, f'4016 audit display-name drift: {name}')
    require(synonyms == AUDIT_WRONG_SYNONYMS, f'4016 audit synonym drift: {synonyms}')
    require(all(normalize_vietnamese_text(s).startswith('cải ') for s in synonyms.split('|')),
            'Audit evidence is not a narrow reviewed synonym list')
    require(not any(s in synonyms for s in AUDIT_RETIRED_SYNONYMS),
            'A retired napa synonym is still claimed by the 4016 evidence')
    require(audit.WRONG['4015'][0] == 'Cải thìa (cải trắng)', 'C1 moved 4015 audit evidence')
    require(audit.VALID['4010'][0] == 'Cải bắp trắng', 'C1 moved C2 audit evidence')
    masters = {r['code']: r for r in catalog_rows}
    qwen = [r for r in new_ing if r['match_method'] == 'QWEN_LLM_MATCH']
    buckets = [audit.classify(r, masters)[0] for r in qwen]
    counts = {c: buckets.count(c) for c in audit.CLASSES}
    recipes = {c: len({r['recipe_id'] for r, b in zip(qwen, buckets) if b == c})
               for c in audit.CLASSES}
    measured = {'qwen_rows': len(qwen), 'class_counts': counts, 'class_recipes': recipes}
    require(measured == EXPECTED_AUDIT, f'Qwen audit drift: {measured}')
    residual = [r for r in qwen if r['master_ingredient_code'] == '4016']
    require(len(residual) == EXPECTED_NAME_REFRESH_ROWS,
            f'Residual 4016 QWEN population drift: {len(residual)}')
    return dict(measured, wrong_4016=[name, synonyms, reason],
                superseded=SUPERSEDED_AUDIT_CLASSES,
                residual_4016_rows=sorted(r['id'] for r in residual))


def qwen_recovery_protection(catalog_rows):
    """The reviewed clear is refused by the production recovery guard.

    Asserted against the live mapper, so this records what the pipeline would
    actually do rather than what the table says. The exclusion must refuse the
    reviewed line whatever the mapper resolves it to -- the reviewed claim is
    that no exact catalog identity exists -- and must leave every fresh-napa and
    kimchi line eligible.
    """
    masters = {r['code']: r for r in catalog_rows}
    active, _ = build_mapper_rules(masters)
    require(QWEN_EXCLUSION_RAW in _REVIEWED_NO_CATALOG_TARGET_RAW,
            'The reviewed dried-salted-napa line is not excluded from Qwen recovery')
    code, reason = _REVIEWED_NO_CATALOG_TARGET_RAW[QWEN_EXCLUSION_RAW]
    require(reason == QWEN_EXCLUSION_REASON, f'Reviewed exclusion reason drift: {reason}')
    would_reach, name = map_clean_to_master('cải thảo', active)
    require((would_reach, code) == (QWEN_EXCLUSION_WOULD_REACH, QWEN_EXCLUSION_WOULD_REACH),
            f'The neighbour the exclusion protects against moved: {would_reach}')
    for winning in (would_reach, None):
        require(qwen_candidate_eligibility(QWEN_EXCLUSION_RAW, 'cải thảo', winning)
                == (False, QWEN_EXCLUSION_REASON), 'The reviewed clear is Qwen-recoverable')
    allowed = {}
    for raw, cleaned in QWEN_EXCLUSION_MUST_STILL_ALLOW:
        target, _n = map_clean_to_master(cleaned, active)
        require(qwen_candidate_eligibility(raw, cleaned, target) == (True, None),
                f'The exclusion refuses a line it must not: {raw}')
        allowed[raw] = target
    return {'raw_text': QWEN_EXCLUSION_RAW, 'row': DRIED_SALTED_NAPA_ROW,
            'reason': QWEN_EXCLUSION_REASON, 'would_reach': would_reach,
            'would_reach_name': name, 'mechanism': 'nlp.qwen_matching._REVIEWED_NO_CATALOG_TARGET_RAW',
            'enforced_by': 'qwen_candidate_eligibility (scripts/run_qwen_line_pipeline.py block B)',
            'still_allowed': allowed, 'excluded_line_count': len(_REVIEWED_NO_CATALOG_TARGET_RAW)}


def guard_state(rows, aliases, catalog, review, pins, expected):
    """Prove the reviewed keeps held, measured rather than asserted."""
    guards = review['guards']
    live = index(rows)
    measured = {}
    # C3 is a later reviewed stored-data repair. Its rows are explicit additions
    # to the populations; retain C1's exact keep/move checks for every other row.
    c3_ids = set()
    c3_review = ROOT / 'scripts/eda/display_name_batch_c3_reviewed_state.json'
    if c3_review.exists():
        c3_ids = {p['before']['id'] for p in read_json(c3_review).get('rows', [])}

    # Source populations must be exhausted by the pins: never select by code.
    for code, key in (('4010', 'existing_4010_row_ids'), ('4027', 'existing_4027_row_ids'),
                      ('4109', 'existing_4109_row_ids'), ('20034', 'existing_20034_row_ids'),
                      ('4115', 'existing_4115_row_ids')):
        existing = set(guards[key])
        moved = {rid for rid in pins if expected[rid]['master_ingredient_code'] == code}
        require(existing.isdisjoint(moved), f'A pre-existing {code} row is also pinned as moving')
        observed = {r['id'] for r in rows if (r['master_ingredient_code'] or '') == code}
        if code == '4010':
            observed -= c3_ids
        require(observed == existing | moved, f'{code} population is not the reviewed keeps plus the reviewed moves')
        for rid in existing:
            require(live[rid]['master_ingredient_name'] == catalog[code]['name_vi'],
                    f'Pre-existing {code} row lost its display name: {rid}')
        measured[f'kept_rows_on_{code}'] = len(existing)
        measured[f'moved_rows_onto_{code}'] = len(moved)

    # 4011 is emptied and 4015 keeps exactly the reviewed survivors.
    require(not [r for r in rows if (r['master_ingredient_code'] or '') == '4011'],
            '4011 still carries rows after the recovery')
    surviving = set(guards['surviving_4015_row_ids'])
    require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == '4015'} == surviving,
            '4015 population is not the reviewed survivors')
    require(surviving.isdisjoint(pins), 'A surviving 4015 row is also pinned as moving')
    measured['surviving_4015_rows'] = len(surviving)

    # 4094 is untouched, by exact id set and not by count.
    require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == '4094'}
            == set(guards['population_4094_row_ids']), '4094 population drift')
    require(not any(v == NO_NEW_ALIAS_TO for k, v in aliases.items()
                    if k in set(ALIAS_ADDITIONS) | set(ALIAS_REPOINTS)),
            'NO NEW ALIAS TO 4094 violated')
    measured['rows_on_4094'] = len(guards['population_4094_row_ids'])

    # The ten residual rows keep their code, provenance and nutrition and only
    # refresh a stale display name.
    residual = set(guards['residual_qwen_4016_row_ids'])
    require(len(residual) == EXPECTED_NAME_REFRESH_ROWS, f'Residual cohort drift: {len(residual)}')
    for rid in residual:
        row, before = live[rid], pins[rid]['before']
        require(row['master_ingredient_code'] == '4016'
                and row['master_ingredient_name'] == catalog['4016']['name_vi']
                and row['match_method'] == 'QWEN_LLM_MATCH' == before['match_method']
                and row['match_confidence'] == before['match_confidence'],
                f'Residual row is not a pure display-name refresh: {rid}')
        require(all(logical(row)[f] == logical(before)[f] for f in NUTRIENTS),
                f'Residual row moved a nutrient: {rid}')
    measured['residual_4016_rows'] = sorted(residual)

    # Rows this batch must not change at all.
    for key in ('keep_current_needs_review', 'curated_unmatched_compound',
                'introduced_divergence_unreviewed'):
        for rid, before in guards[key].items():
            require(rid not in pins, f'A blast-radius exclusion is pinned as a changed row: {rid}')
            require(logical(live[rid]) == logical(before), f'Excluded row changed: {rid}')
        measured[key] = sorted(guards[key])
    keep = next(iter(guards['keep_current_needs_review'].values()))
    require(keep['master_ingredient_code'] == KEEP_CURRENT_CODE, 'KEEP_CURRENT row moved off 20086')
    curated = next(iter(guards['curated_unmatched_compound'].values()))
    require(curated['match_method'] == 'UNMATCHED' and not (curated['master_ingredient_code'] or ''),
            'The curated compound is no longer stored UNMATCHED')
    for before in guards['introduced_divergence_unreviewed'].values():
        require(before['match_method'] == 'UNMATCHED',
                'An unreviewed `lá cải thảo` row is no longer stored UNMATCHED')

    # The 35 clears carry the full UNMATCHED contract.
    cleared = [p for p in review['rows'] if p['target_code'] is None]
    require(len(cleared) == EXPECTED_CLEARS, f'Clear cohort drift: {len(cleared)}')
    for pin in cleared:
        row = live[pin['before']['id']]
        require(row['match_method'] == 'UNMATCHED'
                and not (row['master_ingredient_code'] or '').strip()
                and not (row['master_ingredient_name'] or '').strip()
                and row['match_confidence'] in (None, '')
                and row['match_confidence'] != '0.0'
                and all(row[f] in (None, '') for f in NUTRIENTS),
                f'Cleared row violates the UNMATCHED contract: {pin["before"]["id"]}')
        for field in ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                      'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g'):
            require(row[field] == pin['before'][field], f'Cleared row lost parsed evidence: {field}')
    measured['cleared_rows'] = sorted(p['before']['id'] for p in cleared)

    # Sibling identities, by count, from the manifest's own frozen table.
    siblings = {code: sum(1 for r in rows if (r['master_ingredient_code'] or '') == code)
                for code in guards['sibling_identity_row_counts']}
    moved_codes = {c for c in EXPECTED_POPULATIONS if c != 'UNMATCHED'}
    untouched = {c: n for c, n in guards['sibling_identity_row_counts'].items() if c not in moved_codes}
    require({c: siblings[c] for c in untouched} == untouched,
            f'Untouched sibling identity drift: {[c for c in untouched if siblings[c] != untouched[c]]}')
    measured['sibling_identity_row_counts'] = siblings
    return measured


def plan(root=ROOT):
    review = read_json(REVIEW)
    cat = read_csv(root / CAT)
    require(len(cat) == review['catalog_count'] == 750, 'Catalog row count drift')
    by_code = index(cat, 'code')
    new_cat = deepcopy(cat)
    new_by_code = index(new_cat, 'code')
    require({r['code'] for r in review['catalog_before']} == set(CATALOG_PATCHES),
            'Reviewed catalog scope drift')
    for before in review['catalog_before']:
        code = before['code']
        after = dict(before, **CATALOG_PATCHES[code])
        require(by_code.get(code) in (before, after), f'Catalog drift: {code}')
        # Only name_vi may move: code, name_en, both categories and every
        # nutrition column are asserted byte-for-byte on both sides.
        require({k: v for k, v in before.items() if k != 'name_vi'} ==
                {k: v for k, v in after.items() if k != 'name_vi'}, f'Non-name catalog change: {code}')
        require(before['name_vi'] == CATALOG_NAME_VI_BEFORE and after['name_vi'] == CATALOG_NAME_VI_AFTER,
                f'Reviewed rename drift: {code}')
        require(after['name_vi'] != FORBIDDEN_CATALOG_NAME, 'The forbidden Qwen-reactivating name was used')
        new_by_code[code].update(after)
    # The repair's justification is 4016's own name_en, not the review's say-so.
    require(new_by_code['4016']['name_en'] == CATALOG_NAME_EN,
            f'4016 is not the mustard-green source row: {new_by_code["4016"]["name_en"]!r}')
    require(by_code['4027']['name_en'] == 'Cucumber, raw' and by_code['4027']['name_vi'] == 'Dưa chuột',
            '4027 is not the cucumber identity this batch hands the cucumber rows to')
    # Sibling identities this batch must not write.
    for code, before in review['catalog_identities'].items():
        if code in CATALOG_PATCHES:
            continue
        require(by_code[code] == new_by_code[code] == before, f'Sibling catalog row modified: {code}')
    require(duplicate_names(cat) == duplicate_names(new_cat) == EXPECTED_DUPLICATE_NAMES,
            f'Duplicate display-name set moved: {duplicate_names(new_cat)}')
    require(sum(1 for r in new_cat if normalize_vietnamese_text(r['name_vi'])
                == normalize_vietnamese_text(CATALOG_NAME_VI_AFTER)) == 1,
            'The repaired name is not unique in the catalog')

    qwen = qwen_rule_state(new_cat)
    # The same rules must already be in that state BEFORE the rename: the batch
    # must neither activate nor deactivate one.
    require(qwen_rule_state(cat) == qwen, 'The rename changed the Qwen mapper rule state')

    aliases = read_json(root / ALIASES)
    require(len(aliases) in (ALIAS_MAP_SIZE_BEFORE, ALIAS_MAP_SIZE_LIVE),
            f'Alias map size drift: {len(aliases)}')
    require(review['alias_map_size'] == ALIAS_MAP_SIZE_BEFORE, 'Reviewed alias map size drift')
    actions = len(ALIAS_REPOINTS) + len(ALIAS_REMOVALS) + len(ALIAS_ADDITIONS)
    require(actions == EXPECTED_ALIAS_ACTIONS, f'Alias action count drift: {actions}')
    require(len({*ALIAS_REPOINTS, *ALIAS_REMOVALS, *ALIAS_ADDITIONS, *ALIAS_KEEPS}) ==
            actions + len(ALIAS_KEEPS), 'An alias key appears in two reviewed actions')
    require(set(ALIAS_REPOINTS) | set(ALIAS_REMOVALS) | set(ALIAS_KEEPS) == set(review['aliases_before']),
            'Reviewed alias scope drift')
    require(set(ALIAS_ADDITIONS) == set(review['aliases_absent_before']),
            'Reviewed alias addition scope drift')
    require(NO_NEW_ALIAS_TO not in set(ALIAS_ADDITIONS.values()) | set(ALIAS_REPOINTS.values()),
            'NO NEW ALIAS TO 4094')

    new_aliases = dict(aliases)
    for key, before in review['aliases_before'].items():
        if key in ALIAS_REMOVALS:
            require(aliases.get(key) in (before, None), f'Alias drift: {key}')
            new_aliases.pop(key, None)
            continue
        after = ALIAS_REPOINTS.get(key, before)
        require(aliases.get(key) in (before, after), f'Alias drift: {key}')
        new_aliases[key] = after
    for key, after in ALIAS_ADDITIONS.items():
        require(aliases.get(key) in (None, after), f'Added alias already points elsewhere: {key}')
        new_aliases[key] = after
    for key, code in ALIAS_KEEPS.items():
        require(review['aliases_before'][key] == code and aliases[key] == code and new_aliases[key] == code,
                f'Reviewed alias keep drift: {key}')
    moved_keys = {k for k in aliases.keys() | new_aliases.keys() if aliases.get(k) != new_aliases.get(k)}
    require(moved_keys <= set(ALIAS_REPOINTS) | set(ALIAS_REMOVALS) | set(ALIAS_ADDITIONS),
            f'Unrelated alias change: {sorted(moved_keys - set(ALIAS_REPOINTS) - set(ALIAS_REMOVALS) - set(ALIAS_ADDITIONS))}')
    require(len(new_aliases) == ALIAS_MAP_SIZE_LIVE,
            f'Alias map size after the repair: {len(new_aliases)} (want {ALIAS_MAP_SIZE_LIVE})')
    require(all(k not in new_aliases for k in ALIAS_REMOVALS), 'A removed alias survived')
    left_behind = {k: v for k, v in new_aliases.items() if k in ALIAS_REPOINTS and v != ALIAS_REPOINTS[k]}
    require(left_behind == {}, f'Repointed alias not applied: {left_behind}')
    # Every alias left on the repaired identity must be reviewed, and no alias
    # naming a cucumber may still reach it.
    reviewed_on_4016 = ({k for k, v in ALIAS_REPOINTS.items() if v == '4016'}
                        | {k for k, v in ALIAS_ADDITIONS.items() if v == '4016'}
                        | {k for k, v in ALIAS_KEEPS.items() if v == '4016'})
    on_4016 = {k for k, v in new_aliases.items() if v == '4016'}
    require(on_4016 == reviewed_on_4016,
            f'Unreviewed alias targets the repaired 4016: {sorted(on_4016 - reviewed_on_4016)}')
    require(not any('dưa' in normalize_vietnamese_text(k) for k in on_4016),
            'A cucumber/pickle phrase still reaches 4016')
    require(not any('thảo' in normalize_vietnamese_text(k) or 'thìa' in normalize_vietnamese_text(k)
                    for k in on_4016), 'A napa/bok-choy phrase reaches the mustard-green identity')
    require(all('dưa' in normalize_vietnamese_text(k) for k, v in new_aliases.items() if v == '4027'),
            'A non-cucumber alias reaches 4027')
    # 4094's keys are untouched, asserted from the live map rather than narrated.
    on_4094_before = {k for k, v in aliases.items() if v == NO_NEW_ALIAS_TO}
    require({k for k, v in new_aliases.items() if v == NO_NEW_ALIAS_TO} == on_4094_before,
            'A 4094 alias key moved')
    require(new_aliases[LONG_REVIEWED_ALIAS] == '4016' and len(LONG_REVIEWED_ALIAS.split()) > 6,
            'The reviewed parser-damaged key was replaced by a broad generic alias')

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
    changed_pins = {rid for rid, pin in pins.items() if pin['cohort'] != NAME_REFRESH_COHORT}
    require(len(changed_pins) == EXPECTED_CHANGED_ROWS,
            f'Reviewed changed-row scope drift: {len(changed_pins)}')
    require(len(pins) - len(changed_pins) == EXPECTED_NAME_REFRESH_ROWS, 'Name-refresh scope drift')

    for cohort, (source, target, count, provenance) in COHORTS.items():
        pinned = {rid for rid, pin in pins.items() if pin['cohort'] == cohort}
        require(len(pinned) == count, f'Reviewed cohort count drift: {cohort}={len(pinned)}')
        require(all(pins[rid]['target_code'] == target for rid in pinned), f'Reviewed target drift: {cohort}')
        for rid in pinned:
            before = pins[rid]['before']
            if source is None:
                require(before['match_method'] == 'UNMATCHED'
                        and not (before['master_ingredient_code'] or '').strip()
                        and all(before[f] in (None, '') for f in NUTRIENTS),
                        f'Reviewed recovery source drift: {rid}')
            else:
                require(before['master_ingredient_code'] == source, f'Reviewed source drift: {cohort}: {rid}')
            if provenance in ('preserved', 'name_refresh'):
                require(expected[rid]['match_method'] == before['match_method']
                        and expected[rid]['match_confidence'] == before['match_confidence'],
                        f'Match provenance not preserved: {rid}')
            elif provenance == 'measured':
                require(pins[rid].get('match_after'), f'Re-measured row carries no reviewed verdict: {rid}')
            # Raw and parsed evidence must survive untouched on every row, clears
            # and recoveries included.
            for field in ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                          'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g'):
                require(expected[rid][field] == before[field], f'Raw/parsed field moved: {rid}.{field}')
            if target is not None:
                require(expected[rid]['master_ingredient_name'] == new_by_code[target]['name_vi'],
                        f'Target display name drift: {rid}')

    # Cohorts are semantic, not code selections: each is stated over its own
    # cleaned names or its own pinned ids.
    def cleaned(cohort):
        return {pins[rid]['before']['cleaned_name'] for rid, p in pins.items() if p['cohort'] == cohort}
    require(cleaned('cucumber_4016_to_4027') == {'dưa leo', 'ăn kèm dưa leo', 'dưa leo cắt sợi'},
            'Reviewed cucumber cohort is not the reviewed cleaned-name set')
    require(cleaned('mustard_alias_4011_to_4016') == {'cải bẹ xanh', 'rau cải xanh', 'ăn kèm cải bẹ xanh'},
            'Reviewed mustard alias cohort is not the reviewed cleaned-name set')
    require(cleaned('mustard_exact_4011_to_4016') == {'cải xanh'}, 'Reviewed exact cohort drift')
    require(cleaned('mustard_leaf_4015_to_4016') == {'lá cải xanh'}, 'Reviewed 4015 leaf cohort drift')
    require(cleaned('spinach_clear_to_unmatched') == {'cải cải bó xôi'}, 'Reviewed spinach cohort drift')
    require(cleaned('kale_clear_to_unmatched') == {'cải xoăn'}, 'Reviewed kale cohort drift')
    require(cleaned('fresh_napa_4016_to_4109') == {'cải thảo', 'lá cải thảo'}, 'Reviewed napa cohort drift')
    require(cleaned('kimchi_4016_to_20034') == {'kim chi cải thảo', 'kimchi cải thảo'},
            'Reviewed kimchi cohort drift')
    require(cleaned('residual_qwen_keep_4016')
            == {'cải con', 'cải thìa', 'cải thìa con', 'cải thìa chua'}, 'Residual cohort drift')
    require(sum(1 for rid in pins if pins[rid]['cohort'] == NAME_REFRESH_COHORT
                and pins[rid]['before']['cleaned_name'] == 'cải con') == 5,
            'Residual `cải con` count drift')
    require(cleaned('collision_clear_to_unmatched')
            == {'bông cải xanh baby', 'cải xanh', 'cải xanh đuôi phụng'}, 'Collision cohort drift')
    require(cleaned('mustard_unmatched_recovery_to_4016') == set(ALIAS_ADDITIONS) - {
        'lá cải thảo', 'kimchi cải thảo', 'lá cải xanh'}, 'Recovery cohort is not the added narrow keys')
    # The single-row reviewed decisions, pinned by id AND by exact raw text.
    for short_id, raw_text in ((DRIED_SALTED_NAPA_ROW, DRIED_SALTED_NAPA_RAW),
                               (GREEN_CABBAGE_ROW, GREEN_CABBAGE_RAW),
                               (SALTED_NAPA_ROW, SALTED_NAPA_RAW)):
        matches = [rid for rid in pins if rid.startswith(short_id)]
        require(len(matches) == 1, f'Reviewed single-row pin is not unique: {short_id}')
        require(pins[matches[0]]['before']['raw_text'] == raw_text,
                f'Reviewed single-row raw text drift: {short_id}')
    dried = next(rid for rid in pins if rid.startswith(DRIED_SALTED_NAPA_ROW))
    require(pins[dried]['target_code'] is None
            and pins[dried]['cohort'] == 'dried_salted_napa_clear_to_unmatched',
            'The reviewer-approved dried-salted-napa clear is not stored as a clear')
    green = next(rid for rid in pins if rid.startswith(GREEN_CABBAGE_ROW))
    require(pins[green]['target_code'] == '4010' and pins[green]['before']['cleaned_name'] == 'cải xanh',
            'The reviewed green-cabbage repair drifted')
    salted = next(rid for rid in pins if rid.startswith(SALTED_NAPA_ROW))
    require(pins[salted]['target_code'] == '4115', 'The reviewed salted-napa correction drifted')
    long_row = next(rid for rid in pins if rid.startswith(LONG_REVIEWED_ALIAS_ROW))
    require(pins[long_row]['before']['cleaned_name'] == LONG_REVIEWED_ALIAS,
            'The long reviewed alias no longer matches its one row')

    # Never select by code alone: the pins must exhaust each source population.
    for code in ('4016', '4011'):
        on_code_before = {rid for rid, pin in pins.items() if pin['before']['master_ingredient_code'] == code}
        on_code_after = {rid for rid in pins if expected[rid]['master_ingredient_code'] == code}
        population = {r['id'] for r in ingredients if r['master_ingredient_code'] == code}
        require(population in (on_code_before, on_code_after | (population - pins.keys())),
                f'Unreviewed rows on {code}: {len(population)}')
    require(len({rid for rid, pin in pins.items() if pin['before']['master_ingredient_code'] == '4016'})
            == 301, 'Reviewed 4016 population drift')
    require(len({rid for rid, pin in pins.items() if pin['before']['master_ingredient_code'] == '4011'})
            == 41, 'Reviewed 4011 population drift')

    def transform(rows):
        mutable = set(NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name',
                                    'match_method', 'match_confidence'}
        return [dict(r, **{k: v for k, v in expected[r['id']].items() if k in mutable})
                if r['id'] in expected else dict(r) for r in rows]
    new_ing, new_ing_json = transform(ingredients), transform(ingredients_json)
    parity(new_ing, new_ing_json)
    untouched = [r for r in ingredients if r['id'] not in pins]
    require([logical(r) for r in untouched] == [logical(r) for r in new_ing if r['id'] not in pins],
            f'A row outside the reviewed {EXPECTED_ROWS} changed')

    populations = {code: sum(1 for r in new_ing if (r['master_ingredient_code'] or '') == code)
                   for code in EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in new_ing if r['match_method'] == 'UNMATCHED')
    require(populations == EXPECTED_POPULATIONS, f'Final population drift: {populations}')
    require(populations['UNMATCHED'] == sum(1 for r in new_ing if not (r['master_ingredient_code'] or '').strip()),
            'UNMATCHED/blank-code mismatch')
    require(populations['4016'] == (EXPECTED_NAME_REFRESH_ROWS + 40 + 5 + 5),
            'Final 4016 composition is not 10 residual + 40 + 5 + 5')
    corpus_nulls = {f: sum(1 for r in new_ing if r[f] in (None, '')) for f in NUTRIENTS}
    require(corpus_nulls == EXPECTED_CORPUS_NULLS, f'Corpus null drift: {corpus_nulls}')
    guard_measured = guard_state(new_ing, new_aliases, new_by_code, review, pins, expected)

    ordered = sorted(changed_pins)
    combined = nutrient_report([pins[rid]['before'] for rid in ordered], [expected[rid] for rid in ordered])
    require({f: combined[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_NUTRITION_DELTA,
            f"Nutrition delta drift: {[combined[f]['known_sum_delta'] for f in NUTRIENTS]}")
    all_rows = sorted(pins)
    combined_all = nutrient_report([pins[rid]['before'] for rid in all_rows],
                                   [expected[rid] for rid in all_rows])
    require({f: combined_all[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_NUTRITION_DELTA,
            'The display-name refreshes moved a nutrient')
    require({f: (combined_all[f]['before_null_count'], combined_all[f]['after_null_count'])
             for f in NUTRIENTS} == EXPECTED_NULL_TRANSITIONS, 'Null transition drift')
    require({f: combined_all[f]['value_to_null'] for f in NUTRIENTS} == EXPECTED_VALUE_TO_NULL
            and {f: combined_all[f]['null_to_value'] for f in NUTRIENTS} == EXPECTED_NULL_TO_VALUE,
            'Null direction drift')
    # The extra fat_g nulls are missing catalog data, not coerced zeros.
    fat_nulls = [rid for rid in all_rows if pins[rid]['before']['fat_g'] not in (None, '')
                 and expected[rid]['fat_g'] in (None, '') and pins[rid]['target_code'] is not None]
    require(len(fat_nulls) == EXPECTED_FAT_NULL_FROM_MISSING_TARGET
            and {pins[rid]['target_code'] for rid in fat_nulls} == set(FAT_NULL_TARGETS),
            f'Unexpected fat_g null source: {len(fat_nulls)}')
    for code in FAT_NULL_TARGETS:
        require(new_by_code[code]['fat_g'].strip() == '', f'{code} unexpectedly publishes fat_g')
    cohort_nutrition = {}
    for cohort in COHORTS:
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        cohort_nutrition[cohort] = nutrient_report([pins[rid]['before'] for rid in ids],
                                                   [expected[rid] for rid in ids])
    require({c: {f: n[f]['known_sum_delta'] for f in NUTRIENTS} for c, n in cohort_nutrition.items()}
            == EXPECTED_COHORT_NUTRITION_DELTA, 'Reviewed cohort nutrition delta drift')
    # Every populated nutrient is the live TARGET catalog column scaled by the
    # row's own weight through the project's own scaler (AGENTS.md section 9).
    for rid in all_rows:
        if pins[rid]['target_code'] is None:
            require(all(expected[rid][f] is None for f in NUTRIENTS), f'A cleared row kept nutrition: {rid}')
            continue
        target = new_by_code[pins[rid]['target_code']]
        weight = float(expected[rid]['estimated_weight_g'])
        for field, column in NUTRITION_FIELDS.items():
            want = scale_nutrition(target[column], weight / 100.0, 1)
            if want is None:
                require(expected[rid][field] is None, f'Missing nutrient coerced: {rid}.{field}')
            else:
                require(expected[rid][field] is not None and float(expected[rid][field]) == want,
                        f'Nutrient not recomputed from the target catalog: {rid}.{field}')

    recipes_affected = {expected[rid]['recipe_id'] for rid in pins}
    changed_recipes = {expected[rid]['recipe_id'] for rid in changed_pins}
    require(len(recipes_affected) == EXPECTED_RECIPES, f'Recipe radius drift: {len(recipes_affected)}')
    require(len(changed_recipes) == EXPECTED_CHANGED_ROW_RECIPES,
            f'Changed-row recipe radius drift: {len(changed_recipes)}')
    recipes = read_csv(root / DATA / 'recipes.csv')
    recipes_json = read_json(root / DATA / 'recipes.json')
    parity(recipes, recipes_json)
    new_recipes, new_recipes_json = deepcopy(recipes), deepcopy(recipes_json)
    rollups = recompute_recipe_rollups(new_ing)
    affected_rollups = {k: v for k, v in rollups.items() if k in recipes_affected}
    _apply_rollups(new_recipes, affected_rollups)
    _apply_rollups(new_recipes_json, affected_rollups)
    # Radius is measured against the reviewed BEFORE state, reconstructed from the
    # manifest, so the figures are identical on a first apply and on a replay --
    # and, unlike a git diff, they do not invert once the batch is committed.
    baseline_ing = [dict(pins[r['id']]['before']) if r['id'] in pins else dict(r) for r in ingredients]
    baseline_rollups = recompute_recipe_rollups(baseline_ing)
    changed_rollups = {rid for rid in rollups if _new_totals(baseline_rollups[rid]) != _new_totals(rollups[rid])}
    require(changed_rollups == changed_recipes,
            f'Rollup radius is not exactly the reviewed changed-row recipes: {len(changed_rollups)}')
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
    c3_review = ROOT / 'scripts/eda/display_name_batch_c3_reviewed_state.json'
    if c3_review.exists():
        c3_recipes = {p['before']['recipe_id'] for p in read_json(c3_review).get('rows', [])}
        transitions = {rid: t for rid, t in transitions.items() if rid not in c3_recipes}
        labels = {rid for rid, t in transitions.items() if t['before'][0] != t['after'][0]}
        status['recipes_with_changed_missing_count'] = len(transitions)
        status['recipes_with_status_label_changed'] = len(labels)
        status['missing_count_transitions'] = {rid: {'before': t['before'][1], 'after': t['after'][1]} for rid, t in transitions.items()}
        status['status_transitions'] = {rid: f"{t['before'][0]} -> {t['after'][0]}" for rid, t in transitions.items() if rid in labels}
    if not c3_review.exists():
        require({rid: (t['before'][1], t['after'][1]) for rid, t in transitions.items()}
                == EXPECTED_MISSING_COUNT_TRANSITIONS, f'missing_nutrition_count radius drift: {status}')
        require(status['status_transitions'] == EXPECTED_STATUS_LABEL_TRANSITIONS,
                f"Status transition drift: {status['status_transitions']}")
    # Clear-bearing recipes may only gain missing rows; recovery recipes may only lose them.
    clear_recipes = {pins[p['before']['id']]['before']['recipe_id']
                     for p in review['rows'] if p['target_code'] is None}
    recovery_recipes = {pins[rid]['before']['recipe_id'] for rid in pins
                        if pins[rid]['before']['match_method'] == 'UNMATCHED'}
    napa_recipes = {pins[rid]['before']['recipe_id'] for rid in pins
                    if pins[rid]['target_code'] in FAT_NULL_TARGETS}
    for rid, t in transitions.items():
        if rid in clear_recipes:
            require(t['after'][1] >= t['before'][1] or rid in recovery_recipes,
                    f'A clear-bearing recipe lost a missing row without a recovery: {rid}')
        elif rid in recovery_recipes:
            require(t['after'][1] < t['before'][1], f'A recovery recipe did not lose a missing row: {rid}')
        else:
            require(rid in napa_recipes, f'An unreviewed recipe changed its missing count: {rid}')
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
        if name in EXPECTED_CANONICAL_TOTALS:
            require(len(after) == EXPECTED_CANONICAL_TOTALS[name], f'Canonical total drift: {name}={len(after)}')
        changed = [rid for rid in before if logical(before[rid]) != logical(after[rid])]
        if name == 'recipe_canonical_mapping.csv':
            stable = ('canonical_recipe_id', 'phase1_canonical_recipe_id', 'selected_source_url',
                      'canonical_group_id', 'canonical_dish_name', 'duplicate_group_size',
                      'resolution_status', 'candidate_rank')
            require(all(all(logical(before[rid])[f] == logical(after[rid])[f] for f in stable) for rid in before),
                    'Canonical mapping / representative drift')
            require(set(changed) <= recipes_affected, f'Unexpected canonical mapping change: {len(changed)}')
            moved = {f for rid in changed for f in before[rid]
                     if logical(before[rid])[f] != logical(after[rid])[f]}
            require(moved <= EXPECTED_MAPPING_CHANGED_FIELDS, f'Unexpected mapping field moved: {moved}')
            groups = len({before[rid]['canonical_recipe_id'] for rid in recipes_affected})
            changed_groups = len({before[rid]['canonical_recipe_id'] for rid in changed_recipes})
            require(groups == EXPECTED_CANONICAL_GROUPS, f'Canonical group radius drift: {groups}')
            require(changed_groups == EXPECTED_CANONICAL_GROUPS_CHANGED_ROWS,
                    f'Changed-row canonical group radius drift: {changed_groups}')
            canonical[name] = {'changed_count': len(changed), 'changed_fields': sorted(moved),
                               'mapping_rows_for_affected_recipes': len(recipes_affected & before.keys()),
                               'canonical_groups_involved': groups,
                               'canonical_groups_for_changed_rows': changed_groups}
            require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')
            continue
        if name == 'canonical_recipe_ingredients.csv':
            require(set(changed) <= pins.keys(), 'Unrelated canonical ingredients changed')
            absent = len(pins.keys() - before.keys())
            require(absent == EXPECTED_CANONICAL_INGREDIENT_ROWS_ABSENT,
                    f'Reviewed rows absent from canonical ingredients: {absent}')
            canonical[name] = {'changed_count': len(changed), 'reviewed_rows_absent': absent}
        else:
            require(set(changed) <= recipes_affected, 'Unrelated canonical recipe changed')
            canonical[name] = {'changed_count': len(changed),
                               'recipes_touched_without_content_change':
                                  len((recipes_affected & before.keys()) - set(changed))}
        require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')

    downstream = downstream_state(root)
    audit_evidence = audit_evidence_state(new_ing, new_cat)
    qwen_protection = qwen_recovery_protection(new_cat)

    files = {CAT: new_cat, ALIASES: new_aliases,
             DATA / 'recipe_ingredients.csv': new_ing, DATA / 'recipe_ingredients.json': new_ing_json,
             DATA / 'recipes.csv': new_recipes, DATA / 'recipes.json': new_recipes_json}
    # The write set is the whole write set: nothing historical is ever in it.
    require(all('interim' not in p.as_posix() for p in files),
            'A historical/interim path entered the write set')
    before_files = {CAT: cat, ALIASES: aliases, DATA / 'recipe_ingredients.csv': ingredients,
                    DATA / 'recipe_ingredients.json': ingredients_json, DATA / 'recipes.csv': recipes,
                    DATA / 'recipes.json': recipes_json}
    changed_now = [rid for rid in pins if logical(live[rid]) != logical(expected[rid])]
    catalog_before = {r['code']: r for r in review['catalog_before']}
    report = dict(
        policy='DISPLAY_NAME_BATCH_C1',
        root_cause=(
            'Catalog 4016 is the raw Viện Dinh Dưỡng row `Mustard greens, raw`, but its Vietnamese '
            'display name read `Dưa chuột (dưa leo)` -- cucumber -- which is 4027\'s identity, and '
            '4027 already carries `Dưa chuột`. The alias map organised three cucumber keys and 248 '
            'processed rows around 4016 as though it were a cucumber, while the genuine mustard '
            'greens sat on red cabbage 4011 and bok choy 4015, five more sat stored-UNMATCHED, and '
            'spinach, kale, napa and kimchi rows were parked on 4016 because nothing else claimed '
            'them.'),
        reviewer_override=REVIEWER_OVERRIDE,
        rows_repaired=EXPECTED_CHANGED_ROWS, rows_written=EXPECTED_ROWS,
        display_name_refreshes=EXPECTED_NAME_REFRESH_ROWS,
        rows_pending=len(changed_now), recipes_affected=EXPECTED_CHANGED_ROW_RECIPES,
        recipes_touched_including_name_refresh=EXPECTED_RECIPES,
        catalog_count=750,
        catalog_diff={c: {k: {'before': catalog_before[c][k], 'after': v} for k, v in patch.items()}
                      for c, patch in CATALOG_PATCHES.items()},
        catalog_name_en={c: new_by_code[c]['name_en'] for c in CATALOG_PATCHES},
        catalog_unchanged_columns=sorted(k for k in catalog_before['4016'] if k != 'name_vi'),
        forbidden_name={'name': FORBIDDEN_CATALOG_NAME,
                        'reason': ('would reactivate the disabled Qwen rule ("cải con", "cải mầm", '
                                   '"cải thìa") -> 4016 "Cải bẹ trắng (cải thìa/thảo)" through the '
                                   'A1 identity check, republishing the bok-choy/napa identity this '
                                   'batch removes from 4016')},
        duplicate_names_before=sorted(EXPECTED_DUPLICATE_NAMES),
        duplicate_names_after=sorted(EXPECTED_DUPLICATE_NAMES),
        qwen_mapper=qwen,
        alias_actions=EXPECTED_ALIAS_ACTIONS,
        alias_diff={
            'repointed': {k: {'before': review['aliases_before'][k], 'after': v}
                          for k, v in sorted(ALIAS_REPOINTS.items())},
            'removed': {k: {'before': review['aliases_before'][k], 'after': None}
                        for k in sorted(ALIAS_REMOVALS)},
            'added': {k: {'before': None, 'after': v} for k, v in sorted(ALIAS_ADDITIONS.items())},
        },
        alias_keeps=ALIAS_KEEPS, alias_map_size_before=ALIAS_MAP_SIZE_BEFORE,
        alias_map_size=len(new_aliases),
        no_new_alias_to_4094={'invariant': 'NO NEW ALIAS TO 4094', 'keys_on_4094': sorted(on_4094_before),
                              'reason': ('4094 publishes `Súp lơ (bông cải xanh)` over name_en '
                                         '`Mint leaves, raw` and is itself display-name corrupted.')},
        alias_removal_fallthrough=ALIAS_REMOVAL_FALLTHROUGH,
        populations=populations, corpus_nulls=corpus_nulls,
        combined_nutrition=combined, combined_nutrition_all_rows=combined_all,
        superseded_audit_nutrition_delta=SUPERSEDED_AUDIT_NUTRITION_DELTA,
        recipe_status=status, canonical=canonical,
        canonical_id_drift=0, representative_drift=0,
        superseded_audit_canonical=SUPERSEDED_AUDIT_CANONICAL,
        downstream_hard_codes=downstream, audit_evidence=audit_evidence,
        qwen_recovery_protection=qwen_protection,
        interim=interim_digest(root), write_set=sorted(p.as_posix() for p in files),
        non_reproducible=NON_REPRODUCIBLE,
        guards=guard_measured, deferrals=DEFERRALS,
        affected_recipe_ids=sorted(recipes_affected),
        row_outcomes={rid: dict(cohort=pins[rid]['cohort'], before=pins[rid]['before'], after=expected[rid])
                      for rid in all_rows},
        cohorts={}, exclusions=EXCLUSIONS)
    recipe_before, recipe_after = index(recipes_json), index(new_recipes_json)
    report['recipe_outcomes'] = {rid: {'before': recipe_before[rid], 'after': recipe_after[rid]}
                                 for rid in sorted(recipes_affected)}
    for cohort, (source, target, _count, provenance) in COHORTS.items():
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        report['cohorts'][cohort] = dict(
            source_code=source or 'UNMATCHED', target_code=target or 'UNMATCHED',
            provenance=provenance, row_count=len(ids),
            recipe_count=len({expected[rid]['recipe_id'] for rid in ids}), row_ids=ids,
            cleaned_names=sorted({pins[rid]['before']['cleaned_name'] for rid in ids}),
            nutrition=cohort_nutrition[cohort])
    return files, before_files, report


def replay(matcher, report):
    """Every reviewed identity and every reviewed row, in production shape.

    Production shape is match_batch(cleaned_name, raw_contexts=raw_text): the
    cleaned name is the query and the original recipe line is the context the
    qualifier guards need. Rows are classified A (reproducible repaired row),
    B (curated divergence) or C (curated UNMATCHED), and every divergence
    records the code the matcher would have reached instead.
    """
    probes = {}
    queries = list(PROBES)
    for query, verdict in zip(queries, matcher.match_batch(queries, raw_contexts=queries)):
        code = (verdict['matched_item'] or {}).get('code')
        require(code == PROBES[query], f'Matcher probe failed: {query}: {code} (want {PROBES[query]})')
        probes[query] = {'code': code, 'method': verdict['method'],
                         'confidence': round(float(verdict['confidence']), 4)}

    outcomes = report['row_outcomes']
    ids = sorted(outcomes)
    verdicts = matcher.match_batch([outcomes[i]['before']['cleaned_name'] for i in ids],
                                   raw_contexts=[outcomes[i]['before']['raw_text'] for i in ids])
    classes = {'A_reproducible': [], 'B_curated_divergence': [], 'C_curated_unmatched': [],
               'D_deferred_name_refresh': []}
    divergence = {}
    for rid, verdict in zip(ids, verdicts):
        outcome = outcomes[rid]
        reached = (verdict['matched_item'] or {}).get('code')
        stored = (outcome['after']['master_ingredient_code'] or '') or None
        record = {'reached': reached, 'method': verdict['method'],
                  'confidence': round(float(verdict['confidence']), 4),
                  'stored': stored or 'UNMATCHED', 'cleaned_name': outcome['before']['cleaned_name']}
        if outcome['cohort'] == NAME_REFRESH_COHORT:
            classes['D_deferred_name_refresh'].append(rid)
            divergence[rid] = record
        elif stored is None:
            classes['C_curated_unmatched'].append(rid)
            divergence[rid] = record
        elif (reached == stored and verdict['method'] == outcome['after']['match_method']
              and str(round(float(verdict['confidence']), 2)) == outcome['after']['match_confidence']):
            classes['A_reproducible'].append(rid)
        else:
            classes['B_curated_divergence'].append(rid)
            divergence[rid] = record
    counts = {k: len(v) for k, v in classes.items()}
    require(counts['C_curated_unmatched'] == EXPECTED_CLEARS, f'Curated clear replay drift: {counts}')
    require(counts['D_deferred_name_refresh'] == EXPECTED_NAME_REFRESH_ROWS, f'Residual replay drift: {counts}')
    require(counts['A_reproducible'] + counts['B_curated_divergence'] + counts['C_curated_unmatched']
            == EXPECTED_CHANGED_ROWS, f'Changed-row replay drift: {counts}')
    require(counts['A_reproducible'] == EXPECTED_REPRODUCIBLE_ROWS, f'Reproducible drift: {counts}')
    require(counts['B_curated_divergence'] == EXPECTED_CURATED_DIVERGENCE_ROWS,
            f'Curated divergence drift: {counts}')
    require({rid[:8] for rid in classes['B_curated_divergence']} == {GREEN_CABBAGE_ROW, SALTED_NAPA_ROW},
            'The curated divergences are not the two reviewed rows')
    for short_id, want in ((GREEN_CABBAGE_ROW, '4016'), (SALTED_NAPA_ROW, '4109'),
                           (DRIED_SALTED_NAPA_ROW, '4109')):
        rid = next(i for i in ids if i.startswith(short_id))
        require(divergence[rid]['reached'] == want,
                f'Reviewed divergence drift: {short_id} reaches {divergence[rid]["reached"]}')
    for cohort, want in (('spinach_clear_to_unmatched', '4010'), ('kale_clear_to_unmatched', '4016'),
                         ('collision_clear_to_unmatched', '4016')):
        reached = {divergence[rid]['reached'] for rid in ids if outcomes[rid]['cohort'] == cohort}
        require(reached == {want}, f'Curated clear fallthrough drift: {cohort} -> {reached}')

    # Rows this batch deliberately leaves alone, and the verdicts they diverge
    # from. Measured, never adopted.
    excluded = {}
    review = read_json(REVIEW)
    for key in ('keep_current_needs_review', 'curated_unmatched_compound',
                'introduced_divergence_unreviewed'):
        pinned = review['guards'][key]
        names = [pinned[rid]['cleaned_name'] for rid in sorted(pinned)]
        contexts = [pinned[rid]['raw_text'] for rid in sorted(pinned)]
        for rid, verdict in zip(sorted(pinned), matcher.match_batch(names, raw_contexts=contexts)):
            excluded[rid] = {'group': key, 'cleaned_name': pinned[rid]['cleaned_name'],
                             'stored': (pinned[rid]['master_ingredient_code'] or 'UNMATCHED'),
                             'reached': (verdict['matched_item'] or {}).get('code'),
                             'method': verdict['method'],
                             'confidence': round(float(verdict['confidence']), 4)}
    curated = next(r for rid, r in excluded.items() if r['group'] == 'curated_unmatched_compound')
    require(curated['stored'] == 'UNMATCHED' and curated['reached'] == '4016',
            'The curated compound no longer diverges as reviewed')
    keep = next(r for rid, r in excluded.items() if r['group'] == 'keep_current_needs_review')
    require(keep['stored'] == KEEP_CURRENT_CODE and keep['reached'] == '4016',
            'The KEEP_CURRENT row no longer diverges as reviewed')
    introduced = [r for r in excluded.values() if r['group'] == 'introduced_divergence_unreviewed']
    require(len(introduced) == 3 and all(r['stored'] == 'UNMATCHED' and r['reached'] == '4109'
                                         for r in introduced),
            'The three unreviewed `lá cải thảo` rows no longer behave as recorded')
    return probes, {'counts': counts, 'classes': classes, 'divergence': divergence,
                    'excluded_rows': excluded}


def write_report(report, out):
    out.mkdir(parents=True, exist_ok=True)
    (out / 'applied_fix.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                                          encoding='utf-8')
    diff = report['catalog_diff']['4016']['name_vi']
    override = report['reviewer_override']
    lines = ['# Display-name corruption repair, Batch C1 — mustard greens 4016', '',
             f"Policy: DISPLAY_NAME_BATCH_C1. {report['rows_repaired']} ingredient rows change "
             f"identity across {report['recipes_affected']} source recipes; "
             f"{report['display_name_refreshes']} more rows only refresh a stale display name "
             f"({report['rows_written']} rows written in total).", '',
             '## Root cause', '', report['root_cause'], '',
             '## Reviewer decision that supersedes the audit', '',
             f"Row `{override['row']}` — `{override['raw_text']}` — was **{override['audit_disposition']}** "
             f"in the audit and is **{override['reviewed_disposition']}** here.", '',
             override['reason'], '', override['consequences'], '',
             'Every figure below is therefore re-measured from the approved '
             f"{report['rows_repaired']}-row state rather than carried forward from the audit. The "
             'audit macro delta ' + ' / '.join(report['superseded_audit_nutrition_delta'][f] for f in NUTRIENTS)
             + ' is recorded as superseded, not reused.', '',
             '## Catalog', '', '| Code | Field | Before | After | name_en (unchanged) |', '|---|---|---|---|---|',
             f"| 4016 | name_vi | {diff['before']} | {diff['after']} | `{report['catalog_name_en']['4016']}` |", '',
             'Every other column is asserted byte-for-byte unchanged: '
             f"{', '.join('`' + c + '`' for c in report['catalog_unchanged_columns'])}. Catalog row "
             f"count stays {report['catalog_count']}.", '',
             f"`{report['forbidden_name']['name']}` was **not** used: it {report['forbidden_name']['reason']}. "
             f"Qwen mapper rules after the repair: {report['qwen_mapper']['active']} active / "
             f"{report['qwen_mapper']['disabled']} disabled, unchanged, with that rule still disabled and "
             '`map_clean_to_master` still unresolved for all three of its terms.', '',
             'Colliding display names before: ' + ', '.join(f'`{n}`' for n in report['duplicate_names_before']) +
             '. After: ' + ', '.join(f'`{n}`' for n in report['duplicate_names_after']) +
             ' — unchanged; `Cải xanh` is unique in the catalog and `Dưa chuột (dưa leo)` was never a '
             'duplicate of 4027 `Dưa chuột`, which is why the corruption survived a duplicate-name sweep.', '',
             '## Exact alias changes', '',
             f"{report['alias_actions']} actions. Map size {report['alias_map_size_before']} − "
             f"{len(report['alias_diff']['removed'])} removed + {len(report['alias_diff']['added'])} added = "
             f"{report['alias_map_size']}.", '',
             '| Action | Alias | Before | After |', '|---|---|---|---|']
    for action, entries in report['alias_diff'].items():
        for alias, change in entries.items():
            lines.append(f"| {action} | {alias} | {change['before'] or '—'} | {change['after'] or '—'} |")
    lines += ['', 'Reviewed aliases that were already correct and stay put: ' +
              ', '.join(f'`{k}` → {v}' for k, v in report['alias_keeps'].items()) + '.', '',
              f"**{report['no_new_alias_to_4094']['invariant']}.** "
              + report['no_new_alias_to_4094']['reason'] +
              ' Its keys (' + ', '.join(f'`{k}`' for k in report['no_new_alias_to_4094']['keys_on_4094']) +
              ') are asserted unchanged, and so is its 106-row population.', '',
              'Removing the spinach and kale keys does **not** make those phrases unmatched: ' +
              '; '.join(f"`{k}` was {v['before']} and now reaches {v['after']} at the {v['stage']} stage"
                        for k, v in report['alias_removal_fallthrough'].items()) +
              '. That is exactly why the 31 rows are ID-pinned curated clears and the removal is not '
              'left to define behaviour.', '',
              'The added key `' + LONG_REVIEWED_ALIAS + '` is deliberately long: it is the '
              'parser-damaged cleaned text of exactly one reviewed row. A broad generic key in its '
              'place would claim rows nobody reviewed. Generic `cải` → 4013 is untouched.', '',
              '## Processed rows and nutrition', '',
              'Nutrition sums include known values only; missing values remain null. Every populated value is '
              "the live target catalog column scaled by the row's own weight through "
              '`nlp.nutrition.scale_nutrition` — no second rounding convention is implemented, and the '
              "extra row's delta is measured, never inferred from its textual quantity. Exact "
              f"before/after records for all {report['rows_written']} ingredient rows and "
              f"{report['recipes_touched_including_name_refresh']} recipes are in "
              '[applied_fix.json](applied_fix.json).', '',
              '| Cohort | Source | Target | Provenance | Rows | Recipes | kcal | Protein | Fat | Carbs |',
              '|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for name, c in report['cohorts'].items():
        lines.append(f"| {name} | {c['source_code']} | {c['target_code']} | {c['provenance']} | "
                     f"{c['row_count']} | {c['recipe_count']} | "
                     + ' | '.join(c['nutrition'][f]['known_sum_delta'] for f in NUTRIENTS) + ' |')
    lines += ['', '| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |',
              '|---|---:|---:|---:|---:|']
    for field, n in report['combined_nutrition_all_rows'].items():
        lines.append(f"| {field} | {n['before_known_sum']} | {n['after_known_sum']} | {n['known_sum_delta']} | "
                     f"{n['before_null_count']} → {n['after_null_count']} |")
    lines += ['', 'Null movement is the 35 clears (value → null on all four nutrients) and the five '
              'UNMATCHED recoveries (null → value on all four). `fat_g` moves nine further values to '
              'null: 4109 `Rau cải thảo` and 4115 `Dưa cải bắp` publish no `fat_g` column at all, so '
              'the eight fresh-napa rows and the one salted-napa row correctly store a null rather '
              'than a zero — AGENTS.md section 9. No zero-fill anywhere.', '',
              'Corpus-wide null counts after: ' + json.dumps(report['corpus_nulls']) + '.', '',
              '## The 35 curated clears', '',
              '27 spinach rows, four kale rows, three collision rows and one dried salted napa row. '
              'Neither spinach nor kale exists anywhere in the 750-row catalog, and the three '
              'collision rows (two broccoli, one mizuna) have no trustworthy target because 4094 is '
              'itself display-name corrupted. Picking a component or a neighbour would be exactly the '
              'forced coverage AGENTS.md section 5 rejects. Each is pinned by exact id, exact raw '
              'text and a complete before record, and each carries the full UNMATCHED contract '
              'afterwards: blank code, blank name, `UNMATCHED`, blank confidence (never `0.0`) and '
              'four null nutrients, with raw text, cleaned name, quantity/unit, preparation note and '
              'estimated weight preserved.', '',
              '**All 35 are intentionally NOT matcher-reproducible**, and no broad guard is added to '
              'reproduce them: ' +
              '; '.join(f"{k} would reach {v['matcher_would_reach']}"
                        for k, v in report['non_reproducible'].items()
                        if k in ('spinach', 'kale', 'collision', DRIED_SALTED_NAPA_ROW)) +
              '. A guard wide enough to catch these lines would reach rows nobody reviewed.', '',
              '## The two reviewed non-reproducible repairs', '']
    for key in (GREEN_CABBAGE_ROW, SALTED_NAPA_ROW):
        entry = report['non_reproducible'][key]
        lines.append(f"- **{key}** → stored `{entry['stored']}`, matcher would reach "
                     f"`{entry['matcher_would_reach']}`. {entry['reason']}")
    lines += ['', '## Final populations', '', '| Code | Rows |', '|---|---:|']
    for code, count in report['populations'].items():
        lines.append(f'| {code} | {count} |')
    lines += ['', 'The repaired 4016 carries 60 rows: 40 recovered from 4011, five from 4015, five '
              'recovered from stored-UNMATCHED, and the 10 deferred residual rows below.', '',
              f"Recipe rollups: {report['recipe_status']['recipes_with_changed_missing_count']} recipes "
              f"change `missing_nutrition_count` and "
              f"{report['recipe_status']['recipes_with_status_label_changed']} cross a "
              'COMPLETE/PARTIAL/INCOMPLETE threshold. Every transition is measured from the ingredient '
              'rows and pinned; none is forced.', '',
              '## The 10 deferred residual 4016 rows', '',
              'Five `cải con` and five `cải thìa`-family rows stay on the repaired 4016 and only '
              'refresh their stale stored display name to `Cải xanh` — code, provenance and all four '
              'nutrients are byte-identical. They stay deferred because the bok-choy duplicate 4015 '
              'vs 4135 is unresolved and `cải con` remains domain-ambiguous.', '',
              '## Downstream hard-coded cucumber code', '',
              '| File | Occurrences | on 4016 | on 4027 |', '|---|---:|---:|---:|']
    for path, values in report['downstream_hard_codes'].items():
        if isinstance(values, dict) and 'occurrences' in values:
            lines.append(f"| {path} | {values['occurrences']} | {values['on_4016']} | {values['on_4027']} |")
    lines += ['', 'One live pantry entry bought `dưa chuột` at 4016, which publishes '
              '`Mustard greens, raw`. It now points at 4027. `src/` is re-scanned on every run for '
              'any `("dưa chuột"|"dưa leo", "<code>")` pair, and any other live occurrence fails the '
              'batch closed.', '',
              '## Protecting the reviewed clear from a future Qwen pass', '',
              f"Clearing `{report['qwen_recovery_protection']['row']}` made it Qwen-eligible for "
              'the first time: it now has no master link, and the Qwen extraction cache carries an '
              f"output for its line. Measured against the live pipeline, the mapper resolves that "
              f"output to {report['qwen_recovery_protection']['would_reach']} "
              f"`{report['qwen_recovery_protection']['would_reach_name']}` -- FRESH napa -- and "
              'before this was added the recovery block produced a candidate for it. A Qwen pass '
              'would have silently restated the reviewed clear as a wrong match.', '',
              f"The protection is production logic, not a test assertion: the exact reviewed line "
              f"`{report['qwen_recovery_protection']['raw_text']}` is pinned in "
              f"`{report['qwen_recovery_protection']['mechanism']}` and refused by "
              f"`{report['qwen_recovery_protection']['enforced_by']}` with the reason "
              f"`{report['qwen_recovery_protection']['reason']}`. It refuses the line whatever the "
              'mapper resolves it to, because the reviewed claim is that no exact catalog identity '
              'exists for it at all -- not that one particular code is wrong.', '',
              f"The table holds {report['qwen_recovery_protection']['excluded_line_count']} line. "
              'It is keyed on the whole raw line and nothing else: a rule on the cleaned output '
              '`cải thảo` would block every fresh napa row, and a rule on `muối` or `khô` would '
              'block salt-pickled napa and kimchi, which do have catalog identities (4115, 20034). '
              'Asserted still eligible: ' +
              ', '.join(f'`{raw}` → {code}'
                        for raw, code in report['qwen_recovery_protection']['still_allowed'].items())
              + '.', '',
              '## Audit evidence hygiene', '',
              '`WRONG["4016"]` in `scripts/eda/audit_qwen_matching.py` is **not** retired: 4016 is '
              'still the wrong home for the rows that remain on it. Its display name becomes '
              f"`{report['audit_evidence']['wrong_4016'][0]}` and its synonym list narrows to "
              f"`{report['audit_evidence']['wrong_4016'][1]}` — the cleaned names the "
              f"{len(report['audit_evidence']['residual_4016_rows'])} surviving reviewed rows actually "
              'carry. `cải thảo` and `lá cải thảo` are dropped because those rows are gone, and the '
              'one row that would have justified keeping `cải thảo` is now cleared. `cải thìa chua` '
              'is deliberately absent: the existing compound/preparation logic already holds it in '
              'class B, and widening this regex would relabel other rows.', '',
              'Re-measured against the repaired corpus: '
              + json.dumps({k: report['audit_evidence'][k] for k in ('qwen_rows', 'class_counts', 'class_recipes')},
                           ensure_ascii=False)
              + '. Pre-C1: ' + json.dumps(report['audit_evidence']['superseded'], ensure_ascii=False)
              + ' — 19 rows leave `QWEN_LLM_MATCH` (five `lá cải xanh`, eight napa and two kimchi rows '
              'are re-measured onto `PRESET_ALIAS_MATCH`; three collision rows and the dried salted '
              'napa row are cleared).', '',
              '## Matcher replay', '', 'Production shape: `match_batch(cleaned_name, '
              'raw_contexts=raw_text)`.', '']
    if report.get('matcher_classification'):
        counts = report['matcher_classification']['counts']
        lines += ['| Class | Rows |', '|---|---:|']
        for key, value in counts.items():
            lines.append(f'| {key} | {value} |')
        lines += ['', 'Class B is exactly the two reviewed non-reproducible repairs; class C is the 35 '
                  'curated clears; class D is the 10 deferred residual rows, which the matcher would '
                  'scatter across 4010, 4135, 4015 and 13013 and which this batch therefore does not '
                  'move. Every divergence records the code the matcher would have reached instead; the '
                  'full table is in [applied_fix.json](applied_fix.json). No global matcher or parser '
                  'fix is made.', '']
    lines += ['| Probe | Code | Method | Confidence |', '|---|---|---|---:|']
    for query, result in report.get('matcher_replay', {}).items():
        lines.append(f"| {query} | {result['code']} | {result['method']} | {result['confidence']} |")
    lines += ['', '## Deferred, recorded and unchanged', '']
    for key, why in report['deferrals'].items():
        lines.append(f'- **{key}.** {why}')
    lines += ['', '## Canonical propagation', '', '| Artifact | Changed logical records |', '|---|---:|']
    for name, values in report['canonical'].items():
        lines.append(f"| {name} | {values['changed_count']} |")
    estimate = report['superseded_audit_canonical']
    lines += ['', f"The {report['rows_written']} pinned rows span "
              f"{report['canonical']['recipe_canonical_mapping.csv']['canonical_groups_involved']} canonical "
              f"groups ({report['canonical']['recipe_canonical_mapping.csv']['canonical_groups_for_changed_rows']} "
              'for the changed rows alone), and all but '
              f"{report['canonical']['canonical_recipe_ingredients.csv']['reviewed_rows_absent']} appear in "
              '`canonical_recipe_ingredients.csv` — the others live in recipes canonicalisation '
              'deduplicated away. Canonical ID drift = 0; representative drift = 0.', '',
              'The audit quoted ' + json.dumps(estimate['estimate']) + ' for its 344-row plan. '
              'Measured for the approved state: ' + json.dumps(estimate['measured']) + '.', '',
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
    (out / 'applied_fix.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def git_state(root):
    def run_git(*args):
        return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=True).stdout
    check = run_git('diff', '--check')
    return dict(diff_check='passed' if not check.strip() else check.strip(),
                branch=run_git('rev-parse', '--abbrev-ref', 'HEAD').strip(),
                status_short=[line for line in run_git('status', '--short').splitlines() if line])


def run(apply=False, root=ROOT, out=OUT, tests=None):
    files, before_files, report = plan(root)
    if not apply:
        return report
    changed = [p for p in files if (files[p] != before_files[p] if p.suffix == '.json'
                                    else [logical(r) for r in files[p]] != [logical(r) for r in before_files[p]])]
    prior = out / 'applied_fix.json'
    cache = (root / CAT).with_name('catalog_embeddings_bkai.pt')
    tracked = subprocess.run(['git', 'ls-files', '--', str(cache.relative_to(root))], cwd=root,
                             capture_output=True, text=True, check=True).stdout.strip()
    require(not tracked, 'Embedding cache unexpectedly tracked; review version-control policy')
    if not changed and report['downstream_hard_codes']['pending'] == 0 and prior.exists():
        previous = read_json(prior)
        if previous.get('validation', {}).get('complete') and cache.exists():
            require(hashlib.sha256(cache.read_bytes()).hexdigest() == previous['embeddings']['sha256'],
                    'Embedding cache drift')
            require(embedding_input_digest(files[CAT]) == previous['embeddings']['input_sha256'],
                    'Embedding catalog-input drift')
            verify_canonical(root)
            previous = dict(previous, rows_pending=0, idempotent=True)
            previous['git'] = git_state(root)
            if tests:
                previous['tests'] = tests
            write_report(previous, out)
            return previous
        report = dict(previous, rows_pending=0)
    interim_before = interim_digest(root)
    # Catalog first, then aliases, then the downstream hard-code, then processed
    # rows and rollups. Canonical is regenerated only after the rows verify.
    for path in (CAT, ALIASES, DATA / 'recipe_ingredients.csv', DATA / 'recipe_ingredients.json',
                 DATA / 'recipes.csv', DATA / 'recipes.json'):
        if path not in changed:
            continue
        if path.suffix == '.csv':
            write_csv(root / path, files[path], list(files[path][0]))
        else:
            write_json(root / path, files[path])
    report['downstream_hard_codes'] = downstream_state(root, repair=True)
    require(report['downstream_hard_codes']['pending'] == 0, 'Downstream hard-code repair did not complete')
    report['status'] = 'processed_applied_validation_pending'
    write_report(report, out)
    import torch
    matcher = VietnameseIngredientMatcher(root / CAT)
    cache.unlink(missing_ok=True)
    matcher._init_model()
    tensor = torch.load(cache, map_location=matcher.device, weights_only=True)
    require(list(tensor.shape) == [750, 768] and len(matcher.catalog) == 750,
            f'Embedding shape drift: {tensor.shape}')
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
    report['matcher_replay'], report['matcher_classification'] = replay(matcher, report)
    require(plan(root)[2]['rows_pending'] == 0, 'Processed repair failed read-back')
    report['rows_pending'] = 0  # The report describes the applied state, not the plan.
    for command in (['scripts/canonicalize_recipes.py'], ['scripts/export_canonical_json.py']):
        subprocess.run([sys.executable, *command], cwd=root, check=True)
    verify_canonical(root)
    require(interim_before == interim_digest(root), 'Historical/interim data changed')
    report['interim'] = interim_before
    report['status'] = 'applied'
    report['validation'] = dict(complete=True, processed_parity=True, canonical_parity=True,
                                canonical_check=True, canonical_determinism=True, interim_unchanged=True,
                                catalog_name_vi_only=True, embeddings_rebuilt=True,
                                downstream_hard_codes_repaired=EXPECTED_DOWNSTREAM_REPOINTS,
                                blast_radius_measured_against='reviewed manifest, not git HEAD')
    report['git'] = git_state(root)
    if tests:
        report['tests'] = tests
    write_report(report, out)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--tests', help='JSON summary of the validation test run, recorded in the report')
    args = parser.parse_args()
    report = run(apply=args.apply, tests=json.loads(args.tests) if args.tests else None)
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ('row_outcomes', 'recipe_outcomes', 'affected_recipe_ids',
                                   'matcher_replay', 'matcher_classification', 'cohorts')},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
