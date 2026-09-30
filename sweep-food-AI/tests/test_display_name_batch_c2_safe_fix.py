"""Batch C2: the 4010 white-cabbage identity repair and the displaced celery cohort.

Strict row pins, exact alias actions, the six curated clears and the three
recoveries. Blast radius is measured against the frozen reviewed manifest and the
committed post-state -- never against `git diff`, which is only an invariant while
a batch is unstaged and inverts the moment it lands.
"""
from collections import Counter
import hashlib
import json
import unicodedata

import pytest

from nlp import entity_matcher as em
from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition
from nlp.qwen_matching import _QWEN_MAPPER_RULES, build_mapper_rules, map_clean_to_master
from scripts.eda import apply_display_name_batch_c2_safe_fix as fix
from scripts.eda import audit_qwen_matching as audit

NUTRIENTS = fix.NUTRIENTS
# The 72 celery rows, by reviewed id prefix, exactly as the reconciliation lists them.
CELERY_ROW_PREFIXES = {
    '000acff1', '00d6f4b7', '02e41a8f', '03f24d73', '0444000d', '060eee00', '084ba795', '13db877c',
    '163d626c', '1a31191b', '1dd36264', '20c11d85', '2cd6ec78', '2eb53ee3', '30a46984', '31edd31b',
    '35e6783a', '3cd6eb74', '3f0791d5', '491d2886', '499e612b', '4a5d0132', '4c402c5d', '548ae4b5',
    '58becf44', '59ba1468', '5f9439a6', '66c0e0fb', '679821aa', '6d34fd9d', '7171ba54', '744baaf9',
    '75fc5645', '7628f073', '7b90c484', '88f97847', '8a9d7879', '960be84c', '968de714', '99e49538',
    'a2c34b8d', 'a2ddcab0', 'b4eb32a9', 'b71d8f91', 'b9766fac', 'b9d820f8', 'baa1fc5b', 'bca18ad3',
    'bd39e57f', 'bdc406d2', 'c1a39314', 'c4329e9b', 'c637c0b7', 'ca02c4eb', 'd1ee5753', 'd25c177c',
    'd3f4905d', 'd6c733a4', 'dafeae6d', 'db760105', 'df921dba', 'e20e6d55', 'e3e24675', 'e41c8f78',
    'e563d2f8', 'e770bca7', 'e9a2d22c', 'ebd34df5', 'ed628548', 'f11c272f', 'fa61ded4', 'fe4cf127',
}
CLEAR_ROW_PREFIXES = {'baf69691', 'a7875aed', '58276236', '05067998', 'eb72aab4', '8a71fe23'}
KEEP_ROW_PREFIXES = {'e836ced9', 'c4ba6bd6', '5c7165f5', '6a7fda19', '87896ea2',
                     '6b7fb24a', '093aeb2d', '60cc78ac', '99d4a0bf', '50276402'}
CLEAR_RAW_TEXTS = {
    'baf69691': 'rau ngổ hoặc cần tây',
    'a7875aed': '50 g Bắp cải hoặc cải thảo luộc, vắt khô',
    '58276236': 'Chả trứng và bắp cải luộc',
    '05067998': 'Bắp cải xào lòng gà tép khô',
    'eb72aab4': 'Giá đỗ, bắp cải tim luộc',
    '8a71fe23': 'Bắp cải tím/ ngò rí 1 ít',
}
# C1's identities. None of this may move BY C2. DISPLAY_NAME_BATCH_C1 has since
# landed and repaired the ones it owned: `dưa leo` left the corrupt 4016 for the
# cucumber identity 4027, and `cải xanh` / `cải bẹ xanh` left red cabbage 4011 for
# the repaired mustard-green 4016. `dưa chuột`, `cải thảo` and `cải thìa` are
# unchanged by both batches.
C1_IDENTITIES = {'dưa leo': '4027', 'dưa chuột': '4027', 'cải xanh': '4016',
                 'cải bẹ xanh': '4016', 'cải thảo': '4109', 'cải thìa': '4135'}
# C3's, likewise.
C3_IDENTITIES = {'cải': '4013', 'cải trắng': '4021'}


def norm(value):
    return unicodedata.normalize('NFC', value or '').lower()


def prefixes(ids):
    return {rid[:8] for rid in ids}


@pytest.fixture(scope='module')
def reviewed():
    return fix.read_json(fix.REVIEW)


@pytest.fixture(scope='module')
def pins(reviewed):
    return {p['before']['id']: p for p in reviewed['rows']}


@pytest.fixture(scope='module')
def live_rows():
    csv_rows = fix.read_csv(fix.ROOT / fix.DATA / 'recipe_ingredients.csv')
    json_rows = fix.read_json(fix.ROOT / fix.DATA / 'recipe_ingredients.json')
    fix.parity(csv_rows, json_rows)
    return csv_rows


@pytest.fixture(scope='module')
def live_index(live_rows):
    return fix.index(live_rows)


@pytest.fixture(scope='module')
def live_catalog_rows():
    return fix.read_csv(fix.ROOT / fix.CAT)


@pytest.fixture(scope='module')
def live_catalog(live_catalog_rows):
    return fix.index(live_catalog_rows, 'code')


@pytest.fixture(scope='module')
def live_aliases():
    return fix.read_json(fix.ROOT / fix.ALIASES)


@pytest.fixture(scope='module')
def applied():
    return fix.read_json(fix.OUT / 'applied_fix.json')


@pytest.fixture(scope='module')
def matcher():
    return em.VietnameseIngredientMatcher()


# --- catalog ---------------------------------------------------------------

def test_catalog_rename_exact_before_and_after(live_catalog, reviewed):
    before = {r['code']: r for r in reviewed['catalog_before']}
    assert set(before) == set(fix.CATALOG_PATCHES) == {'4010'}
    assert before['4010']['name_vi'] == 'Cần tây'
    assert live_catalog['4010']['name_vi'] == 'Cải bắp trắng'
    assert fix.CATALOG_PATCHES['4010'] == {'name_vi': 'Cải bắp trắng'}


def test_every_other_catalog_column_is_byte_for_byte_unchanged(live_catalog, reviewed):
    before = reviewed['catalog_before'][0]
    live = live_catalog['4010']
    assert set(before) == set(live)
    for field in before:
        if field == 'name_vi':
            continue
        assert live[field] == before[field], field
    assert live['name_en'] == 'Cabbage, common, raw'
    assert live['category_vi'] == before['category_vi'] and live['category_en'] == before['category_en']
    for field in ('energy_kcal', 'protein_g', 'fat_g', 'carbs_g'):
        assert live[field] == before[field]


