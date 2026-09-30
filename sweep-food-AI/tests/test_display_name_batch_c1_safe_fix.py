"""DISPLAY_NAME_BATCH_C1 regression: catalog 4016 `Dưa chuột (dưa leo)` -> `Cải xanh`.

Every assertion here is stated against live data, the frozen reviewed manifest or
the applied report. None consults version control: a working-tree-vs-HEAD diff is
only an invariant while the batch is unstaged and inverts the moment it lands, so
blast radius is pinned by row id, population and null count instead.
"""

import csv
import hashlib
import json
import subprocess
import unicodedata

import pytest

from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition
from nlp.qwen_matching import _QWEN_MAPPER_RULES, build_mapper_rules, map_clean_to_master
from scripts.eda import apply_display_name_batch_c1_safe_fix as fix
from scripts.eda import audit_qwen_matching as audit

NUTRIENTS = fix.NUTRIENTS
REPORT = fix.OUT / 'applied_fix.json'
# The reviewed single-row decisions, by their short ids.
DRIED = fix.DRIED_SALTED_NAPA_ROW
GREEN = fix.GREEN_CABBAGE_ROW
SALTED = fix.SALTED_NAPA_ROW


def norm(value):
    return unicodedata.normalize('NFC', value or '').lower()


@pytest.fixture(scope='module')
def reviewed():
    return fix.read_json(fix.REVIEW)


@pytest.fixture(scope='module')
def pins(reviewed):
    return {p['before']['id']: p for p in reviewed['rows']}


@pytest.fixture(scope='module')
def live_catalog_rows():
    return fix.read_csv(fix.ROOT / fix.CAT)


@pytest.fixture(scope='module')
def live_catalog(live_catalog_rows):
    return {r['code']: r for r in live_catalog_rows}


@pytest.fixture(scope='module')
def live_aliases():
    return fix.read_json(fix.ROOT / fix.ALIASES)


@pytest.fixture(scope='module')
def live_rows():
    return fix.read_csv(fix.ROOT / fix.DATA / 'recipe_ingredients.csv')


@pytest.fixture(scope='module')
def live_index(live_rows):
    return fix.index(live_rows)


@pytest.fixture(scope='module')
def applied():
    assert REPORT.exists(), 'run scripts/eda/apply_display_name_batch_c1_safe_fix.py --apply'
    return fix.read_json(REPORT)


@pytest.fixture(scope='module')
def matcher():
    pytest.importorskip('torch')
    from nlp.entity_matcher import VietnameseIngredientMatcher
    return VietnameseIngredientMatcher(fix.ROOT / fix.CAT)


def full_id(pins, short):
    matches = [rid for rid in pins if rid.startswith(short)]
    assert len(matches) == 1, short
    return matches[0]


# --- catalog ----------------------------------------------------------------

def test_applied_catalog_rename(live_catalog):
    assert live_catalog['4016']['name_vi'] == 'Cải xanh' == fix.CATALOG_NAME_VI_AFTER
    assert fix.CATALOG_PATCHES == {'4016': {'name_vi': 'Cải xanh'}}


def test_catalog_changes_nothing_but_the_display_name(reviewed, live_catalog):
    """Code, name_en, both categories and every nutrition column, byte-for-byte."""
    before = next(r for r in reviewed['catalog_before'] if r['code'] == '4016')
    assert before['name_vi'] == fix.CATALOG_NAME_VI_BEFORE == 'Dưa chuột (dưa leo)'
    live = live_catalog['4016']
    for field in before:
        if field == 'name_vi':
            continue
        assert live[field] == before[field], field
    assert live['code'] == '4016'
    assert live['name_en'] == fix.CATALOG_NAME_EN == 'Mustard greens,   raw'


def test_the_repair_is_justified_by_the_rows_own_name_en(live_catalog):
    """The identity comes from the source row, not from the review's say-so."""
    assert 'mustard greens' in norm(live_catalog['4016']['name_en'])
    assert live_catalog['4027']['name_en'] == 'Cucumber, raw'
    assert live_catalog['4027']['name_vi'] == 'Dưa chuột'


def test_catalog_row_count_unchanged(live_catalog_rows, reviewed):
    assert len(live_catalog_rows) == reviewed['catalog_count'] == 750


def test_duplicate_display_name_set_is_unchanged(live_catalog_rows):
    """C1 neither adds to nor removes from the deferred collision set.

    `Dưa chuột (dưa leo)` was never a duplicate of 4027's `Dưa chuột`, which is
    exactly why this corruption survived a duplicate-name sweep, and `Cải xanh`
    is unique in the catalog after the rename.
    """
    assert fix.duplicate_names(live_catalog_rows) == fix.EXPECTED_DUPLICATE_NAMES
    assert fix.EXPECTED_DUPLICATE_NAMES == {'nấm kim châm', 'thịt trâu, đùi'}
    assert sum(1 for r in live_catalog_rows if norm(r['name_vi']) == 'cải xanh') == 1


def test_sibling_catalog_rows_are_untouched(reviewed, live_catalog):
    assert reviewed['catalog_identities']
    for code, before in reviewed['catalog_identities'].items():
        if code in fix.CATALOG_PATCHES:
            continue
        assert live_catalog[code] == before, code


def test_no_other_catalog_row_changed(reviewed, live_catalog_rows):
    """Not one row of the manifest's frozen sibling table moved.

    4016 is deliberately absent from that table -- it is the row this batch
    repairs, and it is frozen separately in `catalog_before` so the rename can be
    asserted field by field rather than hidden among the untouched siblings.
    """
    frozen = reviewed['catalog_identities']
    assert '4016' not in frozen
    assert len(frozen) >= 20
    moved = [r['code'] for r in live_catalog_rows
             if r['code'] in frozen and r != frozen[r['code']]]
    assert moved == []


# --- Qwen mapper ------------------------------------------------------------

def test_qwen_mapper_partitions_unchanged(live_catalog):
    active, disabled = build_mapper_rules(live_catalog)
    assert {'active': len(active), 'disabled': len(disabled)} == fix.EXPECTED_QWEN_RULE_COUNTS
    assert len(active) == 29 and len(disabled) == 20


def test_the_4016_mapper_rule_is_still_disabled(live_catalog):
    """The rename must not reactivate a rule through the A1 identity check."""
    terms, code, name = fix.QWEN_RULE_MUST_STAY_DISABLED
    assert (terms, code, name) in _QWEN_MAPPER_RULES
    active, disabled = build_mapper_rules(live_catalog)
    assert not any(r[:3] == (terms, code, name) for r in active)
    assert any(r[:3] == (terms, code, name) for r in disabled)
    for term in terms:
        assert map_clean_to_master(term, active) == (None, None)


