"""DISPLAY_NAME_BATCH_C1 hardening: the dried-salted-napa reviewed catalog gap.

C1 cleared row 2c660d89 `1 muỗng cải thảo muối khô` to UNMATCHED because dried
salted napa has no exact catalog identity. Clearing it made the row Qwen-eligible
for the first time, and its cached Qwen output `cải thảo` resolves through the
live mapper to 4109 `Rau cải thảo` -- FRESH napa, a different preparation with a
different nutrition profile. Measured before the fix, the production recovery
block produced a candidate for it, so a Qwen pass would have silently undone the
reviewed clear.

The fix is a production exclusion, not a test assertion: the reviewed raw line is
pinned in `_REVIEWED_NO_CATALOG_TARGET_RAW` and refused by
`qwen_candidate_eligibility()`, the same guard the pipeline consults. These tests
replay the real pipeline decision path rather than calling the guard alone, so a
regression that leaves the guard intact but bypasses it still fails here.
"""

import csv
import json
from collections import Counter
from pathlib import Path

import pytest

from nlp.qwen_matching import (
    _REVIEWED_NO_CATALOG_TARGET_INDEX,
    _REVIEWED_NO_CATALOG_TARGET_RAW,
    build_mapper_rules,
    eligible_for_qwen_recovery,
    map_clean_to_master,
    qwen_candidate_eligibility,
)
from scripts.eda import apply_display_name_batch_c1_safe_fix as c1

ROOT = Path(__file__).resolve().parents[1]
QWEN_CACHE = ROOT / 'data/interim/qwen_extracted_map.json'
MASTER_CSV = ROOT / 'data/processed/viendinhduong/master_ingredients_nutrition.csv'
PROCESSED_ING = ROOT / 'data/processed/recipes/recipe_ingredients.csv'

ROW_ID = '2c660d89'
RAW = '1 muỗng cải thảo muối khô'
REASON = 'DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET'
FRESH_NAPA = ('4109', 'Rau cải thảo')
C1_HISTORICAL_POPULATIONS = {
    '4010': 14, '4011': 0, '4015': 11, '4016': 60, '4027': 270, '4109': 73,
    '4115': 1, '20034': 75, '4094': 106, '4135': 59, '4018': 177,
    '20035': 33, '4013': 122, '4021': 147, '20086': 101, 'UNMATCHED': 8499,
}
C1_HISTORICAL_NULLS = {
    'calories': 8499, 'protein_g': 16957, 'fat_g': 20262, 'carbs_g': 17458,
}


@pytest.fixture(scope='module')
def master():
    with MASTER_CSV.open(encoding='utf-8-sig', newline='') as stream:
        return {r['code']: r for r in csv.DictReader(stream)}


@pytest.fixture(scope='module')
def active(master):
    return build_mapper_rules(master)[0]


