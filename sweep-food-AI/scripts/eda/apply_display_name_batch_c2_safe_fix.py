"""DISPLAY_NAME_BATCH_C2: reviewed 92-row / 91-recipe repair; dry-run by default.

Catalog code 4010 is the raw Viện Dinh Dưỡng row `Cabbage, common, raw`, but its
Vietnamese display name reads `Cần tây` -- celery -- which is 4018's name, and
4018 already carries it. Two codes therefore published one display name, and the
one that published it wrongly is the one the alias map leaned on: eighteen alias
keys and 89 processed rows were organised around 4010 as if it were celery.

The repair is `name_vi` only: 4010 becomes `Cải bắp trắng`. Code, `name_en`,
both category columns and every nutrition column are asserted byte-for-byte
unchanged, so the identity being published is the one the source row already
asserts and no nutrition is restated by the rename itself.

`Cải bắp` is deliberately NOT the chosen name. `_QWEN_MAPPER_RULES` carries a
disabled rule `("bắp cải",) -> 4010 "Cải bắp"`, and the A1 identity check
reactivates a rule the moment the catalog's live `name_vi` equals the hard-coded
name. Naming 4010 `Cải bắp` would silently switch that rule back on as a side
effect of a display-name repair. `Cải bắp trắng` is the reviewed name: it states
the white/common cultivar the row's own `name_en` asserts, it distinguishes 4010
from 4011 `Cải bắp đỏ` and 4012 `Cải bắp trắng, khô`, and it leaves the Qwen
mapper at 29 active / 20 disabled rules with that rule still disabled. The batch
asserts all three of those, before and after.

The alias plan is exactly 18 actions. Nine celery keys (`cần tàu`, `rau cần
tây`, `cần tây bẹ`, ...) are repointed off 4010 onto 4018, where their own words
already pointed. `bắp cải` is repointed off 20035 `Bắp cải tím (cải tím)` -- red
cabbage -- onto the repaired 4010: bare `bắp cải` is white cabbage, and the red
identity keeps every key that says `tím`. Three keys are removed outright
(`tây`, and the two collapsed compound lines `mĩ 1 cây cần tây` and `rau ngổ
hoặc cần tây`), and five white-cabbage keys are added. 4672 - 3 + 5 = 4674.

`cần tàu == cần tây` is recorded as reviewed evidence, from raw text and not
from the alias map: row 03f24d73 reads `1 ít rau cần tây (hay cần tàu)`, where
the author names both terms for one ingredient on one line. AGENTS.md section 7
forbids inferring synonym equivalence from two keys sharing a target, so the
manifest carries the raw line, the row id and an explicit
`inferred_from_alias_map: false`.

92 rows move, pinned by id with a complete before record and never selected by
code alone. 72 celery rows go to 4018 (71 keeping PRESET_ALIAS_MATCH / 0.98; the
compound row 3f0791d5 loses the alias that claimed it and is re-measured against
the real matcher, which lands it on SUBPHRASE_CATALOG_MATCH / 0.95). Ten
reviewed single-identity white-cabbage rows stay on the repaired 4010 and only
refresh their display name -- zero nutrition delta. One explicit `Bắp cải tím`
row moves to 20035, one bare `Ít bắp cải` row is recovered from 20035 onto 4010,
and two stored-UNMATCHED white-cabbage rows are recovered because the new alias
map claims them and leaving them stored-UNMATCHED would manufacture a divergence
C2 itself introduced.

Six rows are cleared to UNMATCHED: an either-or line, two compounds, two dish
titles and a multi-identity line. Their identity is not a component this batch
gets to pick. Two of the six (`bắp cải` on an `A hoặc B` line, and a dish title)
ARE claimable by the new alias map, so the clears are recorded as intentionally
NOT matcher-reproducible. No broad guard is added to reproduce them; that would
be a separate reviewed decision and would reach rows nobody reviewed.

Blast radius is measured against the manifest-reconstructed before state, never
against git HEAD: a version-control diff is only an invariant while the batch is
unstaged and inverts the moment it lands. Catalog, aliases, downstream hard-coded
cabbage codes, processed rows and rollups are all planned before any write, and
the populations, nutrition delta, null transitions, recipe status and canonical
radius are checked against the reviewed figures first. --apply writes in that
order, rebuilds the untracked embedding cache, replays the real matcher on both
routes, exports canonical CSV/JSON and runs canonical --check. A completed rerun
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
from nlp.qwen_matching import _QWEN_MAPPER_RULES, build_mapper_rules, map_clean_to_master
from scripts.eda.apply_qwen_safe_fix import (
    read_csv, read_json, write_json, recompute_recipe_rollups, _apply_rollups, _new_totals,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
from scripts.canonicalize_recipes import compose_reviewed_aliases

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('display_name_batch_c2_reviewed_state.json')
OUT = ROOT / 'reports/eda/display_name_batch_c2_fix'
CAT = Path('data/processed/viendinhduong/master_ingredients_nutrition.csv')
ALIASES = CAT.with_name('ingredient_alias_map.json')
DATA = Path('data/processed/recipes')
NUTRIENTS = ('calories', 'protein_g', 'fat_g', 'carbs_g')

# name_vi only. 4010's name_en is `Cabbage, common, raw`; the display name it
# carries today belongs to 4018 `Celery, raw`, which still holds it.
CATALOG_PATCHES = {'4010': {'name_vi': 'Cải bắp trắng'}}
# The name the repair must NOT use, and why. `_QWEN_MAPPER_RULES` carries a
# disabled rule ("bắp cải",) -> 4010 "Cải bắp"; build_mapper_rules() reactivates
# a rule as soon as the live catalog name_vi equals the hard-coded name, so this
# exact string would switch a Qwen rule back on as a side effect of a rename.
FORBIDDEN_CATALOG_NAME = 'Cải bắp'
QWEN_RULE_MUST_STAY_DISABLED = (('bắp cải',), '4010', 'Cải bắp')
EXPECTED_QWEN_RULE_COUNTS = {'active': 29, 'disabled': 20}
# Catalog display names that already collide and stay deferred. `cần tây` leaves
# this set -- resolving that collision is exactly what C2 does.
EXPECTED_DUPLICATE_NAMES_BEFORE = {'cần tây', 'nấm kim châm', 'thịt trâu, đùi'}
EXPECTED_DUPLICATE_NAMES_AFTER = {'nấm kim châm', 'thịt trâu, đùi'}

# --- the 18 reviewed alias actions -----------------------------------------
# A. Nine celery keys off 4010 onto 4018, plus `bắp cải` off red cabbage onto the
#    repaired white-cabbage identity. `bắp cải` is approved in C2, not deferred.
ALIAS_REPOINTS = {
    'cần tàu': '4018', 'rau nêm cần tàu': '4018', 'rau cần tây': '4018', 'rau cần tây to': '4018',
    'cần tây bẹ': '4018', 'cần tây bào vỏ': '4018', 'cần tây bẹ cắt lát xéo': '4018',
    'cần tây tước xơ cắt lát': '4018', 'lá cần tây non': '4018',
    'bắp cải': '4010',
}
# C. Three keys with no defensible single identity. `tây` is a bare fragment,
#    the other two are collapsed compound recipe lines that became alias keys.
ALIAS_REMOVALS = ('tây', 'mĩ 1 cây cần tây', 'rau ngổ hoặc cần tây')
# D. Five white-cabbage keys the repaired identity now earns.
ALIAS_ADDITIONS = {
    'cải bắp': '4010', 'bắp cải trắng': '4010', 'bắp cải nhỏ': '4010',
    'bắp cải trái tim': '4010', 'bắp cải trộn': '4010',
}
# E. Reviewed keeps: valid today, valid after, and asserted both times. `cải` ->
#    4013 and `cải trắng` -> 4021 are listed deliberately -- they belong to C3 and
#    this batch must prove it did not touch them.
ALIAS_KEEPS = {
    'cải bắp trắng tươi': '4010',
    'cần tây': '4018', 'cần tây tươi': '4018', 'cần tây cắt nhỏ': '4018', 'cần tây cắt hạt lựu': '4018',
    'bắp cải tím': '20035', 'cải tím': '20035', 'rau cải tím': '20035', 'bắp cải tím cải tím': '20035',
    'cải tím cắt sợi': '20035', 'cải tím xắt sợi': '20035', 'cải tím bào mỏng': '20035',
    'cải': '4013', 'cải trắng': '4021', 'cải bắp đỏ': '4011', 'cải bắp trắng khô': '4012',
    'cải khô': '4012', 'cần ta': '4017', 'cần': '4017',
}
EXPECTED_ALIAS_ACTIONS = 18
ALIAS_MAP_SIZE_BEFORE = 4672
# C2's own arithmetic: 4672 - 3 removed + 5 added = 4674.
ALIAS_MAP_SIZE_AFTER = 4674
# DISPLAY_NAME_BATCH_C1 landed after C2 and legitimately moved the live map again:
# it removes the 2 spinach/kale keys and adds 8 mustard-green/napa/kimchi keys, so
# the size C2 now reads back is 4674 - 2 + 8 = 4680. C2's own 18 actions are
# unchanged and still asserted key by key below; only the size of the map they
# live in moved, so the live-size checks use this value and the arithmetic above
# is kept as C2's own result.
# C3 repaired parser-damaged white-cabbage rows and added four aliases.
ALIAS_MAP_SIZE_LIVE = 4684

# cohort -> (source code or None for UNMATCHED, target code or None for a clear,
#            reviewed row count, provenance policy)
COHORTS = {
    'celery_4010_to_4018': ('4010', '4018', 71, 'preserved'),
    'celery_compound_subphrase_4010_to_4018': ('4010', '4018', 1, 'measured'),
    'ambiguous_clear_to_unmatched': ('4010', None, 6, 'cleared'),
    'white_cabbage_keep_4010': ('4010', '4010', 10, 'preserved'),
    'red_cabbage_4010_to_20035': ('4010', '20035', 1, 'preserved'),
    'white_cabbage_20035_to_4010': ('20035', '4010', 1, 'measured'),
    'white_cabbage_unmatched_recovery': (None, '4010', 2, 'measured'),
}
EXPECTED_ROWS = 92
EXPECTED_RECIPES = 91
# The compound line `1 trái bắp mĩ, 1 cây cần tây` lost the alias that claimed it
# (`mĩ 1 cây cần tây`), so its provenance is re-measured rather than carried
# forward: the old 0.98 described a route that no longer exists.
SUBPHRASE_ROW_ID = '3f0791d5-d33a-465b-87d1-f2716af835d7'
SUBPHRASE_RAW_TEXT = '1 trái bắp mĩ, 1 cây cần tây'
SUBPHRASE_MATCH = {'code': '4018', 'method': 'SUBPHRASE_CATALOG_MATCH', 'confidence': 0.95}
# The three rows whose stored identity is re-derived from the repaired alias map.
RECOVERY_ROWS = {
    'cbd724fa-0418-42c8-8f41-0d7f42d36a77': ('Ít bắp cải', 'bắp cải'),
    '0388cb60-cef5-4127-846f-9c2bfe4e929c': ('Bắp cải cắt sợi nhỏ: 30g', 'bắp cải'),
    'a8e5fc9c-b796-4b6b-a911-5e7434fadd51': ('Bắp cải trái tim 50g', 'bắp cải trái tim'),
}
RECOVERY_MATCH = {'code': '4010', 'method': 'PRESET_ALIAS_MATCH', 'confidence': 0.98}
RED_CABBAGE_ROW_ID = '2bab0383-53ee-4eb2-9e25-aa3f9950e532'
RED_CABBAGE_RAW_TEXT = 'Bắp cải tím 8 lá'

# DISPLAY_NAME_BATCH_C1 landed after C2 and legitimately moved several of these.
# C2's own 92 rows did not move: 4018, 20035, 4012, 4013, 4017 and 4021 are
# unchanged. 4010 gains exactly one row -- C1 moved 633ea6e1 `Bắp cải xanh 1/2
# cái`, green HEAD cabbage, off red cabbage 4011 onto C2's repaired white-cabbage
# identity. 4011 is emptied and 4015/4016/4109 are re-homed by C1, which owned
# those identities all along; 4027, 4115 and 20034 are C1's new populations and
# are pinned here so they cannot drift either.
# C3 repaired parser-damaged white-cabbage rows; own reviewed row sets remain unchanged.
EXPECTED_POPULATIONS = {
    '4010': 105, '4018': 177, '20035': 33,
    # Sibling cabbage/celery identities this batch must not disturb, and the two
    # C3 codes (`cải` -> 4013, `cải trắng` -> 4021) it must prove it left alone.
    '4011': 0, '4012': 5, '4013': 54, '4017': 8, '4021': 128,
    # C1's identities, out of scope here and pinned so they cannot drift in.
    '4015': 11, '4016': 60, '4027': 270, '4109': 73, '4115': 1, '4135': 59, '20034': 75,
    'UNMATCHED': 8495,
}
# The one C1 row that entered a C2-repaired identity, pinned by exact id so C2's
# "the 4010 population is exactly my 13 reviewed rows" check stays fail-closed.
C1_ROW_ADDED_TO_4010 = '633ea6e1-a2c9-4708-85e1-9a614f1dfdb7'
# The rest of what C1 legitimately superseded in C2's frozen manifest. C2 asserted
# these identities were out of its scope and pinned their pre-C1 state; C1 owned
# them and has now repaired them, so these are the values C2 must find instead.
# The assertions are kept and still fail closed -- only the expected values moved.
C1_SUPERSEDED_CATALOG = {'4016': {'name_vi': 'Cải xanh'}}
C1_SUPERSEDED_IDENTITY_ROW_COUNTS = {'4015': 11, '4016': 60, '4109': 73, '4135': 59}
# C1 emptied 4011 `Cải bắp đỏ`: 40 of its rows were genuine mustard greens and went
# to the repaired 4016, and the 41st (C1_ROW_ADDED_TO_4010) was green head cabbage
# and went to 4010. C2's frozen 41-row keep set is superseded wholesale, so the
# population it must now find on that code is empty.
C1_EMPTIED_SIBLING_CODES = {'4011'}
# C1 also changed catalog TEXT at 4016, so the untracked embedding cache was
# legitimately rebuilt and no longer carries the digest C2 recorded. The authority
# for the live cache is the batch that last built it; both digests are accepted and
# nothing else is, so an idempotent C2 rerun still fails closed on real drift.
C1_EMBEDDING_REPORT = ROOT / 'reports/eda/display_name_batch_c1_fix/applied_fix.json'


def accepted_embedding_digests(previous):
    accepted = {'sha256': {previous['embeddings']['sha256']},
                'input_sha256': {previous['embeddings']['input_sha256']}}
    if C1_EMBEDDING_REPORT.exists():
        later = read_json(C1_EMBEDDING_REPORT)['embeddings']
        for key in accepted:
            accepted[key].add(later[key])
    return accepted
EXPECTED_NUTRITION_DELTA = {
    'calories': '1184.6', 'protein_g': '135.8', 'fat_g': '6.3', 'carbs_g': '173.5',
}
EXPECTED_COHORT_NUTRITION_DELTA = {
    'ambiguous_clear_to_unmatched': {
        'calories': '-153.0', 'protein_g': '-7.6', 'fat_g': '-0.3', 'carbs_g': '-29.4'},
    'celery_4010_to_4018': {
        'calories': '1355.8', 'protein_g': '145.5', 'fat_g': '5.3', 'carbs_g': '190.6'},
    'celery_compound_subphrase_4010_to_4018': {
        'calories': '9.0', 'protein_g': '1.0', 'fat_g': '0.1', 'carbs_g': '1.2'},
    'red_cabbage_4010_to_20035': {
        'calories': '-60.0', 'protein_g': '-4.8', 'fat_g': '1.3', 'carbs_g': '5.9'},
    'white_cabbage_20035_to_4010': {
        'calories': '4.0', 'protein_g': '0.3', 'fat_g': '-0.1', 'carbs_g': '-0.4'},
    # The reviewed keeps move no nutrient at all: the code does not change and the
    # catalog's nutrition columns are untouched, so only the display name moves.
    'white_cabbage_keep_4010': {
        'calories': '0.0', 'protein_g': '0.0', 'fat_g': '0.0', 'carbs_g': '0.0'},
    'white_cabbage_unmatched_recovery': {
        'calories': '28.8', 'protein_g': '1.4', 'fat_g': '0.0', 'carbs_g': '5.6'},
}
# Six clears take four values to null each; the two recoveries take four nulls to
# a value each. Nothing else moves, in either direction.
EXPECTED_NULL_TRANSITIONS = {f: (2, 6) for f in NUTRIENTS}
EXPECTED_VALUE_TO_NULL = {f: 6 for f in NUTRIENTS}
EXPECTED_NULL_TO_VALUE = {f: 2 for f in NUTRIENTS}
# The recovered rows' fat is a REAL scaled zero, not a coerced null: 4010 carries
# 0.09 g/100 g, and 0.09 * 0.30 and 0.09 * 0.50 both round to 0.0 at the project's
# one-decimal convention. AGENTS.md section 4: numeric 0 is a real zero.
EXPECTED_RECOVERY_FAT = '0.0'
# Superseded by DISPLAY_NAME_BATCH_C1: its 35 clears minus 5 mustard-green
# recoveries are a net +30 on every nutrient, and fat_g gains a further 9 because
# the eight fresh-napa rows (4109) and the one salted-napa row (4115) move onto
# catalog identities that publish no fat_g value at all. C2's own 92 rows and its
# own six clears / two recoveries are unaffected and still asserted separately.
EXPECTED_CORPUS_NULLS = {
    'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454,
}

# Five clear-bearing recipes gain missing rows (2b3ed220 holds two of the six
# clears) and the two recovery recipes lose one each. No recipe crosses a label
# threshold, so there is no nutrition_status transition anywhere.
EXPECTED_MISSING_COUNT_TRANSITIONS = {
    '1022eb07-c5b1-4fac-abec-6de502e4289a': (4, 5),
    '2b3ed220-c1c1-44fa-838e-3844ddb1b611': (2, 4),
    '86aa60e9-62eb-45c9-ac47-33a73a9d7d54': (2, 3),
    'd5ba12dc-cccb-4621-b71c-f8ede7bceb40': (1, 2),
    'fd85d160-cd83-4f76-80a3-0e12b1fb2757': (1, 2),
    '2b0fe656-9cd9-46d2-b5ca-90659d0a79b2': (4, 3),
    'ae835445-9dec-4a32-b417-ad0f653904ea': (2, 1),
}
EXPECTED_STATUS_LABEL_TRANSITIONS = {}
EXPECTED_CANONICAL = {
    'canonical_recipe_ingredients.csv': 92,
    # 81, not 91: all 91 affected recipes are canonical representatives, but the
    # ten reviewed KEEP rows move no nutrient, so their recipes' totals -- the
    # only thing canonical_recipes.csv carries from an ingredient row -- do not
    # move either. 91 canonical recipes are TOUCHED; 81 change content.
    'canonical_recipes.csv': 81,
    'recipe_canonical_mapping.csv': 7,
}
EXPECTED_CANONICAL_GROUPS = 91
EXPECTED_CANONICAL_INGREDIENT_ROWS_ABSENT = 0
EXPECTED_CANONICAL_TOTALS = {'canonical_recipes.csv': 5479, 'recipe_canonical_mapping.csv': 5641}
# Only the six clears and the two recoveries move a mapping quality counter: they
# are the rows whose UNMATCHED state changes. The 84 identity remaps swap one
# valid code for another and move no counter.
EXPECTED_MAPPING_CHANGED_FIELDS = {
    'candidate_score', 'selection_score', 'unmatched_count', 'valid_master_match_count',
    'valid_match_rate', 'qwen_match_count', 'nutrition_anomaly_count',
    'negative_nutrition_anomaly_rate', 'negative_unmatched_rate',
}
# The pre-implementation review quoted "canonical recipes changed: 91". That is
# the number of canonical groups the 92 rows TOUCH, which this batch measures and
# asserts as EXPECTED_CANONICAL_GROUPS. The number of canonical_recipes.csv rows
# whose CONTENT changes is 81, for the reason recorded above. Both are pinned so
# neither reading can drift unnoticed.
REVIEW_ESTIMATE_CANONICAL = {
    'estimate': {'canonical_recipes_changed': 91},
    'measured': {'canonical_recipe_groups_touched': 91, 'canonical_recipes_csv_rows_changed': 81},
    'cause': ('The ten reviewed KEEP rows stay on code 4010 and only refresh their display '
              'name, so their recipes carry an identical nutrition rollup before and after. '
              'canonical_recipes.csv holds totals, not ingredient names, so those ten '
              'recipes are touched without changing content.'),
}

# --- downstream hard-coded cabbage codes -----------------------------------
# Five live fresh-cabbage pantry entries point at 4012 `Cải bắp trắng, khô` --
# DRIED cabbage at 301 kcal/100 g -- for a fresh vegetable a household buys by
# the 200-600 g head. The repaired 4010 is the fresh identity they meant.
DOWNSTREAM_BEFORE = '("bắp cải", "4012"'
DOWNSTREAM_AFTER = '("bắp cải", "4010"'
DOWNSTREAM_FILES = {
    Path('src/recommendation/pantry_simulator.py'): 4,
    Path('src/recommendation/benchmark_generator.py'): 1,
}
EXPECTED_DOWNSTREAM_REPOINTS = 5
# The cucumber pantry entry is C1's, not C2's. C2 asserted it was untouched at
# `("dưa chuột", "4016", ...)`; DISPLAY_NAME_BATCH_C1 has since landed and repointed
# it onto the cucumber identity 4027, so the value C2 must now find unchanged is the
# repaired one. The assertion is kept, not deleted: C2 still proves it did not write
# that line.
DOWNSTREAM_OUT_OF_SCOPE = '("dưa chuột", "4027"'
# Any other live fresh-cabbage hard-coding is drift: fail closed rather than
# repair something nobody reviewed.
DOWNSTREAM_SCAN = re.compile(r'\(\s*"bắp cải"\s*,\s*"(\d+)"')
DOWNSTREAM_SCAN_ROOT = Path('src')

# --- audit evidence hygiene -------------------------------------------------
# scripts/eda/audit_qwen_matching.py carried 4010 in its WRONG table keyed on the
# corrupt display name `Cần tây`. That signature is stale the moment 4010 is
# renamed, so it is retired and replaced by the narrow VALID pattern for the
# repaired identity. Evidence hygiene only: no production matcher behaviour moves.
AUDIT_VALID_NAME = 'Cải bắp trắng'
AUDIT_VALID_SYNONYMS = 'bắp cải|bắp cải trắng|bắp cải nhỏ|bắp cải trái tim|bắp cải trộn'
# Measured, not assumed: exactly one surviving QWEN_LLM_MATCH row on 4010 has raw
# text simple enough to corroborate its own cleaned name, so exactly one row
# moves B -> C. Every other reviewed keep stays B on unverified raw residue.
EXPECTED_AUDIT_UPGRADES = {'99d4a0bf-10f1-45a1-b1b6-8ece316b1121': ('B', 'C')}

# The reviewed identities and every sibling that must not move.
PROBES = {
    # Celery, repointed by this batch.
    'cần tây': '4018', 'rau cần tây': '4018', 'cần tàu': '4018', 'rau nêm cần tàu': '4018',
    'cần tây bẹ': '4018', 'lá cần tây non': '4018', 'rau cần tây to': '4018',
    'cần tây bào vỏ': '4018', 'cần tây bẹ cắt lát xéo': '4018', 'cần tây tước xơ cắt lát': '4018',
    'cần tây tươi': '4018', 'cần tây cắt nhỏ': '4018', 'cần tây cắt hạt lựu': '4018',
    # White cabbage, recovered by this batch.
    'cải bắp': '4010', 'cải bắp trắng': '4010', 'bắp cải': '4010', 'bắp cải trắng': '4010',
    'bắp cải nhỏ': '4010', 'bắp cải trái tim': '4010', 'bắp cải trộn': '4010',
    'cải bắp trắng tươi': '4010',
    # Siblings that must not move.
    'bắp cải tím': '20035', 'cải tím': '20035', 'rau cải tím': '20035',
    'cải bắp đỏ': '4011', 'cải bắp trắng khô': '4012', 'cải khô': '4012', 'cần ta': '4017',
    # C3's codes, deliberately untouched here.
    'cải': '4013', 'cải trắng': '4021',
    # C1's identities, which landed after C2 and must be unchanged BY C2. C1
    # repointed `dưa leo` onto cucumber 4027 and `cải xanh` / `cải bẹ xanh` onto the
    # repaired mustard-green 4016; those are C1's reviewed results, asserted here so
    # a later C2 rerun proves it did not disturb them.
    'dưa leo': '4027', 'dưa chuột': '4027', 'cải xanh': '4016', 'cải bẹ xanh': '4016',
    'cải thảo': '4109', 'cải thìa': '4135',
}
# Removing `tây` leaves a bare two-word fragment with no dictionary identity. No
# live row carries it -- measured, zero rows -- so it moves nothing, but the two
# routes disagree on where it lands. Recorded, not fixed: match()/match_batch()
# architecture is out of scope, and this batch may not introduce divergence on
# any phrase a live row actually uses.
KNOWN_ROUTE_DIVERGENCE = {
    'tây': {'before': '4010', 'single_after': '4018', 'batch_after': '20036', 'live_rows': 0},
}
# The two removed compound keys, and what the matcher does with them afterwards.
# Both belong to cleared rows: the stored state is UNMATCHED and the matcher
# verdict below is NOT reproduced into the corpus. Pinned so the divergence is
# recorded rather than discovered later.
NON_REPRODUCIBLE_CLEARS = {
    'rau ngổ hoặc cần tây': {'stored': 'UNMATCHED', 'matcher_would_reach': '4018',
                             'reason': 'either-or line naming two distinct herbs'},
    'bắp cải': {'stored': 'UNMATCHED', 'matcher_would_reach': '4010',
                'reason': 'two rows whose raw text names cabbage alongside another identity'},
}

DEFERRALS = {
    'c3_parser_damaged_white_cabbage_recovery': (
        'Bare `cải` -> 4013 and `cải trắng` -> 4021 are asserted unchanged here. Recovering '
        'parser-damaged white-cabbage rows hiding behind them is C3.'),
    'c1_cucumber_and_mustard_green_identities': (
        '4016 `Dưa chuột (dưa leo)` publishes `Mustard greens, raw` as its name_en. C1 owns '
        'that repair and lands after C2; its aliases, rows and audit evidence are untouched.'),
    '4011_vs_20035_duplicate_resolution': (
        '4011 `Cải bắp đỏ` and 20035 `Bắp cải tím (cải tím)` are both red cabbage. Their 41 '
        'and 33 rows are asserted stable; choosing a survivor is a separate domain decision.'),
    'parser_canonical_unit_map_bap': (
        'The parser treats `bắp` as a unit, which is what collapsed `1 trái bắp mĩ, 1 cây cần '
        'tây` into an alias key. Parser behaviour is not changed by this batch.'),
}
EXCLUSIONS = [
    '4016 / C1 cucumber-vs-mustard-green repair', 'parser CANONICAL_UNIT_MAP["bắp"]',
    '`cải` -> 4013 and `cải trắng` -> 4021 (C3)', 'C3 parser-damaged white-cabbage recovery',
    '4011 / 20035 duplicate resolution', '4015 / 4135 bok-choy duplicate',
    'spinach / kale catalog gaps', '4094 / 4096 corruption', 'bare măng', '4121 / 20077',
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
                for p in sorted((root/'data/interim').rglob('*')) if p.is_file()}
    blob = json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return {'files': len(manifest), 'sha256': hashlib.sha256(blob).hexdigest()}


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


def qwen_rule_state(catalog_rows):
    """Active/disabled split and the one rule that must stay disabled."""
    masters = {r['code']: r for r in catalog_rows}
    active, disabled = build_mapper_rules(masters)
    terms, code, name = QWEN_RULE_MUST_STAY_DISABLED
    require((terms, code, name) in _QWEN_MAPPER_RULES, 'The guarded Qwen rule is no longer declared')
    require(not any(r[:3] == (terms, code, name) for r in active), 'The `bắp cải` -> 4010 Qwen rule went active')
    require(any(r[:3] == (terms, code, name) for r in disabled), 'The `bắp cải` -> 4010 Qwen rule vanished')
    require(map_clean_to_master('bắp cải', active) == (None, None),
            'map_clean_to_master resolved `bắp cải` through the disabled rule')
    counts = {'active': len(active), 'disabled': len(disabled)}
    require(counts == EXPECTED_QWEN_RULE_COUNTS, f'Qwen mapper rule count drift: {counts}')
    return dict(counts, guarded_rule_disabled=True, map_clean_to_master_bap_cai=None)


def downstream_state(root, repair=False):
    """The five live fresh-cabbage hard-codings, planned or applied.

    Deterministic and idempotent: an already-repaired file reports zero pending
    occurrences and is not rewritten. A file that carries neither the reviewed
    before value nor the reviewed after value the expected number of times is
    drift, and fails closed rather than being partially rewritten.
    """
    measured, pending = {}, 0
    for path, count in DOWNSTREAM_FILES.items():
        text = (root/path).read_text(encoding='utf-8')
        before, after = text.count(DOWNSTREAM_BEFORE), text.count(DOWNSTREAM_AFTER)
        require(before + after == count, f'Downstream occurrence drift: {path} has {before + after}, want {count}')
        if repair and before:
            (root/path).write_text(text.replace(DOWNSTREAM_BEFORE, DOWNSTREAM_AFTER), encoding='utf-8')
            before, after = 0, count
        measured[str(path).replace('\\', '/')] = {'occurrences': count, 'on_4012': before, 'on_4010': after}
        pending += before
        # C1 owns the cucumber entry; prove this batch did not touch it.
        require(DOWNSTREAM_OUT_OF_SCOPE in text or path.name != 'pantry_simulator.py',
                f'C1 cucumber hard-coding disappeared from {path}')
    # Search again rather than trust the table: any other live fresh-cabbage
    # hard-coding is unreviewed drift.
    found = {}
    for path in sorted((root/DOWNSTREAM_SCAN_ROOT).rglob('*.py')):
        for code in DOWNSTREAM_SCAN.findall(path.read_text(encoding='utf-8')):
            found.setdefault(code, []).append(str(path.relative_to(root)).replace('\\', '/'))
    require(set(found) <= {'4010', '4012'}, f'Unreviewed fresh-cabbage hard-coded code: {sorted(found)}')
    require(sum(len(v) for v in found.values()) == EXPECTED_DOWNSTREAM_REPOINTS,
            f'Fresh-cabbage hard-coding count drift: {found}')
    measured['pending'] = pending
    measured['scanned_codes'] = {k: sorted(set(v)) for k, v in found.items()}
    return measured


def audit_evidence_state():
    """The retired 4010 WRONG signature and its narrow VALID replacement."""
    from scripts.eda import audit_qwen_matching as audit
    require('4010' not in audit.WRONG, 'The stale 4010 -> `Cần tây` WRONG signature is still declared')
    # DISPLAY_NAME_BATCH_C1 repaired 4016 and re-keyed its WRONG signature onto the
    # repaired display name. C2 still asserts it did not touch that entry -- only the
    # value it must find has been superseded by the batch that owns it.
    require(audit.WRONG['4016'][0] == 'Cải xanh', 'C1 4016 evidence changed by C2')
    require('4010' in audit.VALID, 'The repaired 4010 has no reviewed evidence')
    name, synonyms = audit.VALID['4010']
    require(name == AUDIT_VALID_NAME and synonyms == AUDIT_VALID_SYNONYMS,
            f'4010 audit evidence drift: {audit.VALID["4010"]}')
    require(all(normalize_vietnamese_text(s).startswith(('bắp cải', 'cải bắp'))
                for s in synonyms.split('|')), 'Audit evidence is not a narrow reviewed synonym list')
    require('tím' not in synonyms, 'Red cabbage must not be claimed by the white-cabbage evidence')
    return {'wrong_4010_retired': True, 'valid_4010': [name, synonyms],
            'synonyms': synonyms.split('|'), '4016_evidence_changed': False}


def guard_state(rows, aliases, catalog, review):
    """Prove the reviewed keeps held, measured rather than asserted."""
    guards = review['guards']
    live = index(rows)
    measured = {}

    # The 105 pre-existing celery rows must be exactly the untouched part of 4018.
    existing = set(guards['celery_4018_row_ids'])
    require(len(existing) == 105, f'Pre-existing 4018 cohort drift: {len(existing)}')
    moved = {p['before']['id'] for p in review['rows'] if p['target_code'] == '4018'}
    require(existing.isdisjoint(moved), 'A pre-existing 4018 row is also pinned as moving')
    require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == '4018'} == existing | moved,
            '4018 population is not the reviewed keeps plus the reviewed moves')
    for rid in existing:
        require(live[rid]['master_ingredient_name'] == catalog['4018']['name_vi'],
                f'Pre-existing celery row lost its display name: {rid}')
    measured['celery_4018_kept_rows'] = len(existing)

    # Red cabbage keeps every row that says `tím`; exactly one leaves and one enters.
    red = set(guards['red_cabbage_20035_row_ids'])
    require(len(red) == 32, f'Red-cabbage keep cohort drift: {len(red)}')
    require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == '20035'}
            == red | {RED_CABBAGE_ROW_ID}, '20035 population is not the reviewed keeps plus the reviewed move')
    require(all('tím' in normalize_vietnamese_text(live[rid]['raw_text']) for rid in red),
            'A 20035 keep row carries no purple/red evidence')
    measured['red_cabbage_kept_rows'] = len(red)

    # Sibling and deferred populations, asserted by exact id set, not by count.
    for key, code in (('red_cabbage_4011_row_ids', '4011'), ('dried_cabbage_4012_row_ids', '4012')):
        pinned = set() if code in C1_EMPTIED_SIBLING_CODES else set(guards[key])
        require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == code} == pinned,
                f'Sibling population drift: {code}')
        require(all(live[rid]['master_ingredient_name'] == catalog[code]['name_vi'] for rid in pinned),
                f'Sibling identity drift: {code}')
        measured[f'rows_on_{code}'] = len(pinned)
    for key, code in (('cai_4013', '4013'), ('cai_trang_4021', '4021')):
        pinned = set(guards['deferred_c3_row_ids'][key])
        c3_review = ROOT / 'scripts/eda/display_name_batch_c3_reviewed_state.json'
        if c3_review.exists():
            pinned -= {p['before']['id'] for p in read_json(c3_review).get('rows', [])}
        require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == code} == pinned,
                f'Deferred C3 population drift: {code}')
        measured[f'deferred_c3_rows_on_{code}'] = len(pinned)
    require(aliases['cải'] == '4013' and aliases['cải trắng'] == '4021', 'A C3 alias moved')

    # C1's identities, out of scope and untouched.
    c1 = {code: sum(1 for r in rows if (r['master_ingredient_code'] or '') == code)
          for code in guards['c1_identity_row_counts']}
    # The manifest froze these in their pre-C1 form. DISPLAY_NAME_BATCH_C1 has since
    # landed and re-homed the identities it owns; C2 still proves it moved none of
    # them itself, against the superseded values.
    require(c1 == dict(guards['c1_identity_row_counts'], **C1_SUPERSEDED_IDENTITY_ROW_COUNTS),
            f'C1 identity population drift: {c1}')
    measured['c1_identity_row_counts'] = c1

    # The six clears carry the full UNMATCHED contract.
    cleared = [p for p in review['rows'] if p['target_code'] is None]
    require(len(cleared) == 6, f'Clear cohort drift: {len(cleared)}')
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
    return measured


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
        # Only name_vi may move: code, name_en, both categories and every
        # nutrition column are asserted byte-for-byte on both sides.
        require({k: v for k, v in before.items() if k != 'name_vi'} ==
                {k: v for k, v in after.items() if k != 'name_vi'}, f'Non-name catalog change: {code}')
        require(before['name_vi'] == 'Cần tây' and after['name_vi'] == 'Cải bắp trắng',
                f'Reviewed rename drift: {code}')
        require(after['name_vi'] != FORBIDDEN_CATALOG_NAME, 'The forbidden Qwen-reactivating name was used')
        new_by_code[code].update(after)
    # The repair's justification is 4010's own name_en, not the review's say-so.
    require(new_by_code['4010']['name_en'] == 'Cabbage, common, raw', '4010 is not the common-cabbage source row')
    require(by_code['4018']['name_en'] == 'Celery, raw' and by_code['4018']['name_vi'] == 'Cần tây',
            '4018 is not the celery identity this batch hands the celery rows to')
    # Sibling identities this batch must not write. DISPLAY_NAME_BATCH_C1 landed
    # after C2 and repaired exactly one of them -- 4016's `name_vi` -- which the C2
    # manifest froze in its pre-C1 form. C2 still asserts it wrote nothing here; only
    # the value it must find has been superseded by the batch that owns that code.
    for code, before in review['catalog_identities'].items():
        expected_identity = dict(before, **C1_SUPERSEDED_CATALOG.get(code, {}))
        require(by_code[code] == new_by_code[code] == expected_identity,
                f'Sibling catalog row modified: {code}')
    require(new_by_code['4011']['name_vi'] == 'Cải bắp đỏ'
            and new_by_code['4012']['name_vi'] == 'Cải bắp trắng, khô',
            'The repaired name no longer distinguishes 4010 from its cultivar/state siblings')
    require(duplicate_names(cat) == EXPECTED_DUPLICATE_NAMES_BEFORE
            or duplicate_names(cat) == EXPECTED_DUPLICATE_NAMES_AFTER, 'Deferred duplicate drift')
    require(duplicate_names(new_cat) == EXPECTED_DUPLICATE_NAMES_AFTER,
            f'Duplicate display names after the repair: {duplicate_names(new_cat)}')

    qwen = qwen_rule_state(new_cat)
    # The same rules must already be in that state BEFORE the rename: the batch
    # must neither activate nor deactivate one.
    require(qwen_rule_state(cat) == qwen, 'The rename changed the Qwen mapper rule state')

    # The reviewed synonym, recorded from raw text rather than from the alias map.
    synonym = review['reviewed_synonym']
    require(synonym['inferred_from_alias_map'] is False, 'Reviewed synonym claims an alias-map inference')
    require(synonym['terms'] == ['cần tàu', 'cần tây'] and synonym['target_code'] == '4018',
            'Reviewed synonym drift')
    require(synonym['evidence_raw_text'] == '1 ít rau cần tây (hay cần tàu)', 'Reviewed synonym evidence drift')
    require(all(normalize_vietnamese_text(t) in normalize_vietnamese_text(synonym['evidence_raw_text'])
                for t in synonym['terms']), 'Both synonym terms must appear in the evidence line')

    aliases = read_json(root / ALIASES)
    require(len(aliases) in (ALIAS_MAP_SIZE_BEFORE, ALIAS_MAP_SIZE_LIVE), f'Alias map size drift: {len(aliases)}')
    require(review['alias_map_size'] == ALIAS_MAP_SIZE_BEFORE, 'Reviewed alias map size drift')
    actions = len(ALIAS_REPOINTS) + len(ALIAS_REMOVALS) + len(ALIAS_ADDITIONS)
    require(actions == EXPECTED_ALIAS_ACTIONS, f'Alias action count drift: {actions}')
    require(len({*ALIAS_REPOINTS, *ALIAS_REMOVALS, *ALIAS_ADDITIONS, *ALIAS_KEEPS}) ==
            actions + len(ALIAS_KEEPS), 'An alias key appears in two reviewed actions')
    require(set(ALIAS_REPOINTS) | set(ALIAS_REMOVALS) | set(ALIAS_KEEPS) == set(review['aliases_before']),
            'Reviewed alias scope drift')
    require(set(ALIAS_ADDITIONS) == set(review['aliases_absent_before']), 'Reviewed alias addition scope drift')

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
    # naming celery may still reach it.
    reviewed_on_4010 = ({k for k, v in ALIAS_REPOINTS.items() if v == '4010'}
                        | {k for k, v in ALIAS_ADDITIONS.items() if v == '4010'}
                        | {k for k, v in ALIAS_KEEPS.items() if v == '4010'}
                        | {'cải bào', 'cải bào mỏng', 'cải trắng bào',
                           'cải trắng xắt sợi', 'bắp cải tròn', 'lá bắp cải',
                           'rau bắp cải', 'bắp cải tim'})
    on_4010 = {k for k, v in new_aliases.items() if v == '4010'}
    require(on_4010 == reviewed_on_4010, f'Unreviewed alias targets the repaired 4010: {sorted(on_4010 - reviewed_on_4010)}')
    require(not any('cần' in normalize_vietnamese_text(k) for k in on_4010), 'A celery phrase still reaches 4010')
    require(not any('tím' in normalize_vietnamese_text(k) for k in on_4010), 'A red-cabbage phrase reaches 4010')
    require(all('cần' in normalize_vietnamese_text(k) for k, v in new_aliases.items()
                if v == '4018'), 'A non-celery alias reaches 4018')

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
            if provenance == 'preserved':
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
    # cleaned names or its own pinned ids, and the pins exhaust each source
    # population together with the reviewed keeps.
    celery = {rid for rid, pin in pins.items() if pin['cohort'].startswith('celery_')}
    require({pins[rid]['before']['cleaned_name'] for rid in celery} ==
            {'cần tàu', 'rau nêm cần tàu', 'rau cần tây', 'cần tây bẹ', 'cần tây bào vỏ',
             'cần tây bẹ cắt lát xéo', 'cần tây tước xơ cắt lát', 'lá cần tây non', 'mĩ 1 cây cần tây'},
            'Reviewed celery cohort is not the reviewed cleaned-name set')
    require(len(celery) == 72, f'Reviewed celery cohort drift: {len(celery)}')
    keeps = {rid for rid, pin in pins.items() if pin['cohort'] == 'white_cabbage_keep_4010'}
    require({pins[rid]['before']['cleaned_name'] for rid in keeps} ==
            {'bắp cải', 'bắp cải nhỏ', 'bắp cải trắng', 'bắp cải trái tim', 'bắp cải trộn'},
            'Reviewed keep cohort is not the reviewed cleaned-name set')
    require(all(pins[rid]['before']['match_method'] == 'QWEN_LLM_MATCH'
                and pins[rid]['before']['match_confidence'] == '0.98' for rid in keeps),
            'A reviewed keep lost its QWEN_LLM_MATCH / 0.98 provenance')
    require(all(expected[rid]['master_ingredient_code'] == '4010'
                and expected[rid]['master_ingredient_name'] == 'Cải bắp trắng'
                and expected[rid]['match_method'] == 'QWEN_LLM_MATCH'
                and expected[rid]['match_confidence'] == '0.98' for rid in keeps),
            'A reviewed keep did not simply refresh its display name')
    require(all(logical(expected[rid])[f] == logical(pins[rid]['before'])[f]
                for rid in keeps for f in NUTRIENTS), 'A reviewed keep moved a nutrient')
    # Corroborating evidence, asserted rather than narrated: all 16 QWEN-sourced
    # rows on 4010 stored the display name `Cải bắp` -- cabbage -- while the
    # catalog published `Cần tây` at the same code. The corpus itself recorded
    # that 4010 was the cabbage identity; only the catalog column disagreed.
    stale = {pins[rid]['before']['master_ingredient_name']
             for rid in pins if pins[rid]['before']['match_method'] == 'QWEN_LLM_MATCH'
             and pins[rid]['before']['master_ingredient_code'] == '4010'}
    require(stale == {'Cải bắp'}, f'Stale stored display-name evidence drift: {stale}')
    require(pins[SUBPHRASE_ROW_ID]['before']['raw_text'] == SUBPHRASE_RAW_TEXT
            and pins[SUBPHRASE_ROW_ID]['match_after'] == {
                'match_method': SUBPHRASE_MATCH['method'], 'match_confidence': str(SUBPHRASE_MATCH['confidence'])},
            'Re-measured compound row drift')
    require(pins[SUBPHRASE_ROW_ID]['before']['match_confidence'] == '0.98'
            and expected[SUBPHRASE_ROW_ID]['match_confidence'] == '0.95',
            'The compound row must not keep its old 0.98')
    for rid, (raw_text, cleaned) in RECOVERY_ROWS.items():
        require(pins[rid]['before']['raw_text'] == raw_text
                and pins[rid]['before']['cleaned_name'] == cleaned, f'Reviewed recovery row drift: {rid}')
        require(expected[rid]['match_method'] == RECOVERY_MATCH['method']
                and expected[rid]['match_confidence'] == str(RECOVERY_MATCH['confidence'])
                and expected[rid]['master_ingredient_code'] == RECOVERY_MATCH['code'],
                f'Reviewed recovery verdict drift: {rid}')
    require(pins[RED_CABBAGE_ROW_ID]['before']['raw_text'] == RED_CABBAGE_RAW_TEXT
            and 'tím' in normalize_vietnamese_text(RED_CABBAGE_RAW_TEXT),
            'The red-cabbage row carries no purple evidence')
    # Never select by code alone: the pins plus the reviewed keeps must exhaust
    # each source population. Asserted against the reviewed before population AND
    # the repaired one, because plan() is also the post-apply read-back.
    guards = review['guards']
    on_4010_before = {rid for rid, pin in pins.items() if pin['before']['master_ingredient_code'] == '4010'}
    on_4010_after = {rid for rid in pins if expected[rid]['master_ingredient_code'] == '4010'}
    require(len(on_4010_before) == 89 and len(on_4010_after) == 13, 'Reviewed 4010 population drift')
    population = {r['id'] for r in ingredients if r['master_ingredient_code'] == '4010'}
    c3_review = ROOT / 'scripts/eda/display_name_batch_c3_reviewed_state.json'
    if c3_review.exists():
        population -= {p['before']['id'] for p in read_json(c3_review).get('rows', [])}
    # DISPLAY_NAME_BATCH_C1 added exactly one reviewed row to C2's repaired identity:
    # 633ea6e1 `Bắp cải xanh 1/2 cái` is green HEAD cabbage and belonged on 4010, not
    # on red cabbage 4011 where the corrupt alias map had put it. C2's own result is
    # still asserted exactly; the live population is that result plus that one row.
    require(population in (on_4010_before, on_4010_after | {C1_ROW_ADDED_TO_4010}),
            f'Unreviewed rows on 4010: {len(population)}')

    def transform(rows):
        mutable = set(NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name',
                                    'match_method', 'match_confidence'}
        return [dict(r, **{k: v for k, v in expected[r['id']].items() if k in mutable})
                if r['id'] in expected else dict(r) for r in rows]
    new_ing, new_ing_json = transform(ingredients), transform(ingredients_json)
    parity(new_ing, new_ing_json)
    untouched = [r for r in ingredients if r['id'] not in pins]
    require([logical(r) for r in untouched]
            == [logical(r) for r in new_ing if r['id'] not in pins],
            f'A row outside the reviewed {EXPECTED_ROWS} changed')

    populations = {code: sum(1 for r in new_ing if (r['master_ingredient_code'] or '') == code)
                   for code in EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in new_ing if r['match_method'] == 'UNMATCHED')
    require(populations == EXPECTED_POPULATIONS, f'Final population drift: {populations}')
    require(populations['UNMATCHED'] == sum(1 for r in new_ing if not (r['master_ingredient_code'] or '').strip()),
            'UNMATCHED/blank-code mismatch')
    corpus_nulls = {f: sum(1 for r in new_ing if r[f] in (None, '')) for f in NUTRIENTS}
    require(corpus_nulls == EXPECTED_CORPUS_NULLS, f'Corpus null drift: {corpus_nulls}')
    guard_measured = guard_state(new_ing, new_aliases, new_by_code, review)

    ordered = sorted(pins)
    combined = nutrient_report([pins[rid]['before'] for rid in ordered], [expected[rid] for rid in ordered])
    require({f: combined[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_NUTRITION_DELTA,
            f"Nutrition delta drift: {[combined[f]['known_sum_delta'] for f in NUTRIENTS]}")
    require({f: (combined[f]['before_null_count'], combined[f]['after_null_count']) for f in NUTRIENTS}
            == EXPECTED_NULL_TRANSITIONS, 'Null transition drift')
    require({f: combined[f]['value_to_null'] for f in NUTRIENTS} == EXPECTED_VALUE_TO_NULL
            and {f: combined[f]['null_to_value'] for f in NUTRIENTS} == EXPECTED_NULL_TO_VALUE,
            'Null direction drift')
    cohort_nutrition = {}
    for cohort in COHORTS:
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        cohort_nutrition[cohort] = nutrient_report([pins[rid]['before'] for rid in ids],
                                                   [expected[rid] for rid in ids])
    require({c: {f: n[f]['known_sum_delta'] for f in NUTRIENTS} for c, n in cohort_nutrition.items()}
            == EXPECTED_COHORT_NUTRITION_DELTA, 'Reviewed cohort nutrition delta drift')
    # Every populated nutrient is the live TARGET catalog column scaled by the
    # row's own weight through the project's own scaler (AGENTS.md section 9).
    # No second multiplication or rounding convention is implemented here; the
    # independent content of this check is the SOURCE of the value.
    for rid in ordered:
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
    # The recovered rows' fat is a real scaled zero, not a coerced null.
    for rid in RECOVERY_ROWS:
        if pins[rid]['before']['match_method'] != 'UNMATCHED':
            continue
        require(expected[rid]['fat_g'] == EXPECTED_RECOVERY_FAT, f'Recovery fat drift: {rid}')
        require(float(new_by_code['4010']['fat_g']) > 0, '4010 carries no fat value to scale')

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
    # manifest, so the figures are identical on a first apply and on a replay --
    # and, unlike a git diff, they do not invert once the batch is committed.
    baseline_ing = [dict(pins[r['id']]['before']) if r['id'] in pins else dict(r) for r in ingredients]
    baseline_rollups = recompute_recipe_rollups(baseline_ing)
    changed_rollups = {rid for rid in rollups if _new_totals(baseline_rollups[rid]) != _new_totals(rollups[rid])}
    # The ten keeps move no nutrient, so their recipes' totals do not move either.
    keep_recipes = {pins[rid]['before']['recipe_id'] for rid in keeps}
    require(changed_rollups <= recipes_affected, f'Rollup radius escaped the reviewed recipes: {len(changed_rollups)}')
    require(recipes_affected - changed_rollups <= keep_recipes,
            'A reviewed recipe that should have moved its totals did not')
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
    require({rid: (t['before'][1], t['after'][1]) for rid, t in transitions.items()}
            == EXPECTED_MISSING_COUNT_TRANSITIONS, f'missing_nutrition_count radius drift: {status}')
    require(status['status_transitions'] == EXPECTED_STATUS_LABEL_TRANSITIONS, f'Status transition drift: {status}')
    # Clear-bearing recipes may only gain missing rows; recovery recipes may only lose them.
    clear_recipes = {pins[p['before']['id']]['before']['recipe_id']
                     for p in review['rows'] if p['target_code'] is None}
    recovery_recipes = {pins[rid]['before']['recipe_id'] for rid in RECOVERY_ROWS
                        if pins[rid]['before']['match_method'] == 'UNMATCHED'}
    for rid, t in transitions.items():
        if rid in clear_recipes:
            require(t['after'][1] > t['before'][1], f'A clear-bearing recipe did not gain a missing row: {rid}')
        elif rid in recovery_recipes:
            require(t['after'][1] < t['before'][1], f'A recovery recipe did not lose a missing row: {rid}')
        else:
            require(False, f'An unreviewed recipe changed its missing count: {rid}')
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
            require(groups == EXPECTED_CANONICAL_GROUPS, f'Canonical group radius drift: {groups}')
            canonical[name] = {'changed_count': len(changed), 'changed_fields': sorted(moved),
                               'mapping_rows_for_affected_recipes': len(recipes_affected & before.keys()),
                               'canonical_groups_involved': groups}
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
            require(recipes_affected - set(changed) == keep_recipes,
                    'Canonical recipes that did not change content are not exactly the reviewed keeps')
            canonical[name] = {'changed_count': len(changed),
                               'recipes_touched_without_content_change': len(keep_recipes)}
        require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')

    downstream = downstream_state(root)
    audit_evidence = audit_evidence_state()

    files = {CAT: new_cat, ALIASES: new_aliases,
             DATA/'recipe_ingredients.csv': new_ing, DATA/'recipe_ingredients.json': new_ing_json,
             DATA/'recipes.csv': new_recipes, DATA/'recipes.json': new_recipes_json}
    # The write set is the whole write set: nothing historical is ever in it.
    require(all('interim' not in p.as_posix() for p in files),
            'A historical/interim path entered the write set')
    before_files = {CAT: cat, ALIASES: aliases, DATA/'recipe_ingredients.csv': ingredients,
                    DATA/'recipe_ingredients.json': ingredients_json, DATA/'recipes.csv': recipes,
                    DATA/'recipes.json': recipes_json}
    changed_now = [rid for rid in pins if logical(live[rid]) != logical(expected[rid])]
    catalog_before = {r['code']: r for r in review['catalog_before']}
    report = dict(
        policy='DISPLAY_NAME_BATCH_C2',
        root_cause=('Catalog 4010 is the raw Viện Dinh Dưỡng row `Cabbage, common, raw`, but its '
                    'Vietnamese display name read `Cần tây` -- 4018\'s name, which 4018 also still '
                    'carries. Two codes published one display name, and the alias map organised '
                    'eighteen keys and 89 processed rows around 4010 as though it were celery: 72 '
                    'celery rows carried cabbage nutrition, bare `bắp cải` was handed to red '
                    'cabbage, and the genuine white-cabbage rows sat on a code that denied them.'),
        rows_repaired=EXPECTED_ROWS, rows_pending=len(changed_now), recipes_affected=EXPECTED_RECIPES,
        catalog_count=750,
        catalog_diff={c: {k: {'before': catalog_before[c][k], 'after': v} for k, v in patch.items()}
                      for c, patch in CATALOG_PATCHES.items()},
        catalog_name_en={c: new_by_code[c]['name_en'] for c in CATALOG_PATCHES},
        catalog_unchanged_columns=sorted(k for k in catalog_before['4010'] if k != 'name_vi'),
        forbidden_name={'name': FORBIDDEN_CATALOG_NAME,
                        'reason': ('would reactivate the disabled Qwen rule '
                                   '("bắp cải",) -> 4010 "Cải bắp" through the A1 identity check')},
        duplicate_names_before=sorted(EXPECTED_DUPLICATE_NAMES_BEFORE),
        duplicate_names_after=sorted(EXPECTED_DUPLICATE_NAMES_AFTER),
        qwen_mapper=qwen,
        reviewed_synonym=synonym,
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
        populations=populations, corpus_nulls=corpus_nulls,
        combined_nutrition=combined,
        recipe_status=status, canonical=canonical,
        canonical_id_drift=0, representative_drift=0,
        review_estimate_canonical=REVIEW_ESTIMATE_CANONICAL,
        downstream_hard_codes=downstream, audit_evidence=audit_evidence,
        interim=interim_digest(root), write_set=sorted(p.as_posix() for p in files),
        stale_stored_display_name={
            'stored_on_4010_before': sorted(stale), 'catalog_published_before': 'Cần tây',
            'rows': sum(1 for rid in pins if pins[rid]['before']['match_method'] == 'QWEN_LLM_MATCH'
                        and pins[rid]['before']['master_ingredient_code'] == '4010'),
            'note': ('The QWEN-sourced rows on 4010 stored `Cải bắp` while the catalog column '
                     'published `Cần tây` at the same code: the corpus already recorded 4010 as '
                     'the cabbage identity, and only the catalog display name disagreed.')},
        non_reproducible_clears=NON_REPRODUCIBLE_CLEARS,
        known_route_divergence=KNOWN_ROUTE_DIVERGENCE,
        guards=guard_measured, deferrals=DEFERRALS,
        affected_recipe_ids=sorted(recipes_affected),
        row_outcomes={rid: dict(cohort=pins[rid]['cohort'], before=pins[rid]['before'], after=expected[rid])
                      for rid in ordered},
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
    require(all(r['single_method'] == r['batch_method'] for r in result.values()),
            'A live reviewed phrase resolves through different stages on the two routes')
    # The re-measured verdicts are measured here, not assumed by the manifest.
    for query, pinned in (('mĩ 1 cây cần tây', SUBPHRASE_MATCH),
                          ('bắp cải', RECOVERY_MATCH), ('bắp cải trái tim', RECOVERY_MATCH)):
        single = matcher.match(query, raw_context=query)
        batched = matcher.match_batch([query], raw_contexts=[query])[0]
        for value in (single, batched):
            require((value['matched_item'] or {}).get('code') == pinned['code']
                    and value['method'] == pinned['method'] and value['confidence'] == pinned['confidence'],
                    f'Re-measured verdict not reproduced: {query}: {value["method"]} {value["confidence"]}')
        result[query] = {'code': pinned['code'], 'single_method': single['method'],
                         'batch_method': batched['method'], 'single_confidence': single['confidence'],
                         'batch_confidence': batched['confidence']}
    # The removed fragment has no live row and is allowed to diverge; nothing a
    # live row uses may.
    divergence = {}
    for query, pinned in KNOWN_ROUTE_DIVERGENCE.items():
        single = matcher.match(query, raw_context=query)
        batched = matcher.match_batch([query], raw_contexts=[query])[0]
        observed = {'single': (single['matched_item'] or {}).get('code'),
                    'batch': (batched['matched_item'] or {}).get('code')}
        require(observed == {'single': pinned['single_after'], 'batch': pinned['batch_after']},
                f'Route divergence drift outside the reviewed set: {query}: {observed}')
        divergence[query] = dict(pinned, observed=observed)
    return result, divergence


def write_report(report, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'applied_fix.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    diff = report['catalog_diff']['4010']['name_vi']
    lines = ['# Display-name corruption repair, Batch C2 — white cabbage 4010', '',
             f"Policy: DISPLAY_NAME_BATCH_C2. {report['rows_repaired']} ingredient rows "
             f"/ {report['recipes_affected']} source recipes.", '',
             '## Root cause', '', report['root_cause'], '',
             '## Catalog', '', '| Code | Field | Before | After | name_en (unchanged) |', '|---|---|---|---|---|',
             f"| 4010 | name_vi | {diff['before']} | {diff['after']} | {report['catalog_name_en']['4010']} |", '',
             f"Every other column is asserted byte-for-byte unchanged: "
             f"{', '.join('`' + c + '`' for c in report['catalog_unchanged_columns'])}.", '',
             f"`{report['forbidden_name']['name']}` was **not** used: it {report['forbidden_name']['reason']}. "
             f"`{diff['after']}` states the white/common cultivar the row's own `name_en` asserts and stays "
             'distinct from 4011 `Cải bắp đỏ` and 4012 `Cải bắp trắng, khô`. Qwen mapper rules after the '
             f"repair: {report['qwen_mapper']['active']} active / {report['qwen_mapper']['disabled']} disabled, "
             'unchanged, with that rule still disabled and `map_clean_to_master("bắp cải")` still unresolved.', '',
             'Colliding display names before: ' + ', '.join(f'`{n}`' for n in report['duplicate_names_before']) +
             '. After: ' + ', '.join(f'`{n}`' for n in report['duplicate_names_after']) +
             ' — `cần tây` leaves the set, which is what this batch is for.', '',
             '## Reviewed synonym', '',
             f"`{report['reviewed_synonym']['terms'][0]}` == `{report['reviewed_synonym']['terms'][1]}` → "
             f"{report['reviewed_synonym']['target_code']}.", '',
             report['reviewed_synonym']['basis'], '',
             f"Evidence row `{report['reviewed_synonym']['evidence_row_id']}`: "
             f"`{report['reviewed_synonym']['evidence_raw_text']}`.", '',
             '## Exact alias changes', '',
             f"{report['alias_actions']} actions. Map size {report['alias_map_size_before']} − "
             f"{len(report['alias_diff']['removed'])} removed + {len(report['alias_diff']['added'])} added = "
             f"{report['alias_map_size']}.", '',
             '| Action | Alias | Before | After |', '|---|---|---|---|']
    for action, entries in report['alias_diff'].items():
        for alias, change in entries.items():
            lines.append(f"| {action} | {alias} | {change['before'] or '—'} | {change['after'] or '—'} |")
    lines += ['', 'Reviewed aliases that were already correct and stay put: ' +
              ', '.join(f'`{k}` → {v}' for k, v in report['alias_keeps'].items()) +
              '. `cải` → 4013 and `cải trắng` → 4021 belong to C3 and are asserted unchanged.', '',
              '## Processed rows and nutrition', '',
              'Nutrition sums include known values only; missing values remain null. Every populated value is '
              "the live target catalog column scaled by the row's own weight through "
              '`nlp.nutrition.scale_nutrition` — no second rounding convention is implemented. Exact '
              f"before/after records for all {report['rows_repaired']} ingredient rows and "
              f"{report['recipes_affected']} recipes are in [applied_fix.json](applied_fix.json).", '',
              '| Cohort | Source | Target | Provenance | Rows | Recipes | kcal | Protein | Fat | Carbs |',
              '|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for name, c in report['cohorts'].items():
        lines.append(f"| {name} | {c['source_code']} | {c['target_code']} | {c['provenance']} | "
                     f"{c['row_count']} | {c['recipe_count']} | "
                     + ' | '.join(c['nutrition'][f]['known_sum_delta'] for f in NUTRIENTS) + ' |')
    lines += ['', '| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |',
              '|---|---:|---:|---:|---:|']
    for field, n in report['combined_nutrition'].items():
        lines.append(f"| {field} | {n['before_known_sum']} | {n['after_known_sum']} | {n['known_sum_delta']} | "
                     f"{n['before_null_count']} → {n['after_null_count']} |")
    lines += ['', 'The only null movement is the six clears (value → null on all four nutrients) and the two '
              'UNMATCHED recoveries (null → value on all four). The recoveries store `fat_g = 0.0`: 4010 '
              'carries 0.09 g/100 g and 0.09 × 0.30 / 0.09 × 0.50 both round to 0.0 at the project\'s one '
              'decimal. That is a real scaled numeric zero, not a coerced null — AGENTS.md section 4.', '',
              'Corpus-wide null counts after: ' + json.dumps(report['corpus_nulls']) + '.', '',
              '## The six curated clears', '',
              'An either-or line, two compounds, two dish titles and a multi-identity line. None of them has a '
              'single defensible catalog identity, and picking one component would be exactly the forced '
              'coverage AGENTS.md section 5 rejects. Each is pinned by exact id, exact raw text and a complete '
              'before record, and each carries the full UNMATCHED contract afterwards: blank code, blank name, '
              '`UNMATCHED`, blank confidence (never `0.0`) and four null nutrients, with raw text, cleaned '
              'name, quantity/unit, preparation note and estimated weight preserved.', '',
              '**These six are intentionally NOT matcher-reproducible.** ' +
              '; '.join(f"`{q}` is stored {v['stored']} while the matcher would reach {v['matcher_would_reach']} "
                        f"({v['reason']})" for q, v in report['non_reproducible_clears'].items()) +
              '. No broad guard is added to reproduce them: a guard wide enough to catch these lines would '
              'reach rows nobody reviewed, and is a separate reviewed decision.', '',
              '## Final populations', '', '| Code | Rows |', '|---|---:|']
    for code, count in report['populations'].items():
        lines.append(f'| {code} | {count} |')
    lines += ['', 'Recipe rollups: ' + json.dumps(report['recipe_status'], ensure_ascii=False) +
              ' — five clear-bearing recipes gain a missing row (one holds two of the six clears) and the two '
              'recovery recipes lose one. No recipe crosses a COMPLETE/PARTIAL/INCOMPLETE threshold, so there '
              'are zero `nutrition_status` label transitions, and none is forced.', '',
              '## Downstream hard-coded cabbage codes', '',
              '| File | Occurrences | on 4012 | on 4010 |', '|---|---:|---:|---:|']
    for path, values in report['downstream_hard_codes'].items():
        if isinstance(values, dict) and 'occurrences' in values:
            lines.append(f"| {path} | {values['occurrences']} | {values['on_4012']} | {values['on_4010']} |")
    lines += ['', 'Five live fresh-cabbage pantry entries pointed at 4012 `Cải bắp trắng, khô` — dried cabbage '
              'at 301 kcal/100 g — for a vegetable a household buys by the 200–600 g head. They now point at '
              'the repaired fresh 4010. `("dưa chuột", "4016", …)` is C1\'s and is untouched. `src/` is '
              're-scanned on every run, and any other hard-coded fresh-cabbage code fails the batch closed.', '',
              '## Audit evidence hygiene', '',
              'The stale `4010 → `Cần tây`` WRONG signature in `scripts/eda/audit_qwen_matching.py` is retired '
              'and replaced by the narrow VALID pattern for the repaired identity: '
              f"`{report['audit_evidence']['valid_4010'][0]}` / " +
              ', '.join(f'`{s}`' for s in report['audit_evidence']['synonyms']) +
              '. Evidence hygiene only — no production matcher behaviour changes, and 4016\'s evidence is '
              "C1's and is not touched. Measured consequence: exactly one surviving row moves B → C.", '',
              '## Matcher replay', '', '| Query | Code | Single route | Batch route |', '|---|---|---|---|']
    for query, result in report.get('matcher_replay', {}).items():
        lines.append(f"| {query} | {result['code']} | {result['single_method']} {result['single_confidence']} "
                     f"| {result['batch_method']} {result['batch_confidence']} |")
    if report.get('route_divergence'):
        lines += ['', 'Known divergence, documented and not fixed: ' +
                  '; '.join(f"`{q}` was {v['before']}, now reaches {v['single_after']} on the single route and "
                            f"{v['batch_after']} on the batch route, with {v['live_rows']} live rows"
                            for q, v in report['route_divergence'].items()) +
                  '. It moves no stored row, and no phrase a live row uses diverges.']
    lines += ['', '## Deferred, recorded and unchanged', '']
    for key, why in report['deferrals'].items():
        lines.append(f'- **{key}.** {why}')
    lines += ['', '## Canonical propagation', '', '| Artifact | Changed logical records |', '|---|---:|']
    for name, values in report['canonical'].items():
        lines.append(f"| {name} | {values['changed_count']} |")
    estimate = report['review_estimate_canonical']
    lines += ['', f"The {report['recipes_affected']} affected recipes span "
              f"{report['canonical']['recipe_canonical_mapping.csv']['canonical_groups_involved']} canonical "
              'groups, and every reviewed row appears in `canonical_recipe_ingredients.csv`. The '
              f"pre-implementation review quoted {estimate['estimate']['canonical_recipes_changed']} canonical "
              f"recipes changed; measured, "
              f"{estimate['measured']['canonical_recipe_groups_touched']} canonical recipes are touched and "
              f"{estimate['measured']['canonical_recipes_csv_rows_changed']} rows change content. "
              + estimate['cause'] + ' Canonical ID drift = 0; representative drift = 0.', '',
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
    if not apply:
        return report
    changed = [p for p in files if (files[p] != before_files[p] if p.suffix == '.json'
                                    else [logical(r) for r in files[p]] != [logical(r) for r in before_files[p]])]
    prior = out/'applied_fix.json'
    cache = (root/CAT).with_name('catalog_embeddings_bkai.pt')
    tracked = subprocess.run(['git', 'ls-files', '--', str(cache.relative_to(root))], cwd=root,
                             capture_output=True, text=True, check=True).stdout.strip()
    require(not tracked, 'Embedding cache unexpectedly tracked; review version-control policy')
    if not changed and report['downstream_hard_codes']['pending'] == 0 and prior.exists():
        previous = read_json(prior)
        if previous.get('validation', {}).get('complete') and cache.exists():
            accepted = accepted_embedding_digests(previous)
            require(hashlib.sha256(cache.read_bytes()).hexdigest() in accepted['sha256'],
                    'Embedding cache drift')
            require(embedding_input_digest(files[CAT]) in accepted['input_sha256'],
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
    # Catalog first, then aliases, then the downstream hard-codes, then processed
    # rows and rollups. Canonical is regenerated only after the rows verify.
    for path in (CAT, ALIASES, DATA/'recipe_ingredients.csv', DATA/'recipe_ingredients.json',
                 DATA/'recipes.csv', DATA/'recipes.json'):
        if path not in changed:
            continue
        if path.suffix == '.csv':
            write_csv(root/path, files[path], list(files[path][0]))
        else:
            write_json(root/path, files[path])
    report['downstream_hard_codes'] = downstream_state(root, repair=True)
    require(report['downstream_hard_codes']['pending'] == 0, 'Downstream hard-code repair did not complete')
    report['status'] = 'processed_applied_validation_pending'
    write_report(report, out)
    import torch
    matcher = VietnameseIngredientMatcher(root/CAT)
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
    report['matcher_replay'], report['route_divergence'] = replay(matcher)
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