def test_the_forbidden_name_was_not_used(live_catalog):
    assert fix.FORBIDDEN_CATALOG_NAME == 'Cải bẹ trắng (cải thìa/thảo)'
    assert live_catalog['4016']['name_vi'] != fix.FORBIDDEN_CATALOG_NAME
    assert not any(name == live_catalog['4016']['name_vi']
                   for _, code, name in _QWEN_MAPPER_RULES if code == '4016')


def test_nlp_qwen_matching_source_was_not_modified():
    source = (fix.ROOT / 'nlp/qwen_matching.py').read_text(encoding='utf-8')
    assert '("cải con", "cải mầm", "cải thìa")' in source.replace("'", '"')
    assert 'Cải bẹ trắng (cải thìa/thảo)' in source


# --- aliases ----------------------------------------------------------------

def test_exactly_twenty_alias_actions():
    actions = len(fix.ALIAS_REPOINTS) + len(fix.ALIAS_REMOVALS) + len(fix.ALIAS_ADDITIONS)
    assert actions == fix.EXPECTED_ALIAS_ACTIONS == 20
    assert len(fix.ALIAS_REPOINTS) == 10
    assert len(fix.ALIAS_REMOVALS) == 2
    assert len(fix.ALIAS_ADDITIONS) == 8
    assert set(fix.ALIAS_REPOINTS).isdisjoint(fix.ALIAS_REMOVALS)
    assert set(fix.ALIAS_REPOINTS).isdisjoint(fix.ALIAS_ADDITIONS)
    assert set(fix.ALIAS_REMOVALS).isdisjoint(fix.ALIAS_ADDITIONS)
    assert set(fix.ALIAS_KEEPS).isdisjoint(
        set(fix.ALIAS_REPOINTS) | set(fix.ALIAS_REMOVALS) | set(fix.ALIAS_ADDITIONS))


def test_alias_map_size(live_aliases, reviewed):
    assert reviewed['alias_map_size'] == fix.ALIAS_MAP_SIZE_BEFORE == 4674
    assert len(live_aliases) == fix.ALIAS_MAP_SIZE_LIVE == 4684
    assert 4674 - len(fix.ALIAS_REMOVALS) + len(fix.ALIAS_ADDITIONS) == 4680


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_REPOINTS.items()))
def test_applied_alias_repoints(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == code
    assert reviewed['aliases_before'][alias] != code


def test_the_three_cucumber_keys_all_left_4016(reviewed):
    cucumber = {k: v for k, v in fix.ALIAS_REPOINTS.items() if v == '4027'}
    assert len(cucumber) == 3
    assert all(reviewed['aliases_before'][k] == '4016' for k in cucumber)
    assert all('dưa leo' in norm(k) for k in cucumber)


def test_the_seven_mustard_keys_all_left_red_cabbage_4011(reviewed):
    mustard = {k: v for k, v in fix.ALIAS_REPOINTS.items() if v == '4016'}
    assert len(mustard) == 7
    assert all(reviewed['aliases_before'][k] == '4011' for k in mustard)


@pytest.mark.parametrize('alias', sorted(fix.ALIAS_REMOVALS))
def test_spinach_and_kale_aliases_removed(live_aliases, alias):
    assert alias not in live_aliases
    assert alias in ('cải cải bó xôi', 'cải xoăn')


def test_no_spinach_or_kale_identity_exists_to_alias(live_catalog_rows):
    """The removals are a catalog gap, not a repoint: there is nowhere to point.

    The catalog does carry `Water spinach`, `Malabar, Ceylon spinach` and
    `Buffalo spinach` -- rau muống, mồng tơi and rau ngổ. Those are different
    plants with their own Vietnamese names, not Spinacia oleracea, and none of
    them is `cải bó xôi`. Kale is absent outright.
    """
    vi = {norm(r['name_vi']) for r in live_catalog_rows}
    en = {norm(r['name_en']) for r in live_catalog_rows}
    assert not any('bó xôi' in n or 'chân vịt' in n or 'xoăn' in n for n in vi)
    assert not any('kale' in n for n in en | vi)
    assert not any(n.startswith('spinach') for n in en)
    qualified = {n for n in en if 'spinach' in n}
    assert qualified and all(n.split()[0] in ('water', 'malabar,', 'buffalo') for n in qualified)


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_ADDITIONS.items()))
def test_applied_alias_additions(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == code
    assert alias in reviewed['aliases_absent_before']


def test_the_long_parser_damaged_key_is_deliberate(live_aliases, pins):
    """One long reviewed key for one reviewed row, never a broad generic alias."""
    assert live_aliases[fix.LONG_REVIEWED_ALIAS] == '4016'
    assert len(fix.LONG_REVIEWED_ALIAS.split()) > 6
    rid = full_id(pins, fix.LONG_REVIEWED_ALIAS_ROW)
    assert pins[rid]['before']['cleaned_name'] == fix.LONG_REVIEWED_ALIAS


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_KEEPS.items()))
def test_reviewed_alias_keeps(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == reviewed['aliases_before'][alias] == code


def test_generic_cai_and_the_cai_thia_family_are_untouched(live_aliases):
    assert live_aliases['cải'] == '4013'
    assert live_aliases['cải trắng'] == '4021'
    assert live_aliases['cải thìa'] == '4135'
    assert live_aliases['cải mầm'] == live_aliases['mầm cải'] == '20050'
    assert live_aliases['cải xanh tươi'] == '4016'


def test_no_new_alias_targets_4094(live_aliases, reviewed):
    """Explicit invariant. 4094 is itself display-name corrupted."""
    assert fix.NO_NEW_ALIAS_TO == '4094'
    assert '4094' not in set(fix.ALIAS_ADDITIONS.values()) | set(fix.ALIAS_REPOINTS.values())
    on_4094 = {k for k, v in live_aliases.items() if v == '4094'}
    assert on_4094.isdisjoint(fix.ALIAS_ADDITIONS)
    assert on_4094.isdisjoint(fix.ALIAS_REPOINTS)
    for key in ('bông cải xanh', 'bông cải xanh cắt nhỏ', 'ăn kèm bông cải xanh', 'súp lơ'):
        assert live_aliases[key] == reviewed['aliases_before'][key] == '4094'


def test_only_the_reviewed_aliases_moved(live_aliases, reviewed):
    moved = {k for k, before in reviewed['aliases_before'].items()
             if live_aliases.get(k) != before}
    assert moved == set(fix.ALIAS_REPOINTS) | set(fix.ALIAS_REMOVALS)
    added = {k for k in fix.ALIAS_ADDITIONS if k in live_aliases}
    assert added == set(fix.ALIAS_ADDITIONS)


def test_every_alias_on_the_repaired_identity_is_reviewed(live_aliases):
    reviewed_on_4016 = ({k for k, v in fix.ALIAS_REPOINTS.items() if v == '4016'}
                        | {k for k, v in fix.ALIAS_ADDITIONS.items() if v == '4016'}
                        | {k for k, v in fix.ALIAS_KEEPS.items() if v == '4016'})
    assert {k for k, v in live_aliases.items() if v == '4016'} == reviewed_on_4016
    assert not any('dưa' in norm(k) for k in reviewed_on_4016)


def test_every_alias_reaching_the_cucumber_identity_names_a_cucumber(live_aliases):
    assert all('dưa' in norm(k) for k, v in live_aliases.items() if v == '4027')


# --- rows: cohorts and exact id sets ----------------------------------------

def test_manifest_shape(reviewed, pins):
    assert len(pins) == len(reviewed['rows']) == fix.EXPECTED_ROWS == 355
    changed = {rid for rid, p in pins.items() if p['cohort'] != fix.NAME_REFRESH_COHORT}
    assert len(changed) == fix.EXPECTED_CHANGED_ROWS == 345
    assert len(pins) - len(changed) == fix.EXPECTED_NAME_REFRESH_ROWS == 10


@pytest.mark.parametrize('cohort,spec', sorted(fix.COHORTS.items()))
def test_reviewed_cohort_decisions_and_source_preservation(pins, live_catalog, cohort, spec):
    source, target, count, provenance = spec
    ids = {rid for rid, p in pins.items() if p['cohort'] == cohort}
    assert len(ids) == count
    for rid in ids:
        pin = pins[rid]
        assert pin['target_code'] == target
        if source is None:
            assert pin['before']['match_method'] == 'UNMATCHED'
            assert not (pin['before']['master_ingredient_code'] or '').strip()
        else:
            assert pin['before']['master_ingredient_code'] == source
        after = fix.expected_row(pin, live_catalog)
        if provenance in ('preserved', 'name_refresh'):
            assert after['match_method'] == pin['before']['match_method']
            assert after['match_confidence'] == pin['before']['match_confidence']
        elif provenance == 'measured':
            assert pin['match_after']
        for field in ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                      'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g'):
            assert after[field] == pin['before'][field], (rid, field)