def test_sibling_catalog_rows_are_untouched(live_catalog, reviewed):
    """C2 wrote no sibling row. One of them has since been repaired by its owner.

    DISPLAY_NAME_BATCH_C1 landed after C2 and repaired 4016's `name_vi` from the
    corrupt `Dưa chuột (dưa leo)` to `Cải xanh`. The C2 manifest froze the pre-C1
    value, so the expected value here is superseded -- but only for that one field
    on that one code, which the fix module pins explicitly. Every other column of
    4016 and every other sibling row is still asserted byte-for-byte.
    """
    assert reviewed['catalog_identities']
    assert fix.C1_SUPERSEDED_CATALOG == {'4016': {'name_vi': 'Cải xanh'}}
    for code, before in reviewed['catalog_identities'].items():
        assert live_catalog[code] == dict(before, **fix.C1_SUPERSEDED_CATALOG.get(code, {})), code
    assert live_catalog['4018']['name_vi'] == 'Cần tây'
    assert live_catalog['4018']['name_en'] == 'Celery, raw'


def test_the_repaired_name_stays_distinct_from_its_siblings(live_catalog):
    """4011 is the red cultivar, 4012 the dried state. 4010 is fresh and white."""
    assert live_catalog['4011']['name_vi'] == 'Cải bắp đỏ'
    assert live_catalog['4012']['name_vi'] == 'Cải bắp trắng, khô'
    assert live_catalog['20035']['name_vi'] == 'Bắp cải tím (cải tím)'
    assert len({live_catalog[c]['name_vi'] for c in ('4010', '4011', '4012', '20035')}) == 4


def test_the_celery_display_name_collision_is_resolved(live_catalog_rows):
    assert fix.duplicate_names(live_catalog_rows) == fix.EXPECTED_DUPLICATE_NAMES_AFTER
    assert 'cần tây' not in fix.duplicate_names(live_catalog_rows)
    assert 'cần tây' in fix.EXPECTED_DUPLICATE_NAMES_BEFORE


def test_catalog_row_count_unchanged(live_catalog_rows, reviewed):
    assert len(live_catalog_rows) == reviewed['catalog_count'] == 750


# --- Qwen mapper -----------------------------------------------------------

def test_qwen_rule_counts_unchanged(live_catalog):
    active, disabled = build_mapper_rules(live_catalog)
    assert {'active': len(active), 'disabled': len(disabled)} == fix.EXPECTED_QWEN_RULE_COUNTS
    assert (len(active), len(disabled)) == (29, 20)
    assert len(active) + len(disabled) == len(_QWEN_MAPPER_RULES)


def test_the_bap_cai_rule_remains_disabled(live_catalog):
    """The whole reason `Cải bắp` was not used as the repaired display name."""
    terms, code, name = fix.QWEN_RULE_MUST_STAY_DISABLED
    assert (terms, code, name) == (('bắp cải',), '4010', 'Cải bắp')
    assert (terms, code, name) in _QWEN_MAPPER_RULES
    active, disabled = build_mapper_rules(live_catalog)
    assert not any(r[:3] == (terms, code, name) for r in active)
    assert any(r[:3] == (terms, code, name) for r in disabled)
    # Existing now, under a different name, is exactly what must NOT reactivate it.
    assert code in live_catalog and live_catalog[code]['name_vi'] != name
    assert map_clean_to_master('bắp cải', active) == (None, None)
    assert map_clean_to_master('bắp cải trắng', active) == (None, None)


def test_the_forbidden_name_is_declared_and_avoided(live_catalog):
    assert fix.FORBIDDEN_CATALOG_NAME == 'Cải bắp'
    assert live_catalog['4010']['name_vi'] != fix.FORBIDDEN_CATALOG_NAME


# --- aliases ---------------------------------------------------------------

def test_exactly_eighteen_alias_actions():
    assert len(fix.ALIAS_REPOINTS) == 10
    assert len(fix.ALIAS_REMOVALS) == 3
    assert len(fix.ALIAS_ADDITIONS) == 5
    assert (len(fix.ALIAS_REPOINTS) + len(fix.ALIAS_REMOVALS) + len(fix.ALIAS_ADDITIONS)
            == fix.EXPECTED_ALIAS_ACTIONS == 18)
    assert set(fix.ALIAS_REPOINTS).isdisjoint(fix.ALIAS_REMOVALS)
    assert set(fix.ALIAS_REPOINTS).isdisjoint(fix.ALIAS_ADDITIONS)
    assert set(fix.ALIAS_REMOVALS).isdisjoint(fix.ALIAS_ADDITIONS)
    assert set(fix.ALIAS_KEEPS).isdisjoint(
        set(fix.ALIAS_REPOINTS) | set(fix.ALIAS_REMOVALS) | set(fix.ALIAS_ADDITIONS))


