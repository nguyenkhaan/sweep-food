"""BAMBOO_SHOOT_ALIAS_FIX: reviewed 55-row / 50-recipe repair; dry-run by default.

Three alias keys in `ingredient_alias_map.json` have pointed at the wrong catalog
identity since the original dataset commit, and every one of them resolves at
PRESET_ALIAS_MATCH 0.98 -- the earliest scored stage, so nothing downstream ever
had a chance to correct them:

    măng khô       -> 4048 `Lá mơ lông`   (skunk vine: not bamboo at all)
    măng tươi      -> 4051 `Măng tre, khô` (dried bamboo, for an explicit `tươi` row)
    măng tươi bào  -> 4051 `Măng tre, khô` (same, shaved)

All three targets are wrong against the rows' own qualifiers. The corrections are
the identities the source catalog already asserts: 4051 is `Bamboo shoot, dried`
and 4053 is `Măng tre, tươi` / `Bamboo shoots, raw` in the raw Viện Dinh Dưỡng
table. Both are source rows, not project extensions, and neither is modified --
this batch changes no catalog column and rebuilds no embeddings.

The sibling aliases prove the shape rather than invent it: `măng tre khô` already
points at 4051 and `măng tre` / `măng tre tươi` already point at 4053. After the
repair, `măng khô` agrees with `măng tre khô` and `măng tươi` agrees with
`măng tre tươi`, where today they contradict each other.

Bare `măng` is NOT repaired. It stays on 4051 and its 14 rows are asserted
byte-for-byte unchanged. The corpus marks every state explicitly when it means it
(`khô`, `tươi`, `chua`), so the bare key has no single defensible identity, and
removing it is measurably unsafe rather than merely unreviewed: `măng` is long
enough for SUBPHRASE_CATALOG_MATCH, so deletion does not reach UNMATCHED -- it
falls through to 4051 on the single route and 4050 on the batch route, inventing
a `match()` / `match_batch()` divergence that does not exist today. Clearing those
rows would need a terminal guard, which is a separate reviewed decision.

The adjacent JSON is a frozen review manifest, never discovered or refreshed at
runtime: it carries the complete before record of all 55 rows, the reviewed
before state of all 15 relevant aliases, the four catalog identities asserted
unchanged, and the guard populations this batch must not disturb -- the 14 bare
`măng` rows, the single genuine `Lá mơ lông` row, Batch B's 62 sour-bamboo rows,
the 2 fresh-bamboo EXACT_CATALOG_MATCH rows, the 36 UNMATCHED cultivar/typo rows
and the 51 `măng tây` / 6 `măng cụt` rows. Rows are never selected by current
code alone: each pinned row must equal its reviewed before state or its computed
after state, and the pins must exhaust each source population.

All 55 rows preserve their existing PRESET_ALIAS_MATCH / 0.98 provenance, their
raw text, cleaned name, parsed quantity/unit and estimated weight. Only the
master identity and the four nutrient columns move, recomputed from the live
target catalog row through the project's own scaler.

Aliases, processed rows and rollups are planned before any writes, and the
resulting populations, nutrition delta, null transitions and canonical radius are
all checked against the reviewed figures first. --apply writes in that order,
asserts the untracked embedding cache is byte-identical (the catalog did not
move, so it cannot), replays the real matcher over both routes, exports canonical
CSV/JSON and runs canonical --check. A completed rerun writes nothing.
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

from nlp.entity_matcher import VietnameseIngredientMatcher
from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition
from scripts.eda.apply_qwen_safe_fix import (
    read_csv, read_json, write_json, recompute_recipe_rollups, _apply_rollups, _new_totals,
)
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status
from scripts.canonicalize_recipes import compose_reviewed_aliases

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).with_name('bamboo_shoot_alias_reviewed_state.json')
OUT = ROOT / 'reports/eda/bamboo_shoot_alias_fix'
CAT = Path('data/processed/viendinhduong/master_ingredients_nutrition.csv')
ALIASES = CAT.with_name('ingredient_alias_map.json')
DATA = Path('data/processed/recipes')
NUTRIENTS = ('calories', 'protein_g', 'fat_g', 'carbs_g')

# The three reviewed repoints. Nothing is added and nothing is removed.
ALIAS_PATCHES = {'măng khô': '4051', 'măng tươi': '4053', 'măng tươi bào': '4053'}
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
# Reviewed aliases that are already correct and must stay exactly where they are.
# `măng` is listed here deliberately: leaving it on 4051 is the reviewed outcome
# of this batch, not an oversight. See the module docstring.
ALIAS_KEEPS = {
    'măng': '4051', 'măng tre khô': '4051', 'măng tre': '4053', 'măng tre tươi': '4053',
    'măng chua': '4050', 'măng muối': '4050', 'măng le chua': '4050', 'măng chua măng tre': '4050',
    'lá mơ lông': '4048', 'lá mơ lông tươi': '4048', 'măng tây': '20033', 'măng cụt': '5061',
}
# cohort -> (source code, target code, reviewed row count, reviewed cleaned_name)
COHORTS = {
    'mang_kho_4048_to_4051': ('4048', '4051', 20, 'măng khô'),
    'mang_tuoi_4051_to_4053': ('4051', '4053', 32, 'măng tươi'),
    'mang_tuoi_bao_4051_to_4053': ('4051', '4053', 3, 'măng tươi bào'),
}
# The catalog is not touched. These are asserted, not written: 4051 and 4053 are
# the raw Viện Dinh Dưỡng rows whose own name_en states the preparation state the
# repair depends on, and 4048/4050 must stay exactly as Batch A/B left them.
EXPECTED_CATALOG_IDENTITY = {
    '4048': ('Lá mơ lông', 'Skunk vine, raw'),
    '4050': ('Măng chua, măng tre', 'Bamboo shoot, fermented, raw'),
    '4051': ('Măng tre, khô', 'Bamboo shoot, dried'),
    '4053': ('Măng tre', 'Bamboo shoots, raw'),
}
# C3 repaired parser-damaged white-cabbage rows; own reviewed row sets remain unchanged.
EXPECTED_POPULATIONS = {
    '4048': 1, '4051': 34, '4053': 37,
    # Sibling identities this batch must not disturb. 4050/4055/4121 are Batch B's
    # result; 20033/5061 are the asparagus and mangosteen homonyms.
    '4050': 62, '4055': 57, '4121': 0, '20033': 51, '5061': 6,
    # UNMATCHED was superseded again by DISPLAY_NAME_BATCH_C1: 35 clears minus 5
    # mustard-green recoveries is a net +30. The bamboo rows are unaffected.
    'UNMATCHED': 8495,
}
EXPECTED_NUTRITION_DELTA = {
    'calories': '-21138.5', 'protein_g': '-955.5', 'fat_g': '-132.3', 'carbs_g': '-4023.2',
}
EXPECTED_COHORT_NUTRITION_DELTA = {
    'mang_kho_4048_to_4051': {
        'calories': '12017.5', 'protein_g': '432.3', 'fat_g': '99.8', 'carbs_g': '2351.2'},
    'mang_tuoi_4051_to_4053': {
        'calories': '-31401.0', 'protein_g': '-1314.2', 'fat_g': '-219.8', 'carbs_g': '-6037.0'},
    'mang_tuoi_bao_4051_to_4053': {
        'calories': '-1755.0', 'protein_g': '-73.6', 'fat_g': '-12.3', 'carbs_g': '-337.4'},
}
# The whole null movement is the 20 `măng khô` rows gaining a fat value. 4048
# carries no fat figure and 4051 does, so this is a null -> real transition taken
# from the live target catalog, never a zero-fill. Nothing moves the other way.
EXPECTED_NULL_TRANSITIONS = {
    'calories': (0, 0), 'protein_g': (0, 0), 'fat_g': (20, 0), 'carbs_g': (0, 0),
}
EXPECTED_FAT_NULL_TO_VALUE = 20
# UNMATCHED and the corpus null counts were superseded by DISPLAY_NAME_BATCH_C2,
# which cleared 6 multi-identity cabbage/celery rows to UNMATCHED and recovered 2
# stored-UNMATCHED white-cabbage rows: 8465 - 2 + 6 = 8469, and the same net +4 on
# each nutrient's null count. The bamboo batch's own 55 rows are unaffected.
# Superseded once more by DISPLAY_NAME_BATCH_C1: net +30 on every nutrient from its
# 35 clears and 5 recoveries, plus a further +9 on fat_g alone, because the eight
# fresh-napa rows (4109) and the one salted-napa row (4115) move onto identities that
# publish no fat_g value. The bamboo batch's own 55 rows are unaffected.
EXPECTED_CORPUS_NULLS = {
    'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454,
}
EXPECTED_ROWS = 55
EXPECTED_RECIPES = 50
# canonical_recipes.csv holds one row per group representative. 4 of the 50
# affected recipes are non-winning duplicates, so 46 representative rows change
# content while 49 distinct canonical groups are touched; the same 4 recipes are
# why 51 of the 55 reviewed rows appear in canonical_recipe_ingredients.csv.
EXPECTED_CANONICAL = {
    'canonical_recipe_ingredients.csv': 51,
    'canonical_recipes.csv': 46,
    'recipe_canonical_mapping.csv': 20,
}
EXPECTED_CANONICAL_GROUPS = 49
EXPECTED_CANONICAL_INGREDIENT_ROWS_ABSENT = 4
# Only the 20 `măng khô` recipes move a mapping quality counter, because clearing
# a null fat clears a nutrition anomaly. The 35 fresh-bamboo rows swap one fully
# populated identity for another and move no counter at all.
EXPECTED_MAPPING_CHANGED_FIELDS = {
    'candidate_score', 'selection_score', 'nutrition_anomaly_count',
    'negative_nutrition_anomaly_rate', 'negative_recipe_nutrition_anomalies',
}
# missing_nutrition_count keys on null CALORIES only, and no reviewed row has a
# null calories value before or after, so no recipe changes label or count.
EXPECTED_MISSING_COUNT_RECIPES = set()
EXPECTED_STATUS_LABEL_TRANSITIONS = {}

# Bare `măng` stays on 4051 by review. Recorded, measured, and deliberately unfixed.
DEFERRAL_KEY = 'bare_mang_ambiguous_state_resolution'
DEFERRAL = {
    'status': 'DEFERRED_NEEDS_DOMAIN_REVIEW',
    'alias': 'măng -> 4051 (unchanged)',
    'rows': 14,
    'corpus_evidence': ('8 of the 14 raw lines read `măng luộc` (boiled) and 6 are bare. None '
                        'carries khô, tươi or chua, while every dried row in the corpus says khô, '
                        'every fresh row says tươi and every fermented row says chua. The corpus '
                        'therefore offers no positive evidence for a single identity.'),
    'why_not_4053': ('Fresh is only the residual after eliminating dried and fermented. '
                     'AGENTS.md section 5 requires broad aliases to clear a higher evidence bar '
                     'than qualified ones, and elimination is not that evidence.'),
    'why_not_removed': ('Removal does not reach UNMATCHED. `măng` is 4 characters, so '
                        'SUBPHRASE_CATALOG_MATCH picks it up at 0.95 against the catalog heads '
                        '`măng tre` (4051) and `măng chua` (4050): measured, the single route '
                        'lands on 4051 and the batch route on 4050. Production uses match_batch, '
                        'so deletion would silently move 14 rows onto fermented bamboo AND '
                        'manufacture a match()/match_batch() divergence that does not exist today.'),
    'why_not_cleared': ('Clearing the rows without removing the alias is not durable: a reprocess '
                        're-applies PRESET_ALIAS_MATCH. A durable clear needs a terminal guard in '
                        'the chicken-fat / coriander-seed style, which is a separate decision.'),
    'nutrition_left_wrong': ('The 14 rows keep dried-bamboo nutrition, which is known to be wrong '
                             'in magnitude (`Măng luộc 500 gr` = 1505 kcal). This is recorded as a '
                             'deferred defect, not as an accepted value.'),
    'parser_note': ("clean_culinary_query strips `tươi` but preserves `khô`, so bare `măng` is "
                    'structurally enriched with fresh phrases and cannot receive dried ones. '
                    'Reported as evidence for the future decision; parser behaviour is not changed.'),
}

# Reviewed identities, the three repoints, and every sibling that must not move.
PROBES = {
    # Corrected by this batch.
    'măng khô': '4051', 'măng tươi': '4053', 'măng tươi bào': '4053',
    # Reviewed keeps: the siblings that already agreed with the catalog.
    'măng tre khô': '4051', 'măng tre': '4053', 'măng tre tươi': '4053',
    # Deferred, deliberately unchanged.
    'măng': '4051',
    # Batch B must remain exactly as it was left.
    'măng chua': '4050', 'măng chua ớt': '4050', 'măng muối': '4050', 'măng le chua': '4050',
    'măng chua măng tre': '4050',
    # The skunk-vine identity keeps its own aliases.
    'lá mơ lông': '4048', 'lá mơ lông tươi': '4048',
    # Homonyms that must never be drawn into the bamboo band.
    'măng tây': '20033', 'măng cụt': '5061',
}
# Cultivar and preparation phrases with no catalog identity. They are UNMATCHED in
# the stored corpus and this batch must not change which code they reach; the
# codes below are the matcher's pre-existing neural verdicts, pinned so a silent
# shift into 4051/4053 cannot pass unnoticed.
CULTIVAR_PROBES = {
    'măng le': '5023', 'măng sặt': '5010', 'măng trúc': '4053', 'măng nứa': '5061',
    'măng vầu': '4053', 'măng non': '5061', 'măng vàng': '2026', 'măng luộc': '2012002',
}

EXCLUSIONS = [
    'bare `măng` -> 4051 and its 14 rows', '36 UNMATCHED cultivar/typo/fragment bamboo rows',
    'cultivar-level identities (măng le, nứa, vầu, sặt, trúc, vàng) have no catalog target',
    '4121 vs 20077 duplicate resolution', '4010 / 4016', '4052 / 20033', '4058 / 20037',
    '4044 / 20062', 'other catalog-gap codes', 'broad parser architecture',
    'clean_culinary_query stripping `tươi` but preserving `khô`',
    'match()/match_batch() structural divergence', 'stale code-space contamination generally',
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


def expected_row(reviewed, catalog):
    """Row-level identity repair against the live (unmodified) catalog.

    Provenance is preserved, not recomputed: this batch corrects which catalog
    identity a reviewed link points at, so match_method and match_confidence are
    carried through from the before record and re-asserted by the caller. Weight
    is popped so the source value survives byte-for-byte; only the master identity
    and the four nutrient columns move.
    """
    row = deepcopy(reviewed['before'])
    code = reviewed['target_code']
    patch = stage_qwen_update(row, catalog, float(row['estimated_weight_g']), {
        'master_ingredient_code': code, 'master_ingredient_name': catalog[code]['name_vi'],
        'match_method': row['match_method'], 'match_confidence': row['match_confidence']})
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


def guard_state(rows, aliases, review):
    """Prove the reviewed keeps and deferrals held, measured rather than asserted."""
    guards = review['guards']
    live = index(rows)
    measured = {}

    # Deferred bare `măng`: byte-for-byte identical, still on 4051, still 0.98.
    bare = guards['bare_mang_rows']
    require(len(bare) == DEFERRAL['rows'], f'Bare măng cohort drift: {len(bare)}')
    for before in bare:
        rid = before['id']
        require(rid in live and logical(live[rid]) == logical(before), f'Bare măng row changed: {rid}')
        require(live[rid]['master_ingredient_code'] == '4051'
                and live[rid]['match_method'] == 'PRESET_ALIAS_MATCH'
                and live[rid]['match_confidence'] == '0.98', f'Bare măng provenance drift: {rid}')
    require(aliases['măng'] == '4051', 'Bare măng alias moved')
    measured['bare_mang'] = {'rows': len(bare), 'alias': aliases['măng'],
                             'row_ids': sorted(r['id'] for r in bare)}

    # The one genuine skunk-vine row: 4048 must keep exactly this row and no other.
    mo = guards['la_mo_long_rows']
    require(len(mo) == 1, f'Lá mơ lông cohort drift: {len(mo)}')
    for before in mo:
        require(logical(live[before['id']]) == logical(before), f'Lá mơ lông row changed: {before["id"]}')
    on_4048 = {r['id'] for r in rows if (r['master_ingredient_code'] or '') == '4048'}
    require(on_4048 == {r['id'] for r in mo}, f'4048 population is not the reviewed row alone: {len(on_4048)}')
    measured['la_mo_long'] = {'rows': len(mo), 'row_ids': sorted(on_4048),
                              'aliases': sorted(k for k, v in aliases.items() if v == '4048')}

    # Batch B sour bamboo and the two fresh EXACT_CATALOG_MATCH rows.
    sour = set(guards['sour_bamboo_row_ids'])
    require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == '4050'} == sour,
            'Batch B sour-bamboo population drift')
    require(all(live[rid]['master_ingredient_name'] == 'Măng chua, măng tre' for rid in sour),
            'Batch B sour-bamboo identity drift')
    exact = set(guards['fresh_bamboo_exact_row_ids'])
    require(all(live[rid]['master_ingredient_code'] == '4053'
                and live[rid]['match_method'] == 'EXACT_CATALOG_MATCH'
                and live[rid]['match_confidence'] == '1.0' for rid in exact),
            'Fresh-bamboo EXACT_CATALOG_MATCH rows drifted')
    measured['sour_bamboo_rows'] = len(sour)
    measured['fresh_bamboo_exact_rows'] = len(exact)

    # The 36 cultivar/typo/fragment rows stay stored UNMATCHED, on the full contract.
    unmatched = guards['unmatched_bamboo_row_ids']
    require(len(unmatched) == 36, f'Reviewed UNMATCHED bamboo cohort drift: {len(unmatched)}')
    for rid in unmatched:
        row = live[rid]
        require(row['match_method'] == 'UNMATCHED'
                and not (row['master_ingredient_code'] or '').strip()
                and not (row['master_ingredient_name'] or '').strip()
                and row['match_confidence'] in (None, '')
                and all(row[f] in (None, '') for f in NUTRIENTS),
                f'Reviewed UNMATCHED bamboo row violates the contract: {rid}')
    measured['unmatched_bamboo_rows'] = len(unmatched)

    # Asparagus and mangosteen homonyms.
    for code, key in (('20033', 'mang_tay_row_ids'), ('5061', 'mang_cut_row_ids')):
        pinned = set(guards[key])
        require({r['id'] for r in rows if (r['master_ingredient_code'] or '') == code} == pinned,
                f'Homonym population drift: {code}')
        measured[f'rows_on_{code}'] = len(pinned)
    return measured


def plan(root=ROOT):
    review = read_json(REVIEW)
    cat = read_csv(root / CAT)
    require(len(cat) == review['catalog_count'] == 750, 'Catalog row count drift')
    by_code = index(cat, 'code')
    # The catalog is not written by this batch: assert it byte-for-byte instead.
    require({c: dict(by_code[c]) for c in review['catalog_identities']} == review['catalog_identities'],
            'Catalog identity drift: this batch must not run against a moved catalog')
    for code, (name_vi, name_en) in EXPECTED_CATALOG_IDENTITY.items():
        require(by_code[code]['name_vi'] == name_vi and by_code[code]['name_en'] == name_en,
                f'Reviewed catalog identity drift: {code}')
    # The repair's whole justification is that the targets are preparation-state
    # distinct in the source table; assert that rather than trust the review.
    require(by_code['4051']['name_en'].endswith('dried') and by_code['4053']['name_en'].endswith('raw'),
            'Target preparation states no longer distinguishable from name_en')
    require(float(by_code['4051']['water_g']) < float(by_code['4053']['water_g']),
            'Dried target is not drier than the fresh target')

    aliases = read_json(root / ALIASES)
    require(len(aliases) == ALIAS_MAP_SIZE and review['alias_map_size'] == REVIEWED_ALIAS_MAP_SIZE,
            'Alias map size drift')
    new_aliases = dict(aliases)
    for key, before in review['aliases_before'].items():
        after = ALIAS_PATCHES.get(key, before)
        require(aliases.get(key) in (before, after), f'Alias drift: {key}')
        new_aliases[key] = after
    require(set(ALIAS_PATCHES) <= set(review['aliases_before']), 'Repointed alias missing from the manifest')
    require(set(ALIAS_KEEPS) <= set(review['aliases_before']), 'Reviewed keep missing from the manifest')
    require(set(ALIAS_PATCHES).isdisjoint(ALIAS_KEEPS), 'An alias is both repointed and kept')
    for key, code in ALIAS_KEEPS.items():
        require(review['aliases_before'][key] == code and aliases[key] == code and new_aliases[key] == code,
                f'Reviewed alias keep drift: {key}')
    require({k for k in aliases.keys() | new_aliases.keys() if aliases.get(k) != new_aliases.get(k)}
            <= ALIAS_PATCHES.keys(), 'Unrelated alias change')
    require(len(new_aliases) == len(aliases) == ALIAS_MAP_SIZE, 'Alias map size changed')
    left_behind = {k: v for k, v in new_aliases.items() if k in ALIAS_PATCHES and v != ALIAS_PATCHES[k]}
    require(left_behind == {}, f'Repointed alias not applied: {left_behind}')
    # After the repair no alias may still hand a bamboo phrase to the skunk vine,
    # and the qualified pairs must agree with their `măng tre` siblings.
    require({k for k, v in new_aliases.items() if v == '4048'} == {'lá mơ lông', 'lá mơ lông tươi'},
            'An unreviewed alias still targets 4048')
    require(new_aliases['măng khô'] == new_aliases['măng tre khô'] == '4051',
            'Dried pair disagrees after the repair')
    require(new_aliases['măng tươi'] == new_aliases['măng tre tươi'] == '4053',
            'Fresh pair disagrees after the repair')

    ingredients = read_csv(root / DATA / 'recipe_ingredients.csv')
    ingredients_json = read_json(root / DATA / 'recipe_ingredients.json')
    parity(ingredients, ingredients_json)
    live = index(ingredients)
    pins = {x['before']['id']: x for x in review['rows']}
    require(len(pins) == len(review['rows']) == EXPECTED_ROWS, 'Review manifest row count drift')
    expected = {rid: expected_row(pin, by_code) for rid, pin in pins.items()}
    for rid, pin in pins.items():
        require(rid in live and logical(live[rid]) in (logical(pin['before']), logical(expected[rid])),
                f'Row drift: {rid}')

    for cohort, (source, target, count, cleaned) in COHORTS.items():
        pinned = {rid for rid, pin in pins.items() if pin['cohort'] == cohort}
        require(len(pinned) == count, f'Reviewed cohort count drift: {cohort}={len(pinned)}')
        require(all(pins[rid]['target_code'] == target for rid in pinned), f'Reviewed target drift: {cohort}')
        # A semantic cohort, not "everything on the source code".
        require({pins[rid]['before']['cleaned_name'] for rid in pinned} == {cleaned},
                f'Reviewed cohort is not a single cleaned name: {cohort}')
        for rid in pinned:
            before = pins[rid]['before']
            require(before['master_ingredient_code'] == source, f'Reviewed source drift: {cohort}')
            require(before['match_method'] == 'PRESET_ALIAS_MATCH' and before['match_confidence'] == '0.98',
                    f'Reviewed provenance drift: {rid}')
            require(expected[rid]['match_method'] == before['match_method']
                    and expected[rid]['match_confidence'] == before['match_confidence'],
                    f'Match provenance not preserved: {rid}')
            # Raw and parsed evidence must survive untouched.
            for field in ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                          'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g'):
                require(expected[rid][field] == before[field], f'Raw/parsed field moved: {rid}.{field}')
            require(expected[rid]['master_ingredient_name'] == by_code[target]['name_vi'],
                    f'Target display name drift: {rid}')
    # Never select by code alone: the pins plus the reviewed keeps must exhaust
    # each source population, so no unreviewed row can ride along on a code match.
    # Asserted against BOTH the reviewed before population and the repaired one --
    # the same tolerance the row-level pins use -- because plan() is re-run as the
    # post-apply read-back and on every idempotent replay, when 4048 holds only the
    # skunk-vine row and 4051 holds bare `măng` plus the 20 repaired dried rows.
    guards = review['guards']
    cohort_ids = {c: {rid for rid, pin in pins.items() if pin['cohort'] == c} for c in COHORTS}
    dried, bare = cohort_ids['mang_kho_4048_to_4051'], {r['id'] for r in guards['bare_mang_rows']}
    fresh = cohort_ids['mang_tuoi_4051_to_4053'] | cohort_ids['mang_tuoi_bao_4051_to_4053']
    skunk = {r['id'] for r in guards['la_mo_long_rows']}
    for code, before_pop, after_pop in (('4048', dried | skunk, skunk),
                                        ('4051', fresh | bare, bare | dried)):
        population = {r['id'] for r in ingredients if r['master_ingredient_code'] == code}
        require(population in (before_pop, after_pop), f'Unreviewed rows on source code {code}')

    def transform(rows):
        mutable = set(NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name',
                                    'match_method', 'match_confidence'}
        return [dict(r, **{k: v for k, v in expected[r['id']].items() if k in mutable})
                if r['id'] in expected else dict(r) for r in rows]
    new_ing, new_ing_json = transform(ingredients), transform(ingredients_json)
    parity(new_ing, new_ing_json)
    untouched = [r for r in ingredients if r['id'] not in pins]
    require([logical(r) for r in untouched]
            == [logical(r) for r in new_ing if r['id'] not in pins], 'A row outside the reviewed 55 changed')

    populations = {code: sum(1 for r in new_ing if (r['master_ingredient_code'] or '') == code)
                   for code in EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in new_ing if r['match_method'] == 'UNMATCHED')
    require(populations == EXPECTED_POPULATIONS, f'Final population drift: {populations}')
    require(populations['UNMATCHED'] == sum(1 for r in new_ing if not (r['master_ingredient_code'] or '').strip()),
            'UNMATCHED/blank-code mismatch')
    corpus_nulls = {f: sum(1 for r in new_ing if r[f] in (None, '')) for f in NUTRIENTS}
    require(corpus_nulls == EXPECTED_CORPUS_NULLS, f'Corpus null drift: {corpus_nulls}')
    guard_measured = guard_state(new_ing, new_aliases, review)

    ordered = sorted(pins)
    combined = nutrient_report([pins[rid]['before'] for rid in ordered], [expected[rid] for rid in ordered])
    require({f: combined[f]['known_sum_delta'] for f in NUTRIENTS} == EXPECTED_NUTRITION_DELTA,
            f"Nutrition delta drift: {[combined[f]['known_sum_delta'] for f in NUTRIENTS]}")
    require({f: (combined[f]['before_null_count'], combined[f]['after_null_count']) for f in NUTRIENTS}
            == EXPECTED_NULL_TRANSITIONS, 'Null transition drift')
    require(combined['fat_g']['null_to_value'] == EXPECTED_FAT_NULL_TO_VALUE,
            f"fat null->value drift: {combined['fat_g']['null_to_value']}")
    require(all(combined[f]['value_to_null'] == 0 for f in NUTRIENTS),
            'A repaired row lost a known nutrient value')
    # Every populated nutrient must be the live TARGET catalog column scaled by the
    # row's OWN weight; nothing is copied forward and no null is coerced to zero.
    # Scaling goes through nlp.nutrition.scale_nutrition, which is the project's
    # convention (AGENTS.md section 9) and is load-bearing rather than incidental:
    # it forms the factor first, so `2.1 * (150/100)` is 3.1500000000000004 and
    # rounds to 3.2, where the equally reasonable `2.1 * 150 / 100` is exactly 3.15
    # and rounds to 3.1. One reviewed row (`Măng khô 150 gr`) sits on that boundary.
    # Re-deriving with a different multiplication order would assert a convention
    # the live corpus does not use; the independent content of this check is the
    # source of the value, not a second rounding rule.
    for rid in ordered:
        target = by_code[pins[rid]['target_code']]
        weight = float(expected[rid]['estimated_weight_g'])
        for field, column in NUTRITION_FIELDS.items():
            want = scale_nutrition(target[column], weight / 100.0, 1)
            if want is None:
                require(expected[rid][field] is None, f'Missing nutrient coerced: {rid}.{field}')
            else:
                require(expected[rid][field] is not None and float(expected[rid][field]) == want,
                        f'Nutrient not recomputed from the target catalog: {rid}.{field}')

    cohort_nutrition = {}
    for cohort in COHORTS:
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        cohort_nutrition[cohort] = nutrient_report([pins[rid]['before'] for rid in ids],
                                                   [expected[rid] for rid in ids])
    require({c: {f: n[f]['known_sum_delta'] for f in NUTRIENTS} for c, n in cohort_nutrition.items()}
            == EXPECTED_COHORT_NUTRITION_DELTA, 'Reviewed cohort nutrition delta drift')

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
              'status_transitions': {rid: f"{t['before'][0]} -> {t['after'][0]}" for rid, t in transitions.items()
                                     if rid in labels}}
    require(set(transitions) == EXPECTED_MISSING_COUNT_RECIPES, f'missing_nutrition_count radius drift: {status}')
    require(status['status_transitions'] == EXPECTED_STATUS_LABEL_TRANSITIONS, f'Status transition drift: {status}')
    parity(new_recipes, new_recipes_json)

    relationships = read_json(root / DATA / 'recipe_name_alias_decisions.json')['relationships']
    outputs, _ = compose_reviewed_aliases(new_recipes, new_ing, cat, relationships)
    baseline_recipes = deepcopy(recipes)
    _apply_rollups(baseline_recipes, {k: v for k, v in baseline_rollups.items() if k in recipes_affected})
    baseline_outputs, _ = compose_reviewed_aliases(baseline_recipes, baseline_ing, cat, relationships)
    canonical = {}
    for name in ('canonical_recipes.csv', 'canonical_recipe_ingredients.csv', 'recipe_canonical_mapping.csv'):
        old_rows = read_csv(root / DATA / name)
        key = 'original_recipe_id' if name == 'recipe_canonical_mapping.csv' else 'id'
        before, after = index(baseline_outputs[name], key), index(outputs[name], key)
        require(index(old_rows, key).keys() == after.keys() == before.keys(), f'Canonical ID drift: {name}')
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
            canonical[name] = {'changed_count': len(changed)}
        require(len(changed) == EXPECTED_CANONICAL[name], f'Canonical radius drift: {name}={len(changed)}')

    files = {ALIASES: new_aliases,
             DATA/'recipe_ingredients.csv': new_ing, DATA/'recipe_ingredients.json': new_ing_json,
             DATA/'recipes.csv': new_recipes, DATA/'recipes.json': new_recipes_json}
    before_files = {ALIASES: aliases, DATA/'recipe_ingredients.csv': ingredients,
                    DATA/'recipe_ingredients.json': ingredients_json, DATA/'recipes.csv': recipes,
                    DATA/'recipes.json': recipes_json}
    require(CAT not in files, 'The catalog must not be in this batch write set')
    changed_now = [rid for rid in pins if logical(live[rid]) != logical(expected[rid])]
    report = dict(
        policy='BAMBOO_SHOOT_ALIAS_FIX',
        root_cause=('Three alias keys have pointed at the wrong catalog identity since the original '
                    'dataset commit: `măng khô` at 4048 Lá mơ lông (skunk vine, not bamboo) and '
                    '`măng tươi` / `măng tươi bào` at 4051 Măng tre, khô (dried, for explicitly fresh '
                    'rows). All three resolve at PRESET_ALIAS_MATCH 0.98, the earliest scored stage, '
                    'so 55 rows carried the wrong identity and the wrong nutrition with high '
                    'confidence while the already-correct siblings `măng tre khô` and `măng tre tươi` '
                    'sat beside them contradicting them.'),
        rows_repaired=EXPECTED_ROWS, rows_pending=len(changed_now), recipes_affected=EXPECTED_RECIPES,
        catalog_count=750, catalog_modified=False, embeddings_rebuilt=False,
        catalog_identities={c: {'name_vi': by_code[c]['name_vi'], 'name_en': by_code[c]['name_en'],
                                'energy_kcal': by_code[c]['energy_kcal'], 'water_g': by_code[c]['water_g'],
                                'raw_backed': True}
                            for c in sorted(EXPECTED_CATALOG_IDENTITY)},
        alias_diff={k: {'before': review['aliases_before'][k], 'after': v}
                    for k, v in sorted(ALIAS_PATCHES.items())},
        alias_keeps=ALIAS_KEEPS, alias_map_size=len(new_aliases),
        populations=populations, corpus_nulls=corpus_nulls,
        combined_nutrition=combined,
        recipe_status=status, canonical=canonical,
        canonical_id_drift=0, representative_drift=0,
        guards=guard_measured,
        affected_recipe_ids=sorted(recipes_affected),
        row_outcomes={rid: dict(cohort=pins[rid]['cohort'], before=pins[rid]['before'], after=expected[rid])
                      for rid in ordered},
        cohorts={}, exclusions=EXCLUSIONS)
    report[DEFERRAL_KEY] = dict(DEFERRAL, measured=guard_measured['bare_mang'])
    recipe_before, recipe_after = index(recipes_json), index(new_recipes_json)
    report['recipe_outcomes'] = {rid: {'before': recipe_before[rid], 'after': recipe_after[rid]}
                                 for rid in sorted(recipes_affected)}
    for cohort, (source, target, _count, cleaned) in COHORTS.items():
        ids = sorted(rid for rid in pins if pins[rid]['cohort'] == cohort)
        report['cohorts'][cohort] = dict(
            source_code=source, target_code=target, cleaned_name=cleaned, row_count=len(ids),
            recipe_count=len({expected[rid]['recipe_id'] for rid in ids}), row_ids=ids,
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
    # The repair must not draw a cultivar phrase into the repaired bamboo band.
    cultivars = {}
    batch = matcher.match_batch(list(CULTIVAR_PROBES), raw_contexts=list(CULTIVAR_PROBES))
    for (query, code), batched in zip(CULTIVAR_PROBES.items(), batch):
        single = matcher.match(query, raw_context=query)
        observed = {(single['matched_item'] or {}).get('code'), (batched['matched_item'] or {}).get('code')}
        require(observed == {code}, f'Cultivar probe drift: {query}: {observed}')
        require(single['method'].startswith('BERT') and batched['method'].startswith('BERT'),
                f'Cultivar phrase acquired a dictionary route: {query}')
        cultivars[query] = {'code': code, 'single_method': single['method'], 'batch_method': batched['method']}
    return result, cultivars


def write_report(report, out):
    out.mkdir(parents=True, exist_ok=True)
    (out/'applied_fix.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = ['# Bamboo-shoot alias corruption repair', '',
             f"Policy: BAMBOO_SHOOT_ALIAS_FIX. {report['rows_repaired']} ingredient rows "
             f"/ {report['recipes_affected']} source recipes.", '',
             '## Root cause', '', report['root_cause'], '',
             'The catalog is **not** modified and embeddings are **not** rebuilt. All four identities '
             'below are raw Viện Dinh Dưỡng source rows, not project extensions, and the repair uses '
             'the preparation state each row\'s own `name_en` already asserts.', '',
             '| Code | name_vi | name_en | kcal/100 g | water g/100 g |', '|---|---|---|---:|---:|']
    for code, c in report['catalog_identities'].items():
        lines.append(f"| {code} | {c['name_vi']} | {c['name_en']} | {c['energy_kcal']} | {c['water_g']} |")
    lines += ['', '## Exact alias changes', '',
              f"Alias map size {report['alias_map_size']} (unchanged; nothing added, nothing removed).", '',
              '| Alias | Before | After | Why |', '|---|---|---|---|',
              '| măng khô | 4048 `Lá mơ lông` | 4051 `Măng tre, khô` | skunk vine is not bamboo; '
              'agrees with the existing `măng tre khô` → 4051 |',
              '| măng tươi | 4051 `Măng tre, khô` | 4053 `Măng tre` | explicit `tươi`; agrees with the '
              'existing `măng tre tươi` → 4053 |',
              '| măng tươi bào | 4051 `Măng tre, khô` | 4053 `Măng tre` | explicit `tươi`; `bào` is a '
              'cut, not a state |', '',
              'Reviewed aliases that were already correct and stay put: ' +
              ', '.join(f'`{k}` → {v}' for k, v in report['alias_keeps'].items()) + '.', '',
              '## Processed rows and nutrition', '',
              'Nutrition sums include known values only; missing values remain null. Every populated '
              'value is the live target catalog column scaled by the row\'s own weight. Exact '
              f"before/after records for all {report['rows_repaired']} ingredient rows and "
              f"{report['recipes_affected']} recipes are in [applied_fix.json](applied_fix.json).", '',
              '| Cohort | Cleaned name | Source | Target | Rows | Recipes | kcal | Protein | Fat | Carbs |',
              '|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for name, c in report['cohorts'].items():
        lines.append(f"| {name} | `{c['cleaned_name']}` | {c['source_code']} | {c['target_code']} | "
                     f"{c['row_count']} | {c['recipe_count']} | "
                     + ' | '.join(c['nutrition'][f]['known_sum_delta'] for f in NUTRIENTS) + ' |')
    lines += ['', '| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |',
              '|---|---:|---:|---:|---:|']
    for field, n in report['combined_nutrition'].items():
        lines.append(f"| {field} | {n['before_known_sum']} | {n['after_known_sum']} | {n['known_sum_delta']} | "
                     f"{n['before_null_count']} → {n['after_null_count']} |")
    lines += ['', 'The only null transition is `fat_g` null → real on the 20 `măng khô` rows: 4048 carries '
              'no fat figure and 4051 carries 2.1 g/100 g, so the value comes from the live target '
              'catalog. Nothing moves value → null and no missing nutrient is coerced to zero.', '',
              'Corpus-wide null counts after: ' + json.dumps(report['corpus_nulls']) + '.', '',
              'Recipe rollups: ' + json.dumps(report['recipe_status'], ensure_ascii=False) +
              ' — `missing_nutrition_count` keys on null calories only, and no reviewed row has null '
              'calories before or after, so no recipe changes label.', '',
              '## Final populations', '', '| Code | Rows |', '|---|---:|']
    for code, count in report['populations'].items():
        lines.append(f'| {code} | {count} |')
    lines += ['', '## Reviewed keeps, measured', '',
              'Verified against the repaired data, not asserted: ' +
              json.dumps({k: v for k, v in report['guards'].items() if k not in ('bare_mang', 'la_mo_long')},
                         ensure_ascii=False) + '. The single genuine `Lá mơ lông` row is the entire '
              '4048 population after the repair.', '',
              '## Matcher replay', '', '| Query | Code | Single route | Batch route |', '|---|---|---|---|']
    for query, result in report.get('matcher_replay', {}).items():
        lines.append(f"| {query} | {result['code']} | {result['single_method']} {result['single_confidence']} "
                     f"| {result['batch_method']} {result['batch_confidence']} |")
    if report.get('cultivar_probes'):
        lines += ['', 'Cultivar and preparation phrases with no catalog identity keep their pre-existing '
                  'neural verdicts and acquire no dictionary route — the repair does not widen the '
                  'bamboo band: ' +
                  ', '.join(f"`{q}` → {v['code']}" for q, v in report['cultivar_probes'].items()) + '.']
    deferral = report[DEFERRAL_KEY]
    lines += ['', '## Bare `măng` — ' + deferral['status'], '',
              f"`{DEFERRAL_KEY} = {deferral['status']}`. Alias: {deferral['alias']}. "
              f"Rows: {deferral['rows']}, asserted byte-for-byte unchanged.", '',
              '- **Corpus evidence.** ' + deferral['corpus_evidence'],
              '- **Why not 4053.** ' + deferral['why_not_4053'],
              '- **Why not removed.** ' + deferral['why_not_removed'],
              '- **Why not cleared.** ' + deferral['why_not_cleared'],
              '- **Nutrition left wrong.** ' + deferral['nutrition_left_wrong'],
              '- **Parser note.** ' + deferral['parser_note'], '',
              '## Canonical propagation', '', '| Artifact | Changed logical records |', '|---|---:|']
    for name, values in report['canonical'].items():
        lines.append(f"| {name} | {values['changed_count']} |")
    mapping = report['canonical'].get('recipe_canonical_mapping.csv', {})
    ingredients = report['canonical'].get('canonical_recipe_ingredients.csv', {})
    lines += ['', f"The {report['recipes_affected']} affected recipes span "
              f"{mapping.get('canonical_groups_involved')} canonical groups. "
              f"{ingredients.get('reviewed_rows_absent')} of the reviewed rows belong to non-winning "
              'duplicates and so do not appear in `canonical_recipe_ingredients.csv`, which is also why '
              f"{report['canonical']['canonical_recipes.csv']['changed_count']} representative rows change "
              f"rather than {mapping.get('canonical_groups_involved')}. "
              f"{mapping.get('changed_count')} mapping rows change content, all of them "
              '`măng khô` recipes, and only in ' + ', '.join(f'`{f}`' for f in mapping.get('changed_fields', [])) +
              ' — clearing a null fat clears a nutrition anomaly. The 35 fresh-bamboo rows swap one fully '
              'populated identity for another and move no counter. Canonical ID drift = 0; representative '
              'drift = 0.', '',
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
    # The catalog does not move, so the cache cannot need rebuilding. Pin it.
    cache_digest = hashlib.sha256(cache.read_bytes()).hexdigest() if cache.exists() else None
    catalog_digest = hashlib.sha256((root/CAT).read_bytes()).hexdigest()
    if not changed and prior.exists():
        previous = read_json(prior)
        if previous.get('validation', {}).get('complete'):
            require(cache_digest == previous['embeddings']['sha256'], 'Embedding cache drift')
            require(embedding_input_digest(read_csv(root/CAT)) == previous['embeddings']['input_sha256'],
                    'Embedding catalog-input drift')
            verify_canonical(root)
            previous = dict(previous, rows_pending=0, idempotent=True)
            # A replay re-verifies the blast radius and refreshes the recorded git
            # state / test summary without touching any data file.
            previous['validation'] = dict(previous['validation'], **git_blast_radius(root))
            previous['git'] = git_state(root)
            if tests:
                previous['tests'] = tests
            write_report(previous, out)
            return previous
        report = dict(previous, rows_pending=0)
    interim_before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (root/'data/interim').rglob('*') if p.is_file()}
    # Aliases first, then processed rows and rollups. The catalog is never written.
    for path in (ALIASES, DATA/'recipe_ingredients.csv', DATA/'recipe_ingredients.json',
                 DATA/'recipes.csv', DATA/'recipes.json'):
        if path not in changed:
            continue
        if path.suffix == '.csv':
            write_csv(root/path, files[path], list(files[path][0]))
        else:
            write_json(root/path, files[path])
    report['status'] = 'processed_applied_validation_pending'
    write_report(report, out)
    require(hashlib.sha256((root/CAT).read_bytes()).hexdigest() == catalog_digest, 'Catalog file changed')
    matcher = VietnameseIngredientMatcher(root/CAT)
    matcher._init_model()
    require(len(matcher.catalog) == 750, f'Catalog row count drift: {len(matcher.catalog)}')
    require(cache.exists() and hashlib.sha256(cache.read_bytes()).hexdigest() == cache_digest,
            'Embedding cache was rebuilt; this batch must not touch it')
    report['embeddings'] = dict(rebuilt=False, tracked=False, reused_existing_cache=True,
                                shape=list(matcher.catalog_embeddings.shape), sha256=cache_digest,
                                input_sha256=embedding_input_digest(matcher.catalog))
    report['matcher_replay'], report['cultivar_probes'] = replay(matcher)
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
                                catalog_unchanged=True, embeddings_unchanged=True,
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
    require(catalog == set(), f'Catalog rows changed vs HEAD: {catalog}')
    aliases_before = json.loads(head(str(ALIASES).replace('\\', '/')))
    aliases_after = read_json(root / ALIASES)
    keys = {k for k in aliases_before.keys() | aliases_after.keys()
            if aliases_before.get(k) != aliases_after.get(k)}
    require(keys == set(ALIAS_PATCHES), f'Alias keys changed vs HEAD: {sorted(keys)}')
    require(len(aliases_before) == len(aliases_after) == ALIAS_MAP_SIZE, 'Alias map size changed vs HEAD')
    return dict(rows_changed_vs_git_head=len(rows), recipes_changed_vs_git_head=len(recipes),
                catalog_rows_changed_vs_git_head=0, alias_keys_changed_vs_git_head=len(keys),
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