def test_exact_248_cucumber_ids(pins, live_index):
    ids = {rid for rid, p in pins.items() if p['cohort'] == 'cucumber_4016_to_4027'}
    assert len(ids) == 248
    cleaned = {pins[rid]['before']['cleaned_name'] for rid in ids}
    assert cleaned == {'dưa leo', 'ăn kèm dưa leo', 'dưa leo cắt sợi'}
    counts = {name: sum(1 for rid in ids if pins[rid]['before']['cleaned_name'] == name)
              for name in cleaned}
    assert counts == {'dưa leo': 235, 'ăn kèm dưa leo': 11, 'dưa leo cắt sợi': 2}
    for rid in ids:
        row = live_index[rid]
        assert row['master_ingredient_code'] == '4027'
        assert row['master_ingredient_name'] == 'Dưa chuột'
        assert (row['match_method'], row['match_confidence']) == ('PRESET_ALIAS_MATCH', '0.98')


def test_no_cucumber_row_remains_on_4016(live_rows):
    assert not [r for r in live_rows if r['master_ingredient_code'] == '4016'
                and 'dưa' in norm(r['cleaned_name'])]


def test_exact_40_mustard_ids_from_4011(pins, live_index):
    ids = {rid for rid, p in pins.items()
           if p['cohort'] in ('mustard_alias_4011_to_4016', 'mustard_exact_4011_to_4016')}
    assert len(ids) == 40
    cleaned = {pins[rid]['before']['cleaned_name'] for rid in ids}
    assert cleaned == {'cải bẹ xanh', 'rau cải xanh', 'cải xanh', 'ăn kèm cải bẹ xanh'}
    assert all(pins[rid]['before']['master_ingredient_code'] == '4011' for rid in ids)
    for rid in ids:
        row = live_index[rid]
        assert row['master_ingredient_code'] == '4016'
        assert row['master_ingredient_name'] == 'Cải xanh'


def test_the_five_exact_match_rows_are_the_cai_xanh_rows(pins, live_index):
    ids = {rid for rid, p in pins.items() if p['cohort'] == 'mustard_exact_4011_to_4016'}
    assert len(ids) == 5
    assert {pins[rid]['before']['cleaned_name'] for rid in ids} == {'cải xanh'}
    for rid in ids:
        assert (live_index[rid]['match_method'], live_index[rid]['match_confidence']) \
            == ('EXACT_CATALOG_MATCH', '1.0')


def test_exact_5_mustard_ids_from_4015(pins, live_index):
    ids = sorted(rid for rid, p in pins.items() if p['cohort'] == 'mustard_leaf_4015_to_4016')
    assert [rid[:8] for rid in ids] == ['0bb59e7f', '3a5e76c9', '5cf26d3d', '9a457102', 'ea622c2d']
    for rid in ids:
        assert pins[rid]['before']['master_ingredient_code'] == '4015'
        assert pins[rid]['before']['cleaned_name'] == 'lá cải xanh'
        row = live_index[rid]
        assert row['master_ingredient_code'] == '4016'
        assert (row['match_method'], row['match_confidence']) == ('PRESET_ALIAS_MATCH', '0.98')


def test_exact_5_unmatched_recoveries(pins, live_index):
    ids = sorted(rid for rid, p in pins.items()
                 if p['cohort'] == 'mustard_unmatched_recovery_to_4016')
    assert sorted(rid[:8] for rid in ids) == sorted(
        ['1c9cbc26', 'cdbdb34e', '7fc13ea8', 'fb5b5853', '3b6ffe72'])
    for rid in ids:
        assert pins[rid]['before']['match_method'] == 'UNMATCHED'
        row = live_index[rid]
        assert row['master_ingredient_code'] == '4016'
        assert (row['match_method'], row['match_confidence']) == ('PRESET_ALIAS_MATCH', '0.98')
        assert all(row[f] not in (None, '') for f in NUTRIENTS)