def test_alias_map_size(live_aliases, reviewed):
    """C2's own arithmetic is exact; the live map has since grown by C1's 8 - 2."""
    assert reviewed['alias_map_size'] == fix.ALIAS_MAP_SIZE_BEFORE == 4672
    assert (4672 - len(fix.ALIAS_REMOVALS) + len(fix.ALIAS_ADDITIONS)
            == fix.ALIAS_MAP_SIZE_AFTER == 4674)
    assert len(live_aliases) == fix.ALIAS_MAP_SIZE_LIVE == 4684
    assert fix.ALIAS_MAP_SIZE_AFTER - 2 + 8 + 4 == fix.ALIAS_MAP_SIZE_LIVE


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_REPOINTS.items()))
def test_applied_alias_repoints(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == code
    assert reviewed['aliases_before'][alias] != code


def test_the_nine_celery_repoints_all_left_4010(reviewed):
    celery = {k: v for k, v in fix.ALIAS_REPOINTS.items() if v == '4018'}
    assert len(celery) == 9
    assert all(reviewed['aliases_before'][k] == '4010' for k in celery)
    assert all('cần' in norm(k) for k in celery)


def test_bap_cai_moves_from_red_cabbage_to_the_repaired_white_identity(live_aliases, reviewed):
    """Approved in C2, not deferred to C3."""
    assert reviewed['aliases_before']['bắp cải'] == '20035'
    assert fix.ALIAS_REPOINTS['bắp cải'] == '4010'
    assert live_aliases['bắp cải'] == '4010'


@pytest.mark.parametrize('alias', sorted(fix.ALIAS_REMOVALS))
def test_removed_aliases_are_gone(live_aliases, reviewed, alias):
    assert alias not in live_aliases
    assert reviewed['aliases_before'][alias] == '4010'


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_ADDITIONS.items()))
def test_added_aliases_exist_and_were_absent_before(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == code == '4010'
    assert alias in reviewed['aliases_absent_before']


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_KEEPS.items()))
def test_reviewed_alias_keeps(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == code
    assert reviewed['aliases_before'][alias] == code


def test_only_the_reviewed_aliases_moved(live_aliases, reviewed):
    moved = {k for k, before in reviewed['aliases_before'].items() if live_aliases.get(k) != before}
    assert moved == set(fix.ALIAS_REPOINTS) | set(fix.ALIAS_REMOVALS)
    added = {k for k in fix.ALIAS_ADDITIONS if k in live_aliases}
    assert added == set(fix.ALIAS_ADDITIONS)
    assert (set(live_aliases) - set(reviewed['aliases_before'])) >= set(fix.ALIAS_ADDITIONS)


def test_every_alias_on_the_repaired_identity_is_reviewed(live_aliases):
    on_4010 = {k for k, v in live_aliases.items() if v == '4010'}
    reviewed_on_4010 = ({k for k, v in fix.ALIAS_REPOINTS.items() if v == '4010'}
                        | {k for k, v in fix.ALIAS_ADDITIONS.items() if v == '4010'}
                        | {k for k, v in fix.ALIAS_KEEPS.items() if v == '4010'})
    assert on_4010 == reviewed_on_4010 | {'cải bào', 'cải bào mỏng', 'cải trắng bào',
                                          'cải trắng xắt sợi', 'bắp cải tròn', 'lá bắp cải',
                                          'rau bắp cải', 'bắp cải tim'}
    assert not any('cần' in norm(k) for k in on_4010), 'a celery phrase still reaches 4010'
    assert not any('tím' in norm(k) for k in on_4010), 'a red-cabbage phrase reaches 4010'


def test_every_alias_on_celery_names_celery(live_aliases):
    assert all('cần' in norm(k) for k, v in live_aliases.items() if v == '4018')


def test_red_cabbage_keeps_every_purple_alias(live_aliases, reviewed):
    red = {k for k, v in live_aliases.items() if v == '20035'}
    assert red == {k for k, v in reviewed['aliases_before'].items() if v == '20035'} - {'bắp cải'}
    assert all('tím' in norm(k) for k in red)


@pytest.mark.parametrize('alias,code', sorted(C3_IDENTITIES.items()))
def test_c3_aliases_are_untouched(live_aliases, reviewed, alias, code):
    assert live_aliases[alias] == reviewed['aliases_before'][alias] == code


# --- reviewed synonym ------------------------------------------------------

def test_reviewed_synonym_evidence_is_recorded(reviewed, live_index):
    synonym = reviewed['reviewed_synonym']
    assert synonym['terms'] == ['cần tàu', 'cần tây']
    assert synonym['target_code'] == '4018'
    assert synonym['inferred_from_alias_map'] is False
    assert synonym['evidence_raw_text'] == '1 ít rau cần tây (hay cần tàu)'
    # The evidence is a real live row, and it really says both terms.
    row = live_index[synonym['evidence_row_id']]
    assert row['raw_text'] == synonym['evidence_raw_text']
    assert row['recipe_id'] == synonym['evidence_recipe_id']
    assert all(norm(term) in norm(row['raw_text']) for term in synonym['terms'])
    assert row['master_ingredient_code'] == '4018'


def test_reviewed_synonym_is_not_inferred_from_the_alias_map(applied):
    assert applied['reviewed_synonym']['inferred_from_alias_map'] is False
    assert 'hay' in applied['reviewed_synonym']['evidence_raw_text']


# --- reviewed rows ---------------------------------------------------------

def test_reviewed_manifest_shape(reviewed, pins):
    assert len(reviewed['rows']) == len(pins) == fix.EXPECTED_ROWS == 92
    assert Counter(p['cohort'] for p in reviewed['rows']) == {
        'celery_4010_to_4018': 71,
        'celery_compound_subphrase_4010_to_4018': 1,
        'ambiguous_clear_to_unmatched': 6,
        'white_cabbage_keep_4010': 10,
        'red_cabbage_4010_to_20035': 1,
        'white_cabbage_20035_to_4010': 1,
        'white_cabbage_unmatched_recovery': 2,
    }
    assert {c: v[2] for c, v in fix.COHORTS.items()} == dict(
        Counter(p['cohort'] for p in reviewed['rows']))


def test_the_exact_seventy_two_celery_ids(pins, live_index):
    celery = {rid for rid, p in pins.items() if p['cohort'].startswith('celery_')}
    assert len(celery) == 72
    assert prefixes(celery) == CELERY_ROW_PREFIXES
    for rid in celery:
        assert pins[rid]['before']['master_ingredient_code'] == '4010'
        assert live_index[rid]['master_ingredient_code'] == '4018'
        assert live_index[rid]['master_ingredient_name'] == 'Cần tây'


def test_the_seventy_one_core_celery_rows_preserve_their_provenance(pins, live_index):
    core = {rid for rid, p in pins.items() if p['cohort'] == 'celery_4010_to_4018'}
    assert len(core) == 71
    for rid in core:
        assert pins[rid]['before']['match_method'] == 'PRESET_ALIAS_MATCH'
        assert pins[rid]['before']['match_confidence'] == '0.98'
        assert live_index[rid]['match_method'] == 'PRESET_ALIAS_MATCH'
        assert live_index[rid]['match_confidence'] == '0.98'


def test_the_compound_row_provenance_becomes_subphrase(pins, live_index):
    """3f0791d5 lost the alias that claimed it, so its 0.98 is not preserved."""
    rid = fix.SUBPHRASE_ROW_ID
    row = live_index[rid]
    assert pins[rid]['before']['raw_text'] == fix.SUBPHRASE_RAW_TEXT == '1 trái bắp mĩ, 1 cây cần tây'
    assert pins[rid]['before']['cleaned_name'] == 'mĩ 1 cây cần tây'
    assert pins[rid]['before']['match_confidence'] == '0.98'
    assert row['master_ingredient_code'] == '4018'
    assert row['match_method'] == 'SUBPHRASE_CATALOG_MATCH'
    assert row['match_confidence'] == '0.95'
    assert row['match_confidence'] != pins[rid]['before']['match_confidence']


def test_the_exact_ten_keep_ids(pins, live_index, reviewed):
    reviewed_4010_name_before = reviewed['catalog_before'][0]['name_vi']
    keeps = {rid for rid, p in pins.items() if p['cohort'] == 'white_cabbage_keep_4010'}
    assert len(keeps) == 10
    assert prefixes(keeps) == KEEP_ROW_PREFIXES
    for rid in keeps:
        before, row = pins[rid]['before'], live_index[rid]
        assert before['master_ingredient_code'] == row['master_ingredient_code'] == '4010'
        assert row['master_ingredient_name'] == 'Cải bắp trắng'
        # Before C2 these rows carried `Cải bắp` -- a stale stored name written when
        # the Qwen rule was still active, which disagreed with the catalog's own
        # `Cần tây`. The refresh makes the stored name agree with the catalog again.
        assert before['master_ingredient_name'] == 'Cải bắp'
        assert before['master_ingredient_name'] != reviewed_4010_name_before
        # Existing QWEN_LLM_MATCH / 0.98 metadata is preserved, not recomputed.
        assert before['match_method'] == row['match_method'] == 'QWEN_LLM_MATCH'
        assert before['match_confidence'] == row['match_confidence'] == '0.98'
        # Nutrition delta must be zero: the code did not move.
        for field in NUTRIENTS:
            assert row[field] == before[field], f'{rid}.{field}'


def test_red_cabbage_row_moves_to_20035(pins, live_index, live_catalog):
    rid = fix.RED_CABBAGE_ROW_ID
    row = live_index[rid]
    assert pins[rid]['before']['raw_text'] == fix.RED_CABBAGE_RAW_TEXT == 'Bắp cải tím 8 lá'
    assert pins[rid]['before']['master_ingredient_code'] == '4010'
    assert row['master_ingredient_code'] == '20035'
    assert row['master_ingredient_name'] == live_catalog['20035']['name_vi']
    assert row['match_method'] == pins[rid]['before']['match_method'] == 'QWEN_LLM_MATCH'
    # Nutrition comes from the authoritative target row, not carried forward.
    for field, column in NUTRITION_FIELDS.items():
        want = scale_nutrition(live_catalog['20035'][column], float(row['estimated_weight_g']) / 100.0, 1)
        assert float(row[field]) == want


def test_bare_bap_cai_row_is_recovered_from_red_cabbage(pins, live_index):
    rid = 'cbd724fa-0418-42c8-8f41-0d7f42d36a77'
    row = live_index[rid]
    assert pins[rid]['before']['master_ingredient_code'] == '20035'
    assert pins[rid]['before']['raw_text'] == 'Ít bắp cải'
    assert 'tím' not in norm(row['raw_text']) and 'đỏ' not in norm(row['raw_text'])
    assert row['master_ingredient_code'] == '4010'
    assert row['master_ingredient_name'] == 'Cải bắp trắng'
    assert row['match_method'] == 'PRESET_ALIAS_MATCH'
    assert row['match_confidence'] == '0.98'


@pytest.mark.parametrize('rid', ['0388cb60-cef5-4127-846f-9c2bfe4e929c',
                                 'a8e5fc9c-b796-4b6b-a911-5e7434fadd51'])
def test_unmatched_white_cabbage_recoveries(pins, live_index, rid):
    before, row = pins[rid]['before'], live_index[rid]
    assert before['match_method'] == 'UNMATCHED'
    assert not (before['master_ingredient_code'] or '').strip()
    assert all(before[f] in (None, '') for f in NUTRIENTS)
    assert row['master_ingredient_code'] == '4010'
    assert row['master_ingredient_name'] == 'Cải bắp trắng'
    assert row['match_method'] == 'PRESET_ALIAS_MATCH'
    assert row['match_confidence'] == '0.98'


def test_recovered_rows_store_a_real_scaled_zero_fat_not_a_null(live_index, live_catalog):
    """0.09 g/100 g scaled to 30 g and 50 g rounds to 0.0 at the project's decimal."""
    assert float(live_catalog['4010']['fat_g']) == 0.09
    for rid in ('0388cb60-cef5-4127-846f-9c2bfe4e929c', 'a8e5fc9c-b796-4b6b-a911-5e7434fadd51'):
        row = live_index[rid]
        assert row['fat_g'] == fix.EXPECTED_RECOVERY_FAT == '0.0'
        assert row['fat_g'] not in (None, '')
        assert float(row['fat_g']) == scale_nutrition(
            live_catalog['4010']['fat_g'], float(row['estimated_weight_g']) / 100.0, 1)


def test_reviewed_rows_preserve_raw_and_parsed_evidence(reviewed, live_index):
    immutable = ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                 'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g')
    for pin in reviewed['rows']:
        before, row = pin['before'], live_index[pin['before']['id']]
        for field in immutable:
            assert row[field] == before[field], f"{before['id']}.{field}"