@pytest.fixture(scope='module')
def cache():
    return json.loads(QWEN_CACHE.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def rows():
    with PROCESSED_ING.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def pipeline_decision(row, cache, active):
    """Replay scripts/run_qwen_line_pipeline.py block B for one row.

    Deliberately a re-statement of the production sequence rather than a call to
    the guard: the claim under test is that the row cannot reach a candidate, not
    merely that one function returns False.
    """
    raw = (row.get('raw_text') or '').strip()
    if not eligible_for_qwen_recovery(row) or raw not in cache:
        return {'reached_block_b': False, 'candidate': None, 'reason': None}
    cleaned = cache[raw]
    code, name = map_clean_to_master(cleaned, active)
    allowed, reason = qwen_candidate_eligibility(raw, cleaned, code)
    candidate = (code, name, 'QWEN_LLM_MATCH') if (code and name and allowed) else None
    return {'reached_block_b': True, 'cached_output': cleaned, 'winning_code': code,
            'candidate': candidate, 'reason': reason}


# --- the production exclusion ------------------------------------------------

def test_the_reviewed_line_is_declared_with_its_reviewed_reason():
    assert RAW in _REVIEWED_NO_CATALOG_TARGET_RAW
    code, reason = _REVIEWED_NO_CATALOG_TARGET_RAW[RAW]
    assert reason == REASON
    # The code is recorded as evidence of the neighbour the mapper would publish.
    assert code == FRESH_NAPA[0]


def test_the_exclusion_table_is_narrow():
    """One reviewed line. Not a word, not a code, not a cleaned output."""
    assert len(_REVIEWED_NO_CATALOG_TARGET_RAW) == 1
    assert len(_REVIEWED_NO_CATALOG_TARGET_INDEX) == 1
    assert all(len(key.split()) >= 5 for key in _REVIEWED_NO_CATALOG_TARGET_RAW)


def test_2c660d89_is_not_qwen_recoverable(rows, cache, active):
    """The whole point: the production path yields no candidate for this row."""
    row = next(r for r in rows if r['id'].startswith(ROW_ID))
    decision = pipeline_decision(row, cache, active)
    # It does reach block B -- it is genuinely unlinked and genuinely cached --
    # and is refused there. That is the durable block.
    assert decision['reached_block_b'] is True
    assert decision['cached_output'] == 'cải thảo'
    assert decision['winning_code'] == FRESH_NAPA[0]
    assert decision['candidate'] is None
    assert decision['reason'] == REASON


def test_the_rejection_reason_is_the_reviewed_exclusion():
    allowed, reason = qwen_candidate_eligibility(RAW, 'cải thảo', FRESH_NAPA[0])
    assert allowed is False
    assert reason == REASON


def test_the_exclusion_refuses_whatever_the_mapper_resolved(rows, cache, active):
    """The reviewed claim is `no exact catalog identity`, not `not this code`."""
    for winning_code in (FRESH_NAPA[0], '4115', '20034', '4016', None):
        assert qwen_candidate_eligibility(RAW, 'cải thảo', winning_code) == (False, REASON)


# --- narrowness: nothing else may be refused ---------------------------------

def test_mapper_behaviour_for_genuine_fresh_napa_is_unchanged(active):
    """The 4109 rule itself is untouched -- the guard sits downstream of it."""
    assert map_clean_to_master('cải thảo', active) == FRESH_NAPA
    assert map_clean_to_master('bắp cải thảo', active) == FRESH_NAPA
    assert map_clean_to_master('lá cải thảo', active) == FRESH_NAPA


@pytest.mark.parametrize('raw,cleaned', [
    ('Cải thảo 2 lá', 'cải thảo'),
    ('Cải thảo 15 lá', 'cải thảo'),
    ('Cải thảo 8 bẹ', 'cải thảo'),
    ('Cải thảo: 12 lá bỏ cọng', 'cải thảo'),
    ('Vài lá cải thảo', 'cải thảo'),
    ('1 chén lá cải thảo', 'lá cải thảo'),
    ('2-3 lá cải thảo', 'lá cải thảo'),
    ('3 lá cải thảo', 'lá cải thảo'),
    ('8 cái lá cải thảo', 'lá cải thảo'),
])
def test_fresh_napa_lines_remain_eligible(raw, cleaned, active):
    code, _name = map_clean_to_master(cleaned, active)
    assert code == FRESH_NAPA[0]
    assert qwen_candidate_eligibility(raw, cleaned, code) == (True, None)


@pytest.mark.parametrize('raw,cleaned', [
    ('1 chén kimchi cải thảo', 'kimchi cải thảo'),
    ('1 bát con đầy Kim chi cải thảo loại chua nhiều', 'kim chi cải thảo'),
    ('Cải thảo muối 100 gr', 'cải thảo'),
])
def test_kimchi_and_pickled_napa_are_not_refused_generally(raw, cleaned, active):
    """Those foods DO have identities (20034, 4115); nothing here blocks them."""
    code, _name = map_clean_to_master(cleaned, active)
    assert qwen_candidate_eligibility(raw, cleaned, code) == (True, None)


@pytest.mark.parametrize('raw', [
    '1 muỗng cải thảo muối',
    '2 muỗng cải thảo muối khô',
    'cải thảo muối khô',
    '1 muỗng cải thảo muối khô thêm',
])
def test_near_miss_lines_are_not_caught(raw, active):
    """Whole-line pinning, not a substring rule: near misses stay eligible."""
    code, _name = map_clean_to_master('cải thảo', active)
    assert qwen_candidate_eligibility(raw, 'cải thảo', code) == (True, None)


def test_no_word_level_rule_leaked_into_the_table():
    for key in _REVIEWED_NO_CATALOG_TARGET_RAW:
        assert key not in ('cải thảo', 'muối', 'khô', 'muối khô')


def test_exactly_one_corpus_row_is_newly_refused(rows, cache, active):
    """Corpus-wide: the exclusion changes the verdict for one row and no other."""
    refused = {}
    for row in rows:
        decision = pipeline_decision(row, cache, active)
        if decision['reached_block_b'] and decision['reason'] == REASON:
            refused[row['id']] = decision
    assert len(refused) == 1
    assert next(iter(refused)).startswith(ROW_ID)


def test_the_rest_of_the_flow_is_unchanged(rows, cache, active):
    """Measured totals for the whole corpus, pinned so the guard cannot widen."""
    decisions = [pipeline_decision(r, cache, active) for r in rows]
    reaching = [d for d in decisions if d['reached_block_b']]
    with_candidate = [d for d in reaching if d['winning_code']]
    # Batch C3 recovered four previously-UNMATCHED cabbage rows, so they no
    # longer enter Qwen recovery. Candidate and rejection behavior is unchanged.
    assert len(reaching) == 453
    assert len(with_candidate) == 49
    assert sum(1 for d in with_candidate if d['candidate']) == 39
    assert Counter(d['reason'] for d in with_candidate if not d['candidate']) == {
        'generic_ngo_conflicts_with_raw_ngo_gai': 7,
        'qwen_explicit_ingredient_list': 2,
        REASON: 1,
    }


def test_the_salted_napa_row_is_protected_by_its_stored_link(rows, cache, active):
    """89749d54 needs no exclusion: C1 left it linked to 4115, so it never
    reaches block B. Recorded here so the protection is a tested fact rather
    than an assumption -- if a later batch ever clears it, this test changes and
    the row needs the same reviewed treatment as 2c660d89."""
    row = next(r for r in rows if r['id'].startswith('89749d54'))
    assert row['master_ingredient_code'] == '4115'
    assert eligible_for_qwen_recovery(row) is False
    assert pipeline_decision(row, cache, active)['reached_block_b'] is False


# --- C1's stored state must not have moved -----------------------------------

def test_c1_clear_set_is_unchanged(rows):
    review = c1.read_json(c1.REVIEW)
    pins = {p['before']['id']: p for p in review['rows']}
    cleared = {rid for rid, p in pins.items() if p['target_code'] is None}
    assert len(cleared) == c1.EXPECTED_CLEARS == 35
    live = {r['id']: r for r in rows}
    for rid in cleared:
        row = live[rid]
        assert row['match_method'] == 'UNMATCHED'
        assert not (row['master_ingredient_code'] or '').strip()
        assert all(row[f] in (None, '') for f in c1.NUTRIENTS)
    assert next(rid for rid in cleared if rid.startswith(ROW_ID))


def test_c1_historical_and_live_populations_are_correct(rows):
    applied = c1.read_json(c1.OUT / 'applied_fix.json')
    assert applied['populations'] == C1_HISTORICAL_POPULATIONS

    populations = {code: sum(1 for r in rows if (r['master_ingredient_code'] or '') == code)
                   for code in c1.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in rows if r['match_method'] == 'UNMATCHED')
    assert populations == c1.EXPECTED_POPULATIONS
    assert {code: populations[code] for code in ('4010', '4011', '4013', '4021', 'UNMATCHED')} == {
        '4010': 105, '4011': 0, '4013': 54, '4021': 128, 'UNMATCHED': 8495,
    }
    assert populations['4109'] == 73
    assert {code: populations[code] - applied['populations'][code]
            for code in ('4010', '4013', '4021', 'UNMATCHED')} == {
        '4010': 91, '4013': -68, '4021': -19, 'UNMATCHED': -4,
    }


def test_c1_historical_and_live_corpus_nulls_are_correct(rows):
    applied = c1.read_json(c1.OUT / 'applied_fix.json')
    assert applied['corpus_nulls'] == C1_HISTORICAL_NULLS

    live = {f: sum(1 for r in rows if r[f] in (None, '')) for f in c1.NUTRIENTS}
    assert live == c1.EXPECTED_CORPUS_NULLS == {
        'calories': 8495, 'protein_g': 16953, 'fat_g': 20190, 'carbs_g': 17454}
    assert {f: live[f] - applied['corpus_nulls'][f] for f in c1.NUTRIENTS} == {
        'calories': -4, 'protein_g': -4, 'fat_g': -72, 'carbs_g': -4}


def test_the_hardening_touched_no_processed_data(rows):
    """The hardening changed no data; later C3 movement is exactly accounted."""
    applied = c1.read_json(c1.OUT / 'applied_fix.json')
    live_populations = {
        code: sum(1 for r in rows if (r['master_ingredient_code'] or '') == code)
        for code in applied['populations'] if code != 'UNMATCHED'
    } | {'UNMATCHED': sum(1 for r in rows if r['match_method'] == 'UNMATCHED')}
    assert {code: (applied['populations'][code], live_populations[code])
            for code in ('4010', '4011', '4013', '4021', 'UNMATCHED')} == {
        '4010': (14, 105), '4011': (0, 0), '4013': (122, 54),
        '4021': (147, 128), 'UNMATCHED': (8499, 8495),
    }
    assert applied['corpus_nulls'] == C1_HISTORICAL_NULLS
    assert applied['rows_repaired'] == 345