def test_633ea6e1_moves_to_4010_not_to_the_new_mustard_head(pins, live_index):
    """Green HEAD cabbage. Reviewed, non-reproducible, pinned by id and raw text."""
    rid = full_id(pins, GREEN)
    pin = pins[rid]
    assert pin['before']['raw_text'] == fix.GREEN_CABBAGE_RAW == 'Bắp cải xanh 1/2 cái'
    assert pin['before']['master_ingredient_code'] == '4011'
    assert pin['before']['cleaned_name'] == 'cải xanh'
    assert pin['target_code'] == '4010'
    row = live_index[rid]
    assert row['master_ingredient_code'] == '4010'
    assert row['master_ingredient_name'] == 'Cải bắp trắng'
    assert fix.NON_REPRODUCIBLE[GREEN]['matcher_would_reach'] == '4016'


def test_exact_napa_and_kimchi_dispositions(pins, live_index):
    fresh = sorted(rid for rid, p in pins.items() if p['cohort'] == 'fresh_napa_4016_to_4109')
    assert len(fresh) == 8
    assert {pins[rid]['before']['cleaned_name'] for rid in fresh} == {'cải thảo', 'lá cải thảo'}
    assert any(rid.startswith('1e759efa') for rid in fresh)
    for rid in fresh:
        row = live_index[rid]
        assert row['master_ingredient_code'] == '4109'
        assert row['master_ingredient_name'] == 'Rau cải thảo'
        assert (row['match_method'], row['match_confidence']) == ('PRESET_ALIAS_MATCH', '0.98')
        assert row['fat_g'] in (None, '')  # 4109 publishes no fat_g; null, not zero

    salted = full_id(pins, SALTED)
    assert pins[salted]['before']['raw_text'] == fix.SALTED_NAPA_RAW == 'Cải thảo muối 100 gr'
    assert live_index[salted]['master_ingredient_code'] == '4115'
    assert live_index[salted]['master_ingredient_name'] == 'Dưa cải bắp'
    assert fix.NON_REPRODUCIBLE[SALTED]['matcher_would_reach'] == '4109'

    kimchi = sorted(rid for rid, p in pins.items() if p['cohort'] == 'kimchi_4016_to_20034')
    assert sorted(rid[:8] for rid in kimchi) == ['dc0c4d64', 'fbde0c97']
    for rid in kimchi:
        assert live_index[rid]['master_ingredient_code'] == '20034'
        assert live_index[rid]['master_ingredient_name'] == 'Kim chi'


# --- the 35 curated clears --------------------------------------------------

def test_exactly_thirty_five_clears(pins):
    cleared = {rid for rid, p in pins.items() if p['target_code'] is None}
    assert len(cleared) == fix.EXPECTED_CLEARS == 35
    by_cohort = {c: sum(1 for rid in cleared if pins[rid]['cohort'] == c)
                 for c in {pins[rid]['cohort'] for rid in cleared}}
    assert by_cohort == {'spinach_clear_to_unmatched': 27, 'kale_clear_to_unmatched': 4,
                         'collision_clear_to_unmatched': 3,
                         'dried_salted_napa_clear_to_unmatched': 1}


@pytest.mark.parametrize('short', ['26fcd2f6', '27349b41', '10934e2b'])
def test_the_three_collision_clears(pins, live_index, short):
    rid = full_id(pins, short)
    assert pins[rid]['cohort'] == 'collision_clear_to_unmatched'
    assert pins[rid]['before']['master_ingredient_code'] == '4015'
    assert live_index[rid]['match_method'] == 'UNMATCHED'


def test_the_dried_salted_napa_clear_supersedes_the_audit_deferral(pins, live_index, applied):
    """Reviewer decision: CLEAR, not defer on the repaired 4016."""
    rid = full_id(pins, DRIED)
    pin = pins[rid]
    assert pin['before']['raw_text'] == fix.DRIED_SALTED_NAPA_RAW == '1 muỗng cải thảo muối khô'
    assert pin['before']['master_ingredient_code'] == '4016'
    assert pin['target_code'] is None
    assert applied['reviewer_override']['row'] == DRIED
    assert applied['reviewer_override']['audit_disposition'].startswith('DEFER')
    assert applied['reviewer_override']['reviewed_disposition'] == 'CLEAR_TO_UNMATCHED'
    row = live_index[rid]
    assert row['match_method'] == 'UNMATCHED'
    assert not (row['master_ingredient_code'] or '').strip()
    assert not (row['master_ingredient_name'] or '').strip()
    assert row['match_confidence'] in (None, '') and row['match_confidence'] != '0.0'
    assert all(row[f] in (None, '') for f in NUTRIENTS)
    # Raw and parsed evidence survives, including the weight.
    for field in ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                  'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g'):
        assert row[field] == pin['before'][field], field
    assert row['estimated_weight_g'] == '15.0'


def test_every_clear_honours_the_unmatched_contract(pins, live_index):
    for rid, pin in pins.items():
        if pin['target_code'] is not None:
            continue
        row = live_index[rid]
        assert row['match_method'] == 'UNMATCHED'
        assert not (row['master_ingredient_code'] or '').strip()
        assert not (row['master_ingredient_name'] or '').strip()
        assert row['match_confidence'] in (None, '')
        assert row['match_confidence'] != '0.0'
        assert all(row[f] in (None, '') for f in NUTRIENTS)
        for field in ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                      'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g'):
            assert row[field] == pin['before'][field], (rid, field)


def test_no_broad_guard_was_added_for_the_clears():
    """The clears are ID-pinned rows, not a matcher rule."""
    source = (fix.ROOT / 'nlp/entity_matcher.py').read_text(encoding='utf-8')
    for phrase in ('cải bó xôi', 'cải xoăn', 'cải thảo muối', 'đuôi phụng'):
        assert phrase not in source


# --- residual, excluded and deferred rows -----------------------------------

def test_residual_4016_qwen_rows_are_exactly_ten(pins, live_rows, live_index):
    residual = sorted(rid for rid, p in pins.items() if p['cohort'] == fix.NAME_REFRESH_COHORT)
    assert len(residual) == 10
    cleaned = [pins[rid]['before']['cleaned_name'] for rid in residual]
    assert sum(1 for c in cleaned if c == 'cải con') == 5
    assert sum(1 for c in cleaned if c.startswith('cải thìa')) == 5
    qwen_on_4016 = [r for r in live_rows if r['master_ingredient_code'] == '4016'
                    and r['match_method'] == 'QWEN_LLM_MATCH']
    assert {r['id'] for r in qwen_on_4016} == set(residual)