def test_cohorts_are_semantic_not_code_selections(reviewed, pins):
    """Each cohort is stated over its own cleaned names, so no row rides a code."""
    celery = {rid for rid, p in pins.items() if p['cohort'].startswith('celery_')}
    assert {pins[rid]['before']['cleaned_name'] for rid in celery} == {
        'cần tàu', 'rau nêm cần tàu', 'rau cần tây', 'cần tây bẹ', 'cần tây bào vỏ',
        'cần tây bẹ cắt lát xéo', 'cần tây tước xơ cắt lát', 'lá cần tây non', 'mĩ 1 cây cần tây'}
    keeps = {rid for rid, p in pins.items() if p['cohort'] == 'white_cabbage_keep_4010'}
    assert {pins[rid]['before']['cleaned_name'] for rid in keeps} == {
        'bắp cải', 'bắp cải nhỏ', 'bắp cải trắng', 'bắp cải trái tim', 'bắp cải trộn'}


def test_nutrition_recomputed_from_the_target_catalog(reviewed, live_index, live_catalog):
    for pin in reviewed['rows']:
        row = live_index[pin['before']['id']]
        if pin['target_code'] is None:
            continue
        target = live_catalog[pin['target_code']]
        weight = float(row['estimated_weight_g'])
        for field, column in NUTRITION_FIELDS.items():
            want = scale_nutrition(target[column], weight / 100.0, 1)
            if want is None:
                assert row[field] in (None, ''), f"{row['id']}.{field}"
            else:
                assert float(row[field]) == want, f"{row['id']}.{field}"


# --- the six curated clears -------------------------------------------------

def test_the_exact_six_clear_ids(pins):
    cleared = {rid for rid, p in pins.items() if p['target_code'] is None}
    assert len(cleared) == 6
    assert prefixes(cleared) == CLEAR_ROW_PREFIXES
    assert {rid[:8]: pins[rid]['before']['raw_text'] for rid in cleared} == CLEAR_RAW_TEXTS


def test_cleared_rows_carry_the_full_unmatched_contract(pins, live_index):
    for rid, pin in pins.items():
        if pin['target_code'] is not None:
            continue
        row = live_index[rid]
        assert row['match_method'] == 'UNMATCHED'
        assert not (row['master_ingredient_code'] or '').strip()
        assert not (row['master_ingredient_name'] or '').strip()
        assert row['match_confidence'] in (None, '')
        # 0.0 is the explicit-rejection sentinel and must not appear here.
        assert row['match_confidence'] != '0.0'
        assert all(row[f] in (None, '') for f in NUTRIENTS)


def test_cleared_rows_keep_their_parsed_evidence(pins, live_index):
    for rid, pin in pins.items():
        if pin['target_code'] is not None:
            continue
        before, row = pin['before'], live_index[rid]
        for field in ('raw_text', 'cleaned_name', 'required_quantity', 'unit_vi',
                      'unit', 'preparation_note', 'estimated_weight_g'):
            assert row[field] == before[field], f'{rid}.{field}'
        assert row['estimated_weight_g'] not in (None, '')


def test_the_clears_are_recorded_as_intentionally_non_reproducible(applied):
    """Two of the six ARE claimable by the new alias map. That is recorded, not patched."""
    recorded = applied['non_reproducible_clears']
    assert set(recorded) == {'rau ngổ hoặc cần tây', 'bắp cải'}
    assert all(v['stored'] == 'UNMATCHED' for v in recorded.values())
    assert recorded['bắp cải']['matcher_would_reach'] == '4010'
    assert recorded['rau ngổ hoặc cần tây']['matcher_would_reach'] == '4018'


def test_no_broad_guard_was_added_to_reproduce_the_clears():
    """The clears are curated data, not a matcher rule: the matcher gained nothing."""
    source = (fix.ROOT / 'nlp/entity_matcher.py').read_text(encoding='utf-8')
    assert 'bắp cải' not in source
    assert 'cần tàu' not in source


# --- populations, nutrition, nulls -----------------------------------------

def test_final_populations(live_rows):
    populations = {code: sum(1 for r in live_rows if (r['master_ingredient_code'] or '') == code)
                   for code in fix.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
    assert populations == fix.EXPECTED_POPULATIONS
    # C2's own result was 4010: 13, 4011: 41, UNMATCHED: 8469. DISPLAY_NAME_BATCH_C1
    # has since moved one green-head-cabbage row onto 4010, emptied 4011 onto the
    # repaired mustard-green identity, and cleared 35 rows while recovering 5.
    assert populations['4010'] == 105
    assert populations['4018'] == 177
    assert populations['20035'] == 33
    assert populations['4011'] == 0
    assert populations['4012'] == 5
    assert populations['UNMATCHED'] == 8495


def test_the_thirteen_rows_on_4010_are_exactly_the_reviewed_ones(live_rows, pins):
    """C2 put exactly 13 rows here. C1 later added exactly one more, by id.

    633ea6e1 `Bắp cải xanh 1/2 cái` is green HEAD cabbage; the corrupt alias map had
    it on red cabbage 4011, and DISPLAY_NAME_BATCH_C1 moved it onto C2's repaired
    white-cabbage identity. C2's own 13 are still asserted exactly.
    """
    on_4010 = {r['id'] for r in live_rows if r['master_ingredient_code'] == '4010'}
    expected = ({rid for rid, p in pins.items() if p['cohort'] == 'white_cabbage_keep_4010'}
                | {rid for rid, p in pins.items()
                   if p['cohort'] in ('white_cabbage_20035_to_4010', 'white_cabbage_unmatched_recovery')})
    assert len(expected) == 13
    c3_ids = {p['before']['id'] for p in json.load(open('scripts/eda/display_name_batch_c3_reviewed_state.json', encoding='utf-8'))['rows']}
    assert on_4010 - c3_ids == expected | {fix.C1_ROW_ADDED_TO_4010}
    assert len(on_4010) == 105


def test_combined_nutrition_delta(reviewed, live_index):
    ordered = sorted(reviewed['rows'], key=lambda p: p['before']['id'])
    report = fix.nutrient_report([p['before'] for p in ordered],
                                 [live_index[p['before']['id']] for p in ordered])
    assert {f: report[f]['known_sum_delta'] for f in NUTRIENTS} == fix.EXPECTED_NUTRITION_DELTA
    assert {f: report[f]['known_sum_delta'] for f in NUTRIENTS} == {
        'calories': '1184.6', 'protein_g': '135.8', 'fat_g': '6.3', 'carbs_g': '173.5'}


def test_cohort_nutrition_deltas(reviewed, live_index):
    for cohort, expected in fix.EXPECTED_COHORT_NUTRITION_DELTA.items():
        ordered = sorted((p for p in reviewed['rows'] if p['cohort'] == cohort),
                         key=lambda p: p['before']['id'])
        report = fix.nutrient_report([p['before'] for p in ordered],
                                     [live_index[p['before']['id']] for p in ordered])
        assert {f: report[f]['known_sum_delta'] for f in NUTRIENTS} == expected, cohort


def test_null_transitions_are_the_six_clears_and_the_two_recoveries(reviewed, live_index):
    ordered = sorted(reviewed['rows'], key=lambda p: p['before']['id'])
    report = fix.nutrient_report([p['before'] for p in ordered],
                                 [live_index[p['before']['id']] for p in ordered])
    assert {f: (report[f]['before_null_count'], report[f]['after_null_count'])
            for f in NUTRIENTS} == fix.EXPECTED_NULL_TRANSITIONS
    assert {f: report[f]['value_to_null'] for f in NUTRIENTS} == fix.EXPECTED_VALUE_TO_NULL
    assert {f: report[f]['null_to_value'] for f in NUTRIENTS} == fix.EXPECTED_NULL_TO_VALUE


def test_corpus_null_counts(live_rows):
    """Superseded by DISPLAY_NAME_BATCH_C1: net +30, plus a further +9 on fat_g."""
    assert {f: sum(1 for r in live_rows if r[f] in (None, ''))
            for f in NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS
    assert fix.EXPECTED_CORPUS_NULLS == {
        'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454}


def test_no_missing_nutrition_was_zero_filled(live_rows):
    """A blank stays blank; the only stored zeros are scaled numeric zeros."""
    unmatched = [r for r in live_rows if r['match_method'] == 'UNMATCHED']
    assert len(unmatched) == 8495
    assert all(all(r[f] in (None, '') for f in NUTRIENTS) for r in unmatched)


def test_no_row_outside_the_reviewed_92_changed(reviewed, live_rows, live_catalog, pins):
    """Blast radius, measured against the manifest rather than against git.

    Every pinned row must equal the reviewed transform of its own before record,
    and the corpus shape the batch published -- row count, per-code populations
    and per-nutrient null counts -- is pinned exactly, so a row moving in or out
    of any reviewed identity fails here. No assertion in this module consults
    version control; a working-tree-vs-HEAD diff only holds while a batch is
    unstaged and inverts the moment it lands.
    """
    live = fix.index(live_rows)
    for rid, pin in pins.items():
        assert fix.logical(live[rid]) == fix.logical(fix.expected_row(pin, live_catalog)), rid
    assert len(live_rows) == 63943
    populations = {code: sum(1 for r in live_rows if (r['master_ingredient_code'] or '') == code)
                   for code in fix.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
    assert populations == fix.EXPECTED_POPULATIONS
    assert {f: sum(1 for r in live_rows if r[f] in (None, ''))
            for f in NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS


# --- guards: siblings, C1 and C3 -------------------------------------------

def test_the_105_pre_existing_celery_rows_are_untouched(reviewed, live_rows, live_index):
    kept = set(reviewed['guards']['celery_4018_row_ids'])
    assert len(kept) == 105
    moved = {p['before']['id'] for p in reviewed['rows'] if p['target_code'] == '4018'}
    assert kept.isdisjoint(moved) and len(moved) == 72
    assert {r['id'] for r in live_rows if r['master_ingredient_code'] == '4018'} == kept | moved
    for rid in kept:
        assert live_index[rid]['master_ingredient_name'] == 'Cần tây'


def test_red_cabbage_population_is_the_reviewed_keeps_plus_the_reviewed_move(reviewed, live_rows, live_index):
    kept = set(reviewed['guards']['red_cabbage_20035_row_ids'])
    assert len(kept) == 32
    assert ({r['id'] for r in live_rows if r['master_ingredient_code'] == '20035'}
            == kept | {fix.RED_CABBAGE_ROW_ID})
    assert all('tím' in norm(live_index[rid]['raw_text']) for rid in kept)


@pytest.mark.parametrize('key,code,count', [('red_cabbage_4011_row_ids', '4011', 41),
                                            ('dried_cabbage_4012_row_ids', '4012', 5)])
def test_sibling_populations_unchanged(reviewed, live_rows, key, code, count):
    """C2 moved no sibling row. C1 later emptied 4011, which it owned.

    All 41 rows C2 pinned on red cabbage 4011 were mis-homed: 40 were genuine
    mustard greens and went to the repaired 4016, and the 41st was green head
    cabbage and went to 4010. The frozen 41-row set is still asserted as C2's
    reviewed keep; the live population it maps to is now empty.
    """
    pinned = set(reviewed['guards'][key])
    assert len(pinned) == count
    live = {r['id'] for r in live_rows if r['master_ingredient_code'] == code}
    assert live == (set() if code in fix.C1_EMPTIED_SIBLING_CODES else pinned)


@pytest.mark.parametrize('key,code', [('cai_4013', '4013'), ('cai_trang_4021', '4021')])
def test_deferred_c3_populations_unchanged(reviewed, live_rows, key, code):
    pinned = set(reviewed['guards']['deferred_c3_row_ids'][key])
    c3_ids = {p['before']['id'] for p in json.load(open('scripts/eda/display_name_batch_c3_reviewed_state.json', encoding='utf-8'))['rows']}
    assert {r['id'] for r in live_rows if r['master_ingredient_code'] == code} == pinned - c3_ids


def test_c1_identity_populations_unchanged(reviewed, live_rows):
    """C2 moved none of C1's rows; C1 has since landed and re-homed its own.

    The frozen figures (4015: 19, 4016: 301, 4109: 65, 4135: 59) were C2's
    out-of-scope pin. DISPLAY_NAME_BATCH_C1 owned those identities and repaired
    them, so the live values are the superseded ones the fix module pins. 4135 is
    unchanged in both, which is the point: C1 did not touch the bok-choy duplicate.
    """
    expected = dict(reviewed['guards']['c1_identity_row_counts'],
                    **fix.C1_SUPERSEDED_IDENTITY_ROW_COUNTS)
    assert expected == {'4015': 11, '4016': 60, '4109': 73, '4135': 59}
    assert {code: sum(1 for r in live_rows if r['master_ingredient_code'] == code)
            for code in expected} == expected


def test_c1_audit_evidence_is_not_changed_by_c2():
    """4016's WRONG signature belongs to C1, which has since re-keyed it.

    C2 left the entry alone; DISPLAY_NAME_BATCH_C1 repaired 4016 and re-keyed the
    signature onto the repaired display name, narrowing the synonym list to the ten
    reviewed rows that survive on the code. `cải thảo` deliberately left the list --
    those rows are gone.
    """
    assert audit.WRONG['4016'][0] == 'Cải xanh'
    assert audit.WRONG['4016'][1] == 'cải con|cải thìa|cải thìa con'
    assert 'cải thảo' not in audit.WRONG['4016'][1]


# --- downstream hard-coded cabbage codes ------------------------------------

@pytest.mark.parametrize('path,count', sorted(fix.DOWNSTREAM_FILES.items(), key=lambda kv: str(kv[0])))
def test_downstream_cabbage_hard_codes_point_at_4010(path, count):
    text = (fix.ROOT / path).read_text(encoding='utf-8')
    assert text.count(fix.DOWNSTREAM_AFTER) == count
    assert fix.DOWNSTREAM_BEFORE not in text


def test_exactly_five_downstream_repoints_and_no_stragglers():
    found = {}
    for path in sorted((fix.ROOT / fix.DOWNSTREAM_SCAN_ROOT).rglob('*.py')):
        for code in fix.DOWNSTREAM_SCAN.findall(path.read_text(encoding='utf-8')):
            found.setdefault(code, []).append(path.name)
    assert set(found) == {'4010'}
    assert sum(len(v) for v in found.values()) == fix.EXPECTED_DOWNSTREAM_REPOINTS == 5
    assert sum(len(v) for v in found.values()) == sum(fix.DOWNSTREAM_FILES.values())


def test_the_c1_cucumber_hard_code_is_untouched():
    """C2 never wrote the cucumber pantry entry; C1 owned it and has repaired it.

    C2 asserted the line was still `("dưa chuột", "4016", ...)`. DISPLAY_NAME_BATCH_C1
    has since repointed it onto the cucumber identity 4027, so that is the value C2
    must now find unchanged. The assertion is kept, not deleted.
    """
    text = (fix.ROOT / 'src/recommendation/pantry_simulator.py').read_text(encoding='utf-8')
    assert fix.DOWNSTREAM_OUT_OF_SCOPE == '("dưa chuột", "4027"'
    assert fix.DOWNSTREAM_OUT_OF_SCOPE in text
    assert '("dưa chuột", "4016"' not in text


def test_the_repointed_code_is_the_fresh_identity(live_catalog):
    """4012 is dried cabbage at 301 kcal/100 g; a pantry head of cabbage is 4010."""
    assert live_catalog['4012']['name_en'] == 'Cabbage, dried'
    assert float(live_catalog['4012']['energy_kcal']) > float(live_catalog['4010']['energy_kcal']) * 5
    assert live_catalog['4010']['name_en'] == 'Cabbage, common, raw'


# --- audit evidence hygiene -------------------------------------------------

def test_the_stale_4010_wrong_signature_is_retired():
    assert '4010' not in audit.WRONG


def test_the_repaired_4010_carries_the_narrow_valid_evidence():
    assert audit.VALID['4010'] == (fix.AUDIT_VALID_NAME, fix.AUDIT_VALID_SYNONYMS)
    name, synonyms = audit.VALID['4010']
    assert name == 'Cải bắp trắng'
    assert synonyms.split('|') == ['bắp cải', 'bắp cải trắng', 'bắp cải nhỏ',
                                   'bắp cải trái tim', 'bắp cải trộn']
    # Narrow, not a generic cabbage pattern: no red-cabbage spelling is claimed.
    assert 'tím' not in synonyms and 'tim' not in synonyms.replace('trái tim', '')
    assert '*' not in synonyms and '.' not in synonyms


def test_audit_classifies_only_the_measured_row_as_an_upgrade():
    masters = {r['code']: r for r in audit.read_csv(audit.MASTER)}
    rows = {r['id']: r for r in audit.read_csv(audit.ING) if r['match_method'] == 'QWEN_LLM_MATCH'}
    on_4010 = {rid: r for rid, r in rows.items() if r['master_ingredient_code'] == '4010'}
    assert len(on_4010) == 10
    classes = {rid: audit.classify(r, masters)[0] for rid, r in on_4010.items()}
    upgraded = {rid for rid, c in classes.items() if c == 'C'}
    assert upgraded == set(fix.EXPECTED_AUDIT_UPGRADES)
    assert all(classes[rid] == 'B' for rid in on_4010 if rid not in upgraded)
    # The cleared rows left the QWEN population entirely.
    assert not (prefixes(rows) & CLEAR_ROW_PREFIXES - {'baf69691'})


def test_audit_evidence_change_does_not_touch_production_matching():
    """Hygiene only: the audit module is read-only diagnosis, never imported by nlp."""
    for module in ('nlp/entity_matcher.py', 'nlp/qwen_matching.py', 'nlp/pipeline.py'):
        assert 'audit_qwen_matching' not in (fix.ROOT / module).read_text(encoding='utf-8')


# --- matcher probes ---------------------------------------------------------

@pytest.mark.parametrize('query,code', sorted(fix.PROBES.items()))
def test_matcher_reaches_the_reviewed_identity_on_both_routes(matcher, query, code):
    single = matcher.match(query, raw_context=query)
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    assert (single['matched_item'] or {}).get('code') == code
    assert (batched['matched_item'] or {}).get('code') == code
    assert single['method'] == batched['method']


@pytest.mark.parametrize('query,code', sorted(C1_IDENTITIES.items()))
def test_c1_identities_are_untouched(matcher, query, code):
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    assert (batched['matched_item'] or {}).get('code') == code


@pytest.mark.parametrize('query,code', sorted(C3_IDENTITIES.items()))
def test_c3_identities_are_untouched(matcher, query, code):
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    assert (batched['matched_item'] or {}).get('code') == code


def test_the_recovery_verdicts_are_reproducible(matcher):
    for query in ('bắp cải', 'bắp cải trái tim'):
        for result in (matcher.match(query, raw_context=query),
                       matcher.match_batch([query], raw_contexts=[query])[0]):
            assert (result['matched_item'] or {}).get('code') == '4010'
            assert result['method'] == 'PRESET_ALIAS_MATCH'
            assert result['confidence'] == 0.98


def test_the_compound_celery_verdict_is_reproducible(matcher):
    query = 'mĩ 1 cây cần tây'
    for result in (matcher.match(query, raw_context=fix.SUBPHRASE_RAW_TEXT),
                   matcher.match_batch([query], raw_contexts=[fix.SUBPHRASE_RAW_TEXT])[0]):
        assert (result['matched_item'] or {}).get('code') == '4018'
        assert result['method'] == 'SUBPHRASE_CATALOG_MATCH'
        assert result['confidence'] == 0.95


def test_the_known_divergence_moves_no_live_row(matcher, live_rows):
    """Removing `tây` splits the two routes on a fragment nothing uses."""
    pinned = fix.KNOWN_ROUTE_DIVERGENCE['tây']
    single = matcher.match('tây', raw_context='tây')
    batched = matcher.match_batch(['tây'], raw_contexts=['tây'])[0]
    assert (single['matched_item'] or {}).get('code') == pinned['single_after']
    assert (batched['matched_item'] or {}).get('code') == pinned['batch_after']
    assert pinned['live_rows'] == 0
    assert not [r for r in live_rows if norm(r['cleaned_name']) == 'tây']


def test_production_shape_replay_reproduces_every_non_curated_row(reviewed, live_index, matcher):
    """match_batch(cleaned_name, raw_contexts=raw_text) re-derives the stored state.

    The six curated clears are excluded by name: they are reviewed data decisions
    that the matcher is deliberately NOT taught to make.
    """
    pins = sorted((p for p in reviewed['rows'] if p['target_code'] is not None),
                  key=lambda p: p['before']['id'])
    assert len(pins) == 86
    names = [p['before']['cleaned_name'] for p in pins]
    contexts = [p['before']['raw_text'] for p in pins]
    for pin, result in zip(pins, matcher.match_batch(names, raw_contexts=contexts)):
        rid = pin['before']['id']
        if pin['cohort'] == 'white_cabbage_keep_4010':
            # QWEN-sourced rows: the matcher need only agree on the identity.
            assert (result['matched_item'] or {}).get('code') == '4010', rid
            continue
        assert (result['matched_item'] or {}).get('code') == pin['target_code'], rid
        assert live_index[rid]['master_ingredient_code'] == pin['target_code']


# --- rollups, canonical, embeddings, idempotence ----------------------------

def test_recipe_rollups_agree_with_the_repaired_rows(live_rows):
    recipes = fix.read_csv(fix.ROOT / fix.DATA / 'recipes.csv')
    recipes_json = fix.read_json(fix.ROOT / fix.DATA / 'recipes.json')
    fix.parity(recipes, recipes_json)
    rollups = fix.recompute_recipe_rollups(live_rows)
    for record in recipes:
        if record['id'] in rollups:
            for key, value in fix._new_totals(rollups[record['id']]).items():
                assert record[key] == value, f"{record['id']}.{key}"


def test_recipe_missing_counts_and_zero_status_transitions(applied):
    status = applied['recipe_status']
    assert status['status_transitions'] == fix.EXPECTED_STATUS_LABEL_TRANSITIONS == {}
    assert status['recipes_with_status_label_changed'] == 0
    assert {rid: (v['before'], v['after']) for rid, v in status['missing_count_transitions'].items()} \
        == fix.EXPECTED_MISSING_COUNT_TRANSITIONS
    clears = {'1022eb07-c5b1-4fac-abec-6de502e4289a', '2b3ed220-c1c1-44fa-838e-3844ddb1b611',
              '86aa60e9-62eb-45c9-ac47-33a73a9d7d54', 'd5ba12dc-cccb-4621-b71c-f8ede7bceb40',
              'fd85d160-cd83-4f76-80a3-0e12b1fb2757'}
    recoveries = {'2b0fe656-9cd9-46d2-b5ca-90659d0a79b2', 'ae835445-9dec-4a32-b417-ad0f653904ea'}
    for rid, (before, after) in fix.EXPECTED_MISSING_COUNT_TRANSITIONS.items():
        assert after > before if rid in clears else after < before
    assert set(fix.EXPECTED_MISSING_COUNT_TRANSITIONS) == clears | recoveries


def test_recipe_status_labels_were_not_forced(live_rows):
    """Recompute the project's own rule and require the stored labels to agree."""
    recipes_json = fix.read_json(fix.ROOT / fix.DATA / 'recipes.json')
    computed = fix.nutrition_status(live_rows, recipes_json)
    for record in recipes_json:
        label, missing = computed[record['id']]
        assert record['nutrition_status'] == label, record['id']
        assert int(record['missing_nutrition_count']) == missing, record['id']


def test_canonical_parity_and_identity():
    for name in ('canonical_recipes', 'canonical_recipe_ingredients'):
        fix.parity(fix.read_csv(fix.ROOT / fix.DATA / (name + '.csv')),
                   fix.read_json(fix.ROOT / fix.DATA / (name + '.json')))
    mapping = fix.read_csv(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.csv')
    assert ({r['original_recipe_id']: r['canonical_recipe_id'] for r in mapping}
            == fix.read_json(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.json'))


def test_canonical_totals_and_zero_drift(applied):
    assert applied['canonical_id_drift'] == 0
    assert applied['representative_drift'] == 0
    assert {name: values['changed_count'] for name, values in applied['canonical'].items()} \
        == fix.EXPECTED_CANONICAL
    assert applied['canonical']['recipe_canonical_mapping.csv']['canonical_groups_involved'] \
        == fix.EXPECTED_CANONICAL_GROUPS == 91
    assert applied['canonical']['canonical_recipe_ingredients.csv']['reviewed_rows_absent'] == 0
    assert len(fix.read_csv(fix.ROOT / fix.DATA / 'canonical_recipes.csv')) \
        == fix.EXPECTED_CANONICAL_TOTALS['canonical_recipes.csv'] == 5479
    assert len(fix.read_csv(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.csv')) \
        == fix.EXPECTED_CANONICAL_TOTALS['recipe_canonical_mapping.csv'] == 5641


def test_the_review_estimate_divergence_is_recorded(applied):
    """The brief quoted 91 canonical recipes changed; 91 are touched, 81 change."""
    estimate = applied['review_estimate_canonical']
    assert estimate['estimate']['canonical_recipes_changed'] == 91
    assert estimate['measured']['canonical_recipe_groups_touched'] == 91
    assert estimate['measured']['canonical_recipes_csv_rows_changed'] == 81
    assert applied['canonical']['canonical_recipes.csv']['recipes_touched_without_content_change'] == 10


def test_embeddings_were_rebuilt_and_reload_equal(applied):
    """C2 rebuilt the cache; C1 changed catalog text again and rebuilt it after.

    The digests C2 recorded describe the cache as C2 left it. DISPLAY_NAME_BATCH_C1
    repaired 4016's `name_vi`, which is part of the embedding input text, so the live
    cache is now C1's and is asserted against C1's applied report. Both halves stay
    fail-closed: C2's record must still describe a 750x768 rebuild from the repaired
    4010 text, and the live cache must match the digest of whichever landed batch
    built it.
    """
    torch = pytest.importorskip('torch')
    cache = (fix.ROOT / fix.CAT).with_name('catalog_embeddings_bkai.pt')
    assert cache.exists()
    assert applied['embeddings']['rebuilt'] is True
    assert applied['embeddings']['shape'] == [750, 768]
    assert applied['embeddings']['build_inputs']['4010'].startswith('Cải bắp trắng (')
    assert applied['embeddings']['tracked'] is False
    tensor = torch.load(cache, map_location='cpu', weights_only=True)
    assert list(tensor.shape) == [750, 768]
    current = fix.read_json(fix.C1_EMBEDDING_REPORT)['embeddings']
    assert hashlib.sha256(cache.read_bytes()).hexdigest() in (
        applied['embeddings']['sha256'], current['sha256'])
    # The cache was built from the REPAIRED catalog text, deterministically.
    catalog = fix.read_csv(fix.ROOT / fix.CAT)
    assert fix.embedding_input_digest(catalog) in (
        applied['embeddings']['input_sha256'], current['input_sha256'])


def test_embedding_cache_is_not_tracked():
    import subprocess
    tracked = subprocess.run(
        ['git', 'ls-files', '--', 'data/processed/viendinhduong/catalog_embeddings_bkai.pt'],
        cwd=fix.ROOT, capture_output=True, text=True, check=True).stdout.strip()
    assert tracked == ''


def test_data_interim_is_unchanged(applied):
    """Verified from the data itself, against the digest the batch recorded."""
    assert applied['validation']['interim_unchanged'] is True
    assert fix.interim_digest(fix.ROOT) == applied['interim']
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
    assert report['rows_repaired'] == fix.EXPECTED_ROWS == 92
    assert report['recipes_affected'] == fix.EXPECTED_RECIPES == 91
    assert report['alias_map_size'] == fix.ALIAS_MAP_SIZE_LIVE == 4684
    assert report['alias_actions'] == 18
    assert report['canonical_id_drift'] == 0
    assert report['representative_drift'] == 0
    assert report['populations'] == fix.EXPECTED_POPULATIONS
    assert report['corpus_nulls'] == fix.EXPECTED_CORPUS_NULLS
    assert report['downstream_hard_codes']['pending'] == 0
    assert report['qwen_mapper'] == {'active': 29, 'disabled': 20,
                                     'guarded_rule_disabled': True,
                                     'map_clean_to_master_bap_cai': None}


def test_applied_report_exists_and_describes_the_final_state(applied):
    assert applied['status'] == 'applied'
    assert applied['policy'] == 'DISPLAY_NAME_BATCH_C2'
    assert applied['rows_pending'] == 0
    assert applied['validation']['complete'] is True
    assert applied['validation']['blast_radius_measured_against'] == 'reviewed manifest, not git HEAD'
    assert (fix.OUT / 'applied_fix.md').exists()
    markdown = (fix.OUT / 'applied_fix.md').read_text(encoding='utf-8')
    for phrase in ('cần tàu', 'intentionally NOT matcher-reproducible',
                   'red cabbage', 'Cải bắp trắng'):
        assert phrase in markdown


def test_report_records_the_four_required_statements(applied):
    markdown = (fix.OUT / 'applied_fix.md').read_text(encoding='utf-8')
    # 1. the reviewed synonym
    assert applied['reviewed_synonym']['evidence_raw_text'] in markdown
    # 2. the clears are intentionally non-reproducible
    assert 'intentionally NOT matcher-reproducible' in markdown
    # 3. `bắp cải` moved off the red-cabbage extension onto the raw-backed 4010
    assert applied['alias_diff']['repointed']['bắp cải'] == {'before': '20035', 'after': '4010'}
    # 4. the two UNMATCHED recoveries avoid a C2-introduced divergence
    assert json.dumps(applied['cohorts']['white_cabbage_unmatched_recovery'],
                      ensure_ascii=False).count('"row_count": 2') == 1