def test_the_ten_residual_rows_only_refresh_a_stale_display_name(pins, live_index):
    for rid, pin in pins.items():
        if pin['cohort'] != fix.NAME_REFRESH_COHORT:
            continue
        before, row = pin['before'], live_index[rid]
        assert before['master_ingredient_name'] == 'Cải bẹ trắng (cải thìa/thảo)'
        assert row['master_ingredient_name'] == 'Cải xanh'
        assert row['master_ingredient_code'] == before['master_ingredient_code'] == '4016'
        assert row['match_method'] == before['match_method'] == 'QWEN_LLM_MATCH'
        assert row['match_confidence'] == before['match_confidence']
        for field in NUTRIENTS:
            assert fix.logical(row)[field] == fix.logical(before)[field], (rid, field)


def test_6ce0333f_remains_stored_unmatched(reviewed, live_index):
    rid, before = next(iter(reviewed['guards']['curated_unmatched_compound'].items()))
    assert rid.startswith(fix.CURATED_UNMATCHED_ROW)
    assert 'cải xanh' in norm(before['raw_text'])
    row = live_index[rid]
    assert fix.logical(row) == fix.logical(before)
    assert row['match_method'] == 'UNMATCHED'
    assert not (row['master_ingredient_code'] or '').strip()


def test_e9b2ce8d_is_unchanged_keep_current(reviewed, live_index):
    rid, before = next(iter(reviewed['guards']['keep_current_needs_review'].items()))
    assert rid.startswith(fix.KEEP_CURRENT_ROW)
    assert fix.logical(live_index[rid]) == fix.logical(before)
    assert live_index[rid]['master_ingredient_code'] == fix.KEEP_CURRENT_CODE == '20086'


def test_the_three_unreviewed_la_cai_thao_rows_are_unchanged(reviewed, live_index):
    """C1 introduces this divergence and records it rather than acting on it."""
    rows = reviewed['guards']['introduced_divergence_unreviewed']
    assert len(rows) == 3
    for rid, before in rows.items():
        assert before['cleaned_name'] == 'lá cải thảo'
        assert fix.logical(live_index[rid]) == fix.logical(before)
        assert live_index[rid]['match_method'] == 'UNMATCHED'


@pytest.mark.parametrize('key', ['keep_current_needs_review', 'curated_unmatched_compound',
                                 'introduced_divergence_unreviewed'])
def test_excluded_rows_are_not_pinned_as_changed(reviewed, pins, key):
    assert set(reviewed['guards'][key]).isdisjoint(pins)


# --- populations, nutrition, nulls ------------------------------------------

def test_final_populations(live_rows):
    populations = {code: sum(1 for r in live_rows if (r['master_ingredient_code'] or '') == code)
                   for code in fix.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
    assert populations == fix.EXPECTED_POPULATIONS
    assert populations['4010'] == 105
    assert populations['4011'] == 0
    assert populations['4015'] == 11
    assert populations['4016'] == 60
    assert populations['4027'] == 270
    assert populations['4109'] == 73
    assert populations['4115'] == 1
    assert populations['20034'] == 75
    assert populations['UNMATCHED'] == 8495


def test_4094_population_is_unchanged(reviewed, live_rows):
    pinned = set(reviewed['guards']['population_4094_row_ids'])
    assert len(pinned) == 106
    assert {r['id'] for r in live_rows if r['master_ingredient_code'] == '4094'} == pinned


def test_final_4016_decomposes_into_the_reviewed_parts(pins, live_rows):
    on_4016 = {r['id'] for r in live_rows if r['master_ingredient_code'] == '4016'}
    expected = {rid for rid, p in pins.items()
                if p['cohort'] in ('mustard_alias_4011_to_4016', 'mustard_exact_4011_to_4016',
                                   'mustard_leaf_4015_to_4016',
                                   'mustard_unmatched_recovery_to_4016',
                                   fix.NAME_REFRESH_COHORT)}
    assert on_4016 == expected
    assert len(on_4016) == 60 == 40 + 5 + 5 + 10


def test_corpus_null_counts(live_rows):
    assert {f: sum(1 for r in live_rows if r[f] in (None, ''))
            for f in NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS
    assert fix.EXPECTED_CORPUS_NULLS == {
        'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454}


def test_no_missing_nutrition_was_zero_filled(live_rows, live_catalog):
    unmatched = [r for r in live_rows if r['match_method'] == 'UNMATCHED']
    assert len(unmatched) == 8495
    assert all(all(r[f] in (None, '') for f in NUTRIENTS) for r in unmatched)
    for code in fix.FAT_NULL_TARGETS:
        assert live_catalog[code]['fat_g'].strip() == ''


def test_reviewed_nutrition_delta_is_measured_not_the_audit_figure(pins, live_index, applied):
    changed = sorted(rid for rid, p in pins.items() if p['cohort'] != fix.NAME_REFRESH_COHORT)
    report = fix.nutrient_report([pins[rid]['before'] for rid in changed],
                                 [live_index[rid] for rid in changed])
    delta = {f: report[f]['known_sum_delta'] for f in NUTRIENTS}
    assert delta == fix.EXPECTED_NUTRITION_DELTA
    assert delta == {'calories': '-6700.7', 'protein_g': '-378.1',
                     'fat_g': '-26.2', 'carbs_g': '-1219.1'}
    # The audit's figure did not clear 2c660d89 and is recorded as superseded.
    assert delta != fix.SUPERSEDED_AUDIT_NUTRITION_DELTA
    assert applied['superseded_audit_nutrition_delta'] == fix.SUPERSEDED_AUDIT_NUTRITION_DELTA


def test_the_extra_clear_accounts_for_the_whole_difference_from_the_audit(pins, live_index):
    """Measured through the project's own scaler, never inferred from the text."""
    from decimal import Decimal
    rid = full_id(pins, DRIED)
    report = fix.nutrient_report([pins[rid]['before']], [live_index[rid]])
    for field in NUTRIENTS:
        moved = Decimal(fix.EXPECTED_NUTRITION_DELTA[field]) \
            - Decimal(fix.SUPERSEDED_AUDIT_NUTRITION_DELTA[field])
        assert Decimal(report[field]['known_sum_delta']) == moved, field


def test_cohort_nutrition_deltas(pins, live_index):
    for cohort, expected in fix.EXPECTED_COHORT_NUTRITION_DELTA.items():
        ids = sorted(rid for rid, p in pins.items() if p['cohort'] == cohort)
        report = fix.nutrient_report([pins[rid]['before'] for rid in ids],
                                     [live_index[rid] for rid in ids])
        assert {f: report[f]['known_sum_delta'] for f in NUTRIENTS} == expected, cohort


def test_null_transitions(pins, live_index):
    ids = sorted(pins)
    report = fix.nutrient_report([pins[rid]['before'] for rid in ids],
                                 [live_index[rid] for rid in ids])
    assert {f: (report[f]['before_null_count'], report[f]['after_null_count'])
            for f in NUTRIENTS} == fix.EXPECTED_NULL_TRANSITIONS
    assert {f: report[f]['value_to_null'] for f in NUTRIENTS} == fix.EXPECTED_VALUE_TO_NULL
    assert {f: report[f]['null_to_value'] for f in NUTRIENTS} == fix.EXPECTED_NULL_TO_VALUE


def test_the_extra_fat_nulls_are_missing_catalog_data(pins, live_index):
    rows = [rid for rid, p in pins.items() if p['target_code'] is not None
            and p['before']['fat_g'] not in (None, '') and live_index[rid]['fat_g'] in (None, '')]
    assert len(rows) == fix.EXPECTED_FAT_NULL_FROM_MISSING_TARGET == 9
    assert {pins[rid]['target_code'] for rid in rows} == set(fix.FAT_NULL_TARGETS) == {'4109', '4115'}


def test_every_populated_nutrient_comes_from_the_target_catalog(pins, live_index, live_catalog):
    for rid, pin in pins.items():
        if pin['target_code'] is None:
            continue
        target = live_catalog[pin['target_code']]
        weight = float(live_index[rid]['estimated_weight_g'])
        for field, column in NUTRITION_FIELDS.items():
            want = scale_nutrition(target[column], weight / 100.0, 1)
            value = live_index[rid][field]
            if want is None:
                assert value in (None, ''), (rid, field)
            else:
                assert value not in (None, '') and float(value) == want, (rid, field)


def test_no_row_outside_the_reviewed_355_changed(pins, live_rows, live_catalog):
    """Blast radius, measured against the manifest rather than against git."""
    live = fix.index(live_rows)
    for rid, pin in pins.items():
        assert fix.logical(live[rid]) == fix.logical(fix.expected_row(pin, live_catalog)), rid
    assert len(live_rows) == 63943
    populations = {code: sum(1 for r in live_rows if (r['master_ingredient_code'] or '') == code)
                   for code in fix.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
    assert populations == fix.EXPECTED_POPULATIONS


def test_untouched_sibling_identities(reviewed, live_rows):
    moved = set(fix.EXPECTED_POPULATIONS)
    frozen = reviewed['guards']['sibling_identity_row_counts']
    for code, count in frozen.items():
        if code in moved:
            continue
        assert sum(1 for r in live_rows if r['master_ingredient_code'] == code) == count, code


# --- downstream hard-code ----------------------------------------------------

def test_cucumber_hard_code_points_at_4027():
    text = (fix.ROOT / 'src/recommendation/pantry_simulator.py').read_text(encoding='utf-8')
    assert fix.DOWNSTREAM_AFTER == '("dưa chuột", "4027"'
    assert text.count(fix.DOWNSTREAM_AFTER) == 1
    assert fix.DOWNSTREAM_BEFORE not in text


def test_exactly_one_downstream_repoint_and_no_stragglers():
    found = {}
    for path in sorted((fix.ROOT / fix.DOWNSTREAM_SCAN_ROOT).rglob('*.py')):
        for code in fix.DOWNSTREAM_SCAN.findall(path.read_text(encoding='utf-8')):
            found.setdefault(code, []).append(path.name)
    assert set(found) == {'4027'}
    assert sum(len(v) for v in found.values()) == fix.EXPECTED_DOWNSTREAM_REPOINTS == 1


def test_the_repointed_code_is_the_cucumber_identity(live_catalog):
    assert live_catalog['4027']['name_en'] == 'Cucumber, raw'
    assert 'mustard' in norm(live_catalog['4016']['name_en'])


# --- audit evidence ----------------------------------------------------------

def test_wrong_4016_is_kept_and_re_keyed():
    assert '4016' in audit.WRONG
    name, synonyms, _reason = audit.WRONG['4016']
    assert name == fix.AUDIT_WRONG_NAME == 'Cải xanh'
    assert synonyms == fix.AUDIT_WRONG_SYNONYMS == 'cải con|cải thìa|cải thìa con'
    for retired in fix.AUDIT_RETIRED_SYNONYMS:
        assert retired not in synonyms
    assert 'cải thìa chua' not in synonyms


def test_audit_class_counts_are_re_measured(applied, live_rows, live_catalog):
    qwen = [r for r in live_rows if r['match_method'] == 'QWEN_LLM_MATCH']
    buckets = [audit.classify(r, live_catalog)[0] for r in qwen]
    counts = {c: buckets.count(c) for c in audit.CLASSES}
    assert len(qwen) == fix.EXPECTED_AUDIT['qwen_rows'] == 643
    assert counts == fix.EXPECTED_AUDIT['class_counts'] == {'A': 0, 'B': 549, 'C': 55, 'D': 39}
    assert fix.SUPERSEDED_AUDIT_CLASSES['qwen_rows'] == 662
    assert applied['audit_evidence']['qwen_rows'] == 643


def test_other_batches_audit_evidence_is_untouched():
    assert audit.WRONG['4015'][0] == 'Cải thìa (cải trắng)'
    assert audit.VALID['4010'][0] == 'Cải bắp trắng'


def test_the_reviewed_clear_is_protected_from_qwen_recovery(applied):
    """C1's own report proves the clear is durably blocked in production.

    Not a restatement of the exclusion table: plan() measures it against the live
    mapper on every run, so if the 4109 rule moved or the guard stopped refusing
    the line, the batch would fail closed rather than the report going stale.
    """
    protection = applied['qwen_recovery_protection']
    assert protection['row'] == DRIED
    assert protection['raw_text'] == fix.DRIED_SALTED_NAPA_RAW
    assert protection['reason'] == fix.QWEN_EXCLUSION_REASON         == 'DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET'
    assert protection['would_reach'] == '4109'
    assert protection['mechanism'] == 'nlp.qwen_matching._REVIEWED_NO_CATALOG_TARGET_RAW'
    assert protection['excluded_line_count'] == 1
    # Fresh napa and kimchi stay recoverable.
    assert set(protection['still_allowed'].values()) == {'4109'}
    assert len(protection['still_allowed']) == len(fix.QWEN_EXCLUSION_MUST_STILL_ALLOW)


# --- matcher ------------------------------------------------------------------

@pytest.mark.parametrize('query,code', sorted(fix.PROBES.items()))
def test_matcher_reaches_the_reviewed_identity(matcher, query, code):
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    assert (batched['matched_item'] or {}).get('code') == code


def test_the_248_cucumber_rows_reproduce(matcher, pins):
    ids = sorted(rid for rid, p in pins.items() if p['cohort'] == 'cucumber_4016_to_4027')
    results = matcher.match_batch([pins[rid]['before']['cleaned_name'] for rid in ids],
                                  raw_contexts=[pins[rid]['before']['raw_text'] for rid in ids])
    assert len(results) == 248
    for result in results:
        assert (result['matched_item'] or {}).get('code') == '4027'
        assert result['method'] == 'PRESET_ALIAS_MATCH'
        assert result['confidence'] == 0.98


def test_the_five_unmatched_recoveries_reproduce(matcher, pins):
    ids = sorted(rid for rid, p in pins.items()
                 if p['cohort'] == 'mustard_unmatched_recovery_to_4016')
    results = matcher.match_batch([pins[rid]['before']['cleaned_name'] for rid in ids],
                                  raw_contexts=[pins[rid]['before']['raw_text'] for rid in ids])
    for result in results:
        assert (result['matched_item'] or {}).get('code') == '4016'
        assert result['method'] == 'PRESET_ALIAS_MATCH'
        assert result['confidence'] == 0.98


def test_matcher_classification_counts(applied):
    counts = applied['matcher_classification']['counts']
    assert counts == {'A_reproducible': 308, 'B_curated_divergence': 2,
                      'C_curated_unmatched': 35, 'D_deferred_name_refresh': 10}
    assert counts['A_reproducible'] + counts['B_curated_divergence'] \
        + counts['C_curated_unmatched'] == fix.EXPECTED_CHANGED_ROWS == 345


def test_every_divergence_records_what_the_matcher_would_reach(applied):
    divergence = applied['matcher_classification']['divergence']
    classes = applied['matcher_classification']['classes']
    for key in ('B_curated_divergence', 'C_curated_unmatched', 'D_deferred_name_refresh'):
        for rid in classes[key]:
            assert divergence[rid]['reached'], rid
    assert {rid[:8] for rid in classes['B_curated_divergence']} == {GREEN, SALTED}


def test_recorded_fallthroughs_match_the_reviewed_record(applied):
    divergence = applied['matcher_classification']['divergence']
    outcomes = applied['row_outcomes']
    for cohort, want in (('spinach_clear_to_unmatched', '4010'),
                         ('kale_clear_to_unmatched', '4016'),
                         ('collision_clear_to_unmatched', '4016')):
        reached = {v['reached'] for rid, v in divergence.items()
                   if outcomes[rid]['cohort'] == cohort}
        assert reached == {want}, cohort
    assert fix.ALIAS_REMOVAL_FALLTHROUGH['cải cải bó xôi']['after'] == '4010'
    assert fix.ALIAS_REMOVAL_FALLTHROUGH['cải xoăn']['after'] == '4016'


def test_the_two_excluded_rows_diverge_as_recorded(applied):
    excluded = applied['matcher_classification']['excluded_rows']
    keep = next(v for v in excluded.values() if v['group'] == 'keep_current_needs_review')
    assert keep['stored'] == '20086' and keep['reached'] == '4016'
    curated = next(v for v in excluded.values() if v['group'] == 'curated_unmatched_compound')
    assert curated['stored'] == 'UNMATCHED' and curated['reached'] == '4016'
    introduced = [v for v in excluded.values()
                  if v['group'] == 'introduced_divergence_unreviewed']
    assert len(introduced) == 3
    assert all(v['stored'] == 'UNMATCHED' and v['reached'] == '4109' for v in introduced)


# --- embeddings ---------------------------------------------------------------

def test_embeddings_were_rebuilt_and_reload_equal(applied):
    torch = pytest.importorskip('torch')
    cache = (fix.ROOT / fix.CAT).with_name('catalog_embeddings_bkai.pt')
    assert cache.exists()
    assert applied['embeddings']['rebuilt'] is True
    assert applied['embeddings']['shape'] == [750, 768]
    assert hashlib.sha256(cache.read_bytes()).hexdigest() == applied['embeddings']['sha256']
    tensor = torch.load(cache, map_location='cpu', weights_only=True)
    assert list(tensor.shape) == [750, 768]
    catalog = fix.read_csv(fix.ROOT / fix.CAT)
    assert fix.embedding_input_digest(catalog) == applied['embeddings']['input_sha256']
    assert applied['embeddings']['build_inputs']['4016'].startswith('Cải xanh (')
    assert applied['embeddings']['next_load_equal'] is True
    assert applied['embeddings']['tracked'] is False


def test_embedding_cache_is_not_tracked():
    tracked = subprocess.run(
        ['git', 'ls-files', '--', 'data/processed/viendinhduong/catalog_embeddings_bkai.pt'],
        cwd=fix.ROOT, capture_output=True, text=True, check=True).stdout.strip()
    assert tracked == ''


# --- canonical, parity, interim, idempotence ----------------------------------

def test_canonical_radius_and_zero_identity_drift(applied):
    assert applied['canonical_id_drift'] == 0
    assert applied['representative_drift'] == 0
    assert {k: v['changed_count'] for k, v in applied['canonical'].items()} == fix.EXPECTED_CANONICAL
    mapping = applied['canonical']['recipe_canonical_mapping.csv']
    assert mapping['canonical_groups_involved'] == fix.EXPECTED_CANONICAL_GROUPS == 340
    assert mapping['canonical_groups_for_changed_rows'] \
        == fix.EXPECTED_CANONICAL_GROUPS_CHANGED_ROWS == 333
    ingredients = applied['canonical']['canonical_recipe_ingredients.csv']
    assert ingredients['reviewed_rows_absent'] == fix.EXPECTED_CANONICAL_INGREDIENT_ROWS_ABSENT == 4
    assert ingredients['changed_count'] == 355 - 4


def test_canonical_counts_are_not_the_audits_stale_estimate(applied):
    estimate = applied['superseded_audit_canonical']
    assert estimate['estimate'] != estimate['measured']
    assert estimate['measured']['processed_ingredient_rows_changed'] == 345
    assert estimate['measured']['processed_recipes_touched'] == 333
    assert estimate['measured']['nutrition_status_transitions'] == 16


def test_recipe_status_transitions(applied):
    status = applied['recipe_status']
    assert status['recipes_with_changed_missing_count'] == 37
    assert status['recipes_with_status_label_changed'] == 16
    assert status['status_transitions'] == fix.EXPECTED_STATUS_LABEL_TRANSITIONS


def test_csv_json_parity():
    for name in ('recipe_ingredients', 'recipes', 'canonical_recipes',
                 'canonical_recipe_ingredients'):
        fix.parity(fix.read_csv(fix.ROOT / fix.DATA / (name + '.csv')),
                   fix.read_json(fix.ROOT / fix.DATA / (name + '.json')))


def test_canonical_mapping_json_parity():
    mapping = fix.read_csv(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.csv')
    assert {r['original_recipe_id']: r['canonical_recipe_id'] for r in mapping} \
        == fix.read_json(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.json')


def test_interim_data_is_unchanged(applied):
    assert fix.interim_digest(fix.ROOT) == applied['interim']


def test_write_set_never_included_interim(applied):
    assert all('interim' not in path for path in applied['write_set'])
    assert applied['write_set'] == [
        'data/processed/recipes/recipe_ingredients.csv',
        'data/processed/recipes/recipe_ingredients.json',
        'data/processed/recipes/recipes.csv',
        'data/processed/recipes/recipes.json',
        'data/processed/viendinhduong/ingredient_alias_map.json',
        'data/processed/viendinhduong/master_ingredients_nutrition.csv',
    ]


def test_plan_is_idempotent_against_the_applied_state():
    """A replanned run finds nothing left to do and still verifies the whole radius."""
    _, _, report = fix.plan(fix.ROOT)
    assert report['rows_pending'] == 0
    assert report['rows_repaired'] == fix.EXPECTED_CHANGED_ROWS == 345
    assert report['rows_written'] == fix.EXPECTED_ROWS == 355
    assert report['display_name_refreshes'] == 10
    assert report['recipes_affected'] == fix.EXPECTED_CHANGED_ROW_RECIPES == 333
    assert report['alias_map_size'] == 4684
    assert report['alias_actions'] == 20
    assert report['canonical_id_drift'] == 0
    assert report['representative_drift'] == 0
    assert report['populations'] == fix.EXPECTED_POPULATIONS
    assert report['corpus_nulls'] == fix.EXPECTED_CORPUS_NULLS
    assert report['downstream_hard_codes']['pending'] == 0
    assert report['qwen_mapper']['active'] == 29
    assert report['qwen_mapper']['disabled'] == 20
    assert report['qwen_mapper']['guarded_rule_disabled'] is True


def test_applied_report_describes_the_final_state(applied):
    assert applied['status'] == 'applied'
    assert applied['policy'] == 'DISPLAY_NAME_BATCH_C1'
    assert applied['rows_pending'] == 0
    assert applied['validation']['complete'] is True
    assert applied['validation']['catalog_name_vi_only'] is True
    assert applied['validation']['interim_unchanged'] is True
    assert (fix.OUT / 'applied_fix.md').exists()


def test_applied_report_records_the_reviewed_decisions(applied):
    text = (fix.OUT / 'applied_fix.md').read_text(encoding='utf-8')
    assert 'NO NEW ALIAS TO 4094' in text
    assert DRIED in text and 'CLEAR_TO_UNMATCHED' in text
    assert GREEN in text and SALTED in text
    assert 'KEEP_CURRENT' in applied['deferrals']['keep_current_broccoli_compound']
    assert 'NEEDS_REVIEW' in applied['deferrals']['keep_current_broccoli_compound']
    assert 'UNMATCHED' in applied['deferrals']['curated_unmatched_compound']
    assert 'lá_cải_thảo_unreviewed_rows' in applied['deferrals']
    assert 'residual_4016_qwen_rows' in applied['deferrals']
    assert 'spinach' in applied['non_reproducible'] and 'kale' in applied['non_reproducible']


# --- drift guards -------------------------------------------------------------

@pytest.mark.parametrize('field,value', [('name_en', 'Cucumber, raw'), ('energy_kcal', '999'),
                                         ('category_vi', 'other')])
def test_catalog_drift_fails_closed(monkeypatch, field, value):
    original = fix.read_csv

    def read(path):
        rows = original(path)
        if path == fix.ROOT / fix.CAT:
            next(r for r in rows if r['code'] == '4016')[field] = value
        return rows
    monkeypatch.setattr(fix, 'read_csv', read)
    monkeypatch.setattr(fix, 'write_csv', lambda *a: pytest.fail('wrote before validation'))
    with pytest.raises(fix.DriftError):
        fix.plan()


def test_alias_drift_fails_closed(monkeypatch):
    original = fix.read_json

    def read(path):
        result = original(path)
        if path == fix.ROOT / fix.ALIASES:
            result['cải bẹ xanh'] = '99999'
        return result
    monkeypatch.setattr(fix, 'read_json', read)
    with pytest.raises(fix.DriftError, match='Alias drift'):
        fix.plan()


def test_a_new_alias_on_4094_fails_closed(monkeypatch):
    original = fix.read_json

    def read(path):
        result = original(path)
        if path == fix.ROOT / fix.ALIASES:
            result['cải xanh'] = '4094'
        return result
    monkeypatch.setattr(fix, 'read_json', read)
    with pytest.raises(fix.DriftError):
        fix.plan()


def test_row_drift_fails_closed(monkeypatch, reviewed):
    original_csv, original_json = fix.read_csv, fix.read_json
    rid = reviewed['rows'][0]['before']['id']

    def read(path):
        rows = original_csv(path)
        if path.name == 'recipe_ingredients.csv':
            next(r for r in rows if r['id'] == rid)['raw_text'] = 'different ingredient'
        return rows

    def read_json(path):
        result = original_json(path)
        if path.name == 'recipe_ingredients.json':
            next(r for r in result if r['id'] == rid)['raw_text'] = 'different ingredient'
        return result
    monkeypatch.setattr(fix, 'read_csv', read)
    monkeypatch.setattr(fix, 'read_json', read_json)
    monkeypatch.setattr(fix, 'write_csv', lambda *a: pytest.fail('wrote before validation'))
    with pytest.raises(fix.DriftError, match='Row drift'):
        fix.plan()


def test_an_extra_row_on_a_reviewed_code_fails_closed(monkeypatch, reviewed):
    original_csv = fix.read_csv
    victim = reviewed['guards']['population_4094_row_ids'][0]

    def read(path):
        rows = original_csv(path)
        if path.name == 'recipe_ingredients.csv':
            next(r for r in rows if r['id'] == victim)['master_ingredient_code'] = '4016'
        return rows
    monkeypatch.setattr(fix, 'read_csv', read)
    monkeypatch.setattr(fix, 'write_csv', lambda *a: pytest.fail('wrote before validation'))
    with pytest.raises(fix.DriftError):
        fix.plan()
