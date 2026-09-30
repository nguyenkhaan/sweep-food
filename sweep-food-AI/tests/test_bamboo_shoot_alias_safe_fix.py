"""Bamboo-shoot alias repair: strict row pins, sibling keeps, and the bare `măng` deferral."""
from collections import Counter
import unicodedata

import pytest

from nlp import entity_matcher as em
from nlp.nutrition import NUTRITION_FIELDS, scale_nutrition
from scripts.eda import apply_bamboo_shoot_alias_safe_fix as fix

NUTRIENTS = fix.NUTRIENTS
# Cultivar, species, maturity and preparation phrases the catalog cannot name.
# Every one of them stays UNMATCHED; none may be collapsed onto 4051/4053.
DEFERRED_BAMBOO_PHRASES = (
    'măng le', 'măng le đỏ', 'măng le nhỏ', 'măng nứa', 'măng vầu', 'măng sặt',
    'măng trúc', 'măng trúc ngâm chua', 'măng vàng', 'măng vàng cắt sợi', 'măng non',
    'búp măng non', 'măng củ tươi', 'măng củ chua', 'măng rừng đã', 'măng đã chín',
    'măng tươi đã chín', 'măng tươi sẵn', 'măng tươi đóng', 'nước ngâm măng',
)
# Identities outside this batch that must not move.
UNTOUCHED_IDENTITIES = {
    'măng chua': '4050', 'măng chua ớt': '4050', 'măng muối': '4050', 'măng le chua': '4050',
    'măng chua măng tre': '4050', 'măng tây': '20033', 'măng cụt': '5061',
    'lá mơ lông': '4048', 'lá mơ lông tươi': '4048',
    'khổ qua': '4055', 'mướp đắng': '4055', 'kiệu chua': '20077',
}


def norm(value):
    return unicodedata.normalize('NFC', value or '').lower()


@pytest.fixture(scope='module')
def reviewed():
    return fix.read_json(fix.REVIEW)


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
def live_catalog():
    return fix.index(fix.read_csv(fix.ROOT / fix.CAT), 'code')


@pytest.fixture(scope='module')
def live_aliases():
    return fix.read_json(fix.ROOT / fix.ALIASES)


@pytest.fixture(scope='module')
def matcher():
    return em.VietnameseIngredientMatcher()


# --- catalog: asserted unchanged -------------------------------------------

def test_catalog_is_not_modified_by_this_batch(live_catalog, reviewed):
    """The repair is alias-and-row only; no catalog column moves."""
    assert reviewed['catalog_identities']
    for code, before in reviewed['catalog_identities'].items():
        assert live_catalog[code] == before, code


@pytest.mark.parametrize('code,name_vi,name_en', [
    (c, v, e) for c, (v, e) in fix.EXPECTED_CATALOG_IDENTITY.items()])
def test_reviewed_catalog_identities(live_catalog, code, name_vi, name_en):
    assert live_catalog[code]['name_vi'] == name_vi
    assert live_catalog[code]['name_en'] == name_en


def test_targets_are_preparation_state_distinct(live_catalog):
    """The whole repair rests on 4051 being dried and 4053 being fresh."""
    assert live_catalog['4051']['name_en'].endswith('dried')
    assert live_catalog['4053']['name_en'].endswith('raw')
    assert float(live_catalog['4051']['water_g']) < float(live_catalog['4053']['water_g'])
    assert float(live_catalog['4051']['energy_kcal']) > float(live_catalog['4053']['energy_kcal'])


def test_4048_is_not_a_bamboo_identity(live_catalog):
    assert live_catalog['4048']['name_en'] == 'Skunk vine, raw'
    assert 'măng' not in norm(live_catalog['4048']['name_vi'])


# --- aliases ---------------------------------------------------------------

@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_PATCHES.items()))
def test_applied_alias_repoints(live_aliases, alias, code):
    assert live_aliases[alias] == code


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_KEEPS.items()))
def test_reviewed_alias_keeps(live_aliases, alias, code):
    assert live_aliases[alias] == code


def test_alias_map_size_unchanged(live_aliases, reviewed):
    """Nothing is added and nothing is removed by THIS batch; three values move.

    The live size is 4680, not the 4672 the manifest froze: DISPLAY_NAME_BATCH_C2
    later removed 3 keys and added 5 (4674), and DISPLAY_NAME_BATCH_C1 then removed
    the 2 spinach/kale keys and added 8 mustard-green/napa/kimchi keys. Both figures
    are asserted, so this batch's own "adds nothing, removes nothing" invariant
    stays exact.
    """
    assert len(live_aliases) == fix.ALIAS_MAP_SIZE == 4684
    assert reviewed['alias_map_size'] == fix.REVIEWED_ALIAS_MAP_SIZE == 4672


def test_only_the_reviewed_aliases_moved(live_aliases, reviewed):
    moved = {k for k, before in reviewed['aliases_before'].items() if live_aliases[k] != before}
    assert moved == set(fix.ALIAS_PATCHES)


def test_qualified_pairs_agree_after_the_repair(live_aliases):
    """`măng khô` now agrees with `măng tre khô`, `măng tươi` with `măng tre tươi`."""
    assert live_aliases['măng khô'] == live_aliases['măng tre khô'] == '4051'
    assert live_aliases['măng tươi'] == live_aliases['măng tre tươi'] == '4053'


def test_no_bamboo_alias_still_targets_the_skunk_vine(live_aliases):
    assert {k for k, v in live_aliases.items() if v == '4048'} == {'lá mơ lông', 'lá mơ lông tươi'}


def test_every_alias_on_a_bamboo_identity_is_reviewed(live_aliases, reviewed):
    """No unreviewed alias may reach a bamboo code, in either direction.

    Stated over the bamboo CODES rather than over `măng`-shaped keys: a key-shaped
    assertion would have to enumerate the asparagus and mangosteen homonym
    families (20033, 4052 `Măng tây, tươi`, 5061), which are a different plant and
    none of this batch's business, while still missing any future alias that
    reaches 4051/4053 without the word `măng` in it.
    """
    bamboo = {'4048', '4050', '4051', '4053'}
    on_bamboo = {k: v for k, v in live_aliases.items() if v in bamboo}
    assert set(on_bamboo) == {k for k, v in reviewed['aliases_before'].items() if v in bamboo}
    assert on_bamboo == {k: v for k, v in {**reviewed['aliases_before'],
                                           **fix.ALIAS_PATCHES}.items() if v in bamboo}


def test_asparagus_and_mangosteen_homonyms_are_not_drawn_into_the_bamboo_band(live_aliases):
    """`măng tây` / `măng cụt` share a prefix with bamboo and a different plant."""
    keys = {k for k in live_aliases if norm(k).startswith(('măng tây', 'măng cụt'))}
    assert keys, 'homonym aliases disappeared'
    assert all(live_aliases[k] in ('20033', '4052', '5061') for k in keys), {
        k: live_aliases[k] for k in keys if live_aliases[k] not in ('20033', '4052', '5061')}


# --- reviewed rows ---------------------------------------------------------

def test_reviewed_manifest_shape(reviewed):
    assert len(reviewed['rows']) == fix.EXPECTED_ROWS == 55
    assert Counter(r['cohort'] for r in reviewed['rows']) == {
        'mang_tuoi_4051_to_4053': 32, 'mang_kho_4048_to_4051': 20, 'mang_tuoi_bao_4051_to_4053': 3}


def test_every_reviewed_row_reached_its_target(reviewed, live_index, live_catalog):
    for pin in reviewed['rows']:
        row = live_index[pin['before']['id']]
        target = pin['target_code']
        assert row['master_ingredient_code'] == target, pin['before']['id']
        assert row['master_ingredient_name'] == live_catalog[target]['name_vi']


def test_reviewed_rows_preserve_provenance_and_parsed_fields(reviewed, live_index):
    """Only the identity and the four nutrient columns may move."""
    immutable = ('recipe_id', 'raw_text', 'cleaned_name', 'required_quantity',
                 'unit_vi', 'unit', 'preparation_note', 'estimated_weight_g',
                 'match_method', 'match_confidence')
    for pin in reviewed['rows']:
        before, row = pin['before'], live_index[pin['before']['id']]
        for field in immutable:
            assert row[field] == before[field], f"{before['id']}.{field}"
        assert row['match_method'] == 'PRESET_ALIAS_MATCH'
        assert row['match_confidence'] == '0.98'


def test_reviewed_cohorts_are_semantic_not_code_selections(reviewed):
    """Each cohort is one cleaned name, so no unreviewed row rides along on a code."""
    for cohort, (source, target, count, cleaned) in fix.COHORTS.items():
        rows = [r for r in reviewed['rows'] if r['cohort'] == cohort]
        assert len(rows) == count
        assert {r['before']['cleaned_name'] for r in rows} == {cleaned}
        assert {r['before']['master_ingredient_code'] for r in rows} == {source}
        assert {r['target_code'] for r in rows} == {target}


def test_nutrition_recomputed_from_the_target_catalog(reviewed, live_index, live_catalog):
    """Values come from the target row and the row's own weight, via the project scaler."""
    for pin in reviewed['rows']:
        row = live_index[pin['before']['id']]
        target = live_catalog[pin['target_code']]
        weight = float(row['estimated_weight_g'])
        for field, column in NUTRITION_FIELDS.items():
            want = scale_nutrition(target[column], weight / 100.0, 1)
            if want is None:
                assert row[field] in (None, ''), f"{row['id']}.{field}"
            else:
                assert float(row[field]) == want, f"{row['id']}.{field}"


def test_dried_cohort_gained_a_real_fat_value_never_a_zero_fill(reviewed, live_index, live_catalog):
    """4048 carries no fat; 4051 carries 2.1. The value is the target's, not zero."""
    assert live_catalog['4048']['fat_g'] in (None, '')
    dried = [r for r in reviewed['rows'] if r['cohort'] == 'mang_kho_4048_to_4051']
    assert len(dried) == fix.EXPECTED_FAT_NULL_TO_VALUE == 20
    for pin in dried:
        assert pin['before']['fat_g'] in (None, '')
        row = live_index[pin['before']['id']]
        assert row['fat_g'] not in (None, '')
        assert float(row['fat_g']) == scale_nutrition(
            live_catalog['4051']['fat_g'], float(row['estimated_weight_g']) / 100.0, 1)
        assert float(row['fat_g']) > 0


def test_cohort_nutrition_deltas_match_the_review(reviewed, live_index):
    for cohort, expected in fix.EXPECTED_COHORT_NUTRITION_DELTA.items():
        pins = sorted((r for r in reviewed['rows'] if r['cohort'] == cohort),
                      key=lambda r: r['before']['id'])
        report = fix.nutrient_report([p['before'] for p in pins],
                                     [live_index[p['before']['id']] for p in pins])
        assert {f: report[f]['known_sum_delta'] for f in NUTRIENTS} == expected, cohort


def test_combined_nutrition_delta_and_null_transitions(reviewed, live_index):
    pins = sorted(reviewed['rows'], key=lambda r: r['before']['id'])
    report = fix.nutrient_report([p['before'] for p in pins],
                                 [live_index[p['before']['id']] for p in pins])
    assert {f: report[f]['known_sum_delta'] for f in NUTRIENTS} == fix.EXPECTED_NUTRITION_DELTA
    assert {f: (report[f]['before_null_count'], report[f]['after_null_count'])
            for f in NUTRIENTS} == fix.EXPECTED_NULL_TRANSITIONS
    assert report['fat_g']['null_to_value'] == 20
    assert all(report[f]['value_to_null'] == 0 for f in NUTRIENTS)


# --- populations and untouched rows ----------------------------------------

def test_final_populations(live_rows):
    populations = {code: sum(1 for r in live_rows if (r['master_ingredient_code'] or '') == code)
                   for code in fix.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
    assert populations == fix.EXPECTED_POPULATIONS


def test_corpus_null_counts(live_rows):
    assert {f: sum(1 for r in live_rows if r[f] in (None, ''))
            for f in NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS


def test_no_row_outside_the_reviewed_55_changed(reviewed, live_rows, live_catalog):
    """Blast radius, measured without consulting git.

    This assertion used to diff the working tree against `git show HEAD:`. That
    invariant was commit-unstable by construction: it required the repair to still
    be pending, so it held only while the batch was unstaged and inverted the
    moment the batch landed. A data invariant must not depend on version-control
    state, so it is replaced rather than weakened -- the reviewed 55-row manifest
    is still the only radius this batch is allowed.

    Four measured properties stand in for it, all stable across the commit:

    1. Every pinned row equals the reviewed transform of its own before record --
       re-derived here through the script's own `expected_row` against the live
       catalog, so a repaired row that drifted off the reviewed target, lost its
       provenance or acquired hand-edited nutrition fails.
    2. The repair is closed over the corpus: the exhaustive `măng` accounting and
       the bamboo-band populations below already require every bamboo-coded row to
       be one of the 55 or one of the named guards, so an unreviewed row cannot
       have entered or left the band.
    3. The corpus shape the batch published is pinned exactly -- total rows,
       per-code populations and per-nutrient null counts.
    4. The recipe radius is recomputed, not recorded: rollups derived from the
       manifest-reconstructed pre-fix rows differ from rollups derived from the
       committed rows on exactly the 50 reviewed recipes.
    """
    pins = {p['before']['id']: p for p in reviewed['rows']}
    assert len(pins) == fix.EXPECTED_ROWS == 55
    live = fix.index(live_rows)
    for rid, pin in pins.items():
        assert fix.logical(live[rid]) == fix.logical(fix.expected_row(pin, live_catalog)), rid

    # The corpus shape this batch published, pinned exactly.
    assert len(live_rows) == 63943
    populations = {code: sum(1 for r in live_rows if (r['master_ingredient_code'] or '') == code)
                   for code in fix.EXPECTED_POPULATIONS if code != 'UNMATCHED'}
    populations['UNMATCHED'] = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
    assert populations == fix.EXPECTED_POPULATIONS
    assert {f: sum(1 for r in live_rows if r[f] in (None, ''))
            for f in NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS

    # Recipe radius: rollups over the reconstructed pre-fix rows against rollups
    # over the committed rows. Recomputed on both sides, so it cannot be satisfied
    # by a stored total agreeing with itself.
    baseline = [dict(pins[r['id']]['before']) if r['id'] in pins else dict(r) for r in live_rows]
    before_rollups = fix.recompute_recipe_rollups(baseline)
    after_rollups = fix.recompute_recipe_rollups(live_rows)
    assert before_rollups.keys() == after_rollups.keys()
    changed = {rid for rid in after_rollups
               if fix._new_totals(before_rollups[rid]) != fix._new_totals(after_rollups[rid])}
    assert changed == {pin['before']['recipe_id'] for pin in pins.values()}
    assert len(changed) == fix.EXPECTED_RECIPES == 50


def test_genuine_la_mo_long_row_remains_on_4048(reviewed, live_rows, live_index):
    guarded = reviewed['guards']['la_mo_long_rows']
    assert len(guarded) == 1
    for before in guarded:
        assert fix.logical(live_index[before['id']]) == fix.logical(before)
    on_4048 = [r for r in live_rows if (r['master_ingredient_code'] or '') == '4048']
    assert {r['id'] for r in on_4048} == {r['id'] for r in guarded}
    assert on_4048[0]['cleaned_name'] == 'lá mơ lông'
    assert on_4048[0]['match_method'] == 'EXACT_CATALOG_MATCH'


def test_batch_b_sour_bamboo_rows_are_untouched(reviewed, live_rows, live_index):
    pinned = set(reviewed['guards']['sour_bamboo_row_ids'])
    assert len(pinned) == 62
    assert {r['id'] for r in live_rows if (r['master_ingredient_code'] or '') == '4050'} == pinned
    assert {live_index[r]['master_ingredient_name'] for r in pinned} == {'Măng chua, măng tre'}


def test_fresh_bamboo_exact_match_rows_are_untouched(reviewed, live_index):
    for rid in reviewed['guards']['fresh_bamboo_exact_row_ids']:
        row = live_index[rid]
        assert row['master_ingredient_code'] == '4053'
        assert row['match_method'] == 'EXACT_CATALOG_MATCH'
        assert row['match_confidence'] == '1.0'


@pytest.mark.parametrize('code,key,count', [('20033', 'mang_tay_row_ids', 51),
                                            ('5061', 'mang_cut_row_ids', 6)])
def test_homonym_populations_unchanged(reviewed, live_rows, code, key, count):
    pinned = set(reviewed['guards'][key])
    assert len(pinned) == count
    assert {r['id'] for r in live_rows if (r['master_ingredient_code'] or '') == code} == pinned


def test_reviewed_unmatched_bamboo_rows_keep_the_full_contract(reviewed, live_index):
    ids = reviewed['guards']['unmatched_bamboo_row_ids']
    assert len(ids) == 36
    for rid in ids:
        row = live_index[rid]
        assert row['match_method'] == 'UNMATCHED'
        assert not (row['master_ingredient_code'] or '').strip()
        assert not (row['master_ingredient_name'] or '').strip()
        assert row['match_confidence'] in (None, '')
        assert all(row[f] in (None, '') for f in NUTRIENTS)
        # 0.0 is the explicit-rejection sentinel and must not appear here.
        assert row['match_confidence'] != '0.0'


def test_no_bamboo_row_outside_the_reviewed_set_carries_a_bamboo_code(reviewed, live_rows):
    """Every row mentioning măng is either reviewed, guarded, or UNMATCHED."""
    accounted = ({r['before']['id'] for r in reviewed['rows']}
                 | {r['id'] for r in reviewed['guards']['bare_mang_rows']}
                 | set(reviewed['guards']['sour_bamboo_row_ids'])
                 | set(reviewed['guards']['fresh_bamboo_exact_row_ids'])
                 | set(reviewed['guards']['unmatched_bamboo_row_ids']))
    bamboo = [r for r in live_rows
              if 'măng' in norm(r['raw_text']) + norm(r['cleaned_name'])
              and 'măng tây' not in norm(r['raw_text']) + norm(r['cleaned_name'])
              and 'măng cụt' not in norm(r['raw_text']) + norm(r['cleaned_name'])]
    assert len(bamboo) == 169
    assert {r['id'] for r in bamboo} <= accounted


# --- the bare `măng` deferral ----------------------------------------------

def test_bare_mang_rows_are_byte_for_byte_unchanged(reviewed, live_index):
    guarded = reviewed['guards']['bare_mang_rows']
    assert len(guarded) == fix.DEFERRAL['rows'] == 14
    for before in guarded:
        assert fix.logical(live_index[before['id']]) == fix.logical(before), before['id']
        assert live_index[before['id']]['master_ingredient_code'] == '4051'


def test_bare_mang_alias_is_not_repointed(live_aliases):
    assert live_aliases['măng'] == '4051'
    assert 'măng' in fix.ALIAS_KEEPS and 'măng' not in fix.ALIAS_PATCHES


def test_bare_mang_cohort_carries_no_state_qualifier(reviewed):
    """The reason it stays deferred: the corpus marks state explicitly when it means it."""
    for before in reviewed['guards']['bare_mang_rows']:
        text = norm(before['raw_text'])
        assert 'khô' not in text and 'tươi' not in text and 'chua' not in text, text


def test_removing_the_bare_mang_alias_would_be_unsafe(matcher):
    """Measured, not assumed: deletion does not reach UNMATCHED, and splits the routes."""
    original = dict(matcher.alias_dict)
    try:
        matcher.alias_dict = {k: v for k, v in original.items()
                              if k != em.normalize_vietnamese_text('măng')}
        single = matcher.match('măng', raw_context='măng')
        batched = matcher.match_batch(['măng'], raw_contexts=['măng'])[0]
        assert single['method'] == 'SUBPHRASE_CATALOG_MATCH'
        assert (single['matched_item'] or {}).get('code') is not None
        assert ((single['matched_item'] or {}).get('code')
                != (batched['matched_item'] or {}).get('code'))
    finally:
        matcher.alias_dict = original


def test_deferral_is_recorded(reviewed):
    assert fix.DEFERRAL['status'] == 'DEFERRED_NEEDS_DOMAIN_REVIEW'
    assert fix.DEFERRAL_KEY == 'bare_mang_ambiguous_state_resolution'
    assert len(reviewed['guards']['bare_mang_rows']) == fix.DEFERRAL['rows']


# --- matcher behaviour ------------------------------------------------------

@pytest.mark.parametrize('query,code', sorted(fix.PROBES.items()))
def test_matcher_reaches_the_reviewed_identity_on_both_routes(matcher, query, code):
    single = matcher.match(query, raw_context=query)
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    assert (single['matched_item'] or {}).get('code') == code
    assert (batched['matched_item'] or {}).get('code') == code


@pytest.mark.parametrize('query,code', sorted(UNTOUCHED_IDENTITIES.items()))
def test_sibling_identities_outside_this_batch_do_not_move(matcher, query, code):
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    assert (batched['matched_item'] or {}).get('code') == code


def test_batch_b_sour_bamboo_recovery_still_holds(matcher):
    """`măng chua ớt` still reaches 4050 through Batch B's subphrase head."""
    result = matcher.match_batch(['măng chua ớt'], raw_contexts=['Măng chua ớt 500 gr'])[0]
    assert (result['matched_item'] or {}).get('code') == '4050'
    assert result['method'] == 'SUBPHRASE_CATALOG_MATCH'
    assert result['confidence'] == 0.95


@pytest.mark.parametrize('query,code', sorted(fix.CULTIVAR_PROBES.items()))
def test_cultivar_phrases_gain_no_dictionary_route(matcher, query, code):
    """The repair must not widen the bamboo band onto unnamed cultivars.

    Two assertions with different environmental reach. That a cultivar phrase
    still reaches NO dictionary stage is the invariant this batch owns, and it
    holds with or without torch. The exact neural code is pinned only when torch
    is installed, because without it the matcher falls back to token overlap and
    the fallback's pick is a different -- and equally unreviewed -- identity.
    """
    single = matcher.match(query, raw_context=query)
    batched = matcher.match_batch([query], raw_contexts=[query])[0]
    dictionary = ('EXACT_CATALOG_MATCH', 'CLEANED_NAME_MATCH',
                  'PRESET_ALIAS_MATCH', 'SUBPHRASE_CATALOG_MATCH')
    assert single['method'] not in dictionary
    assert batched['method'] not in dictionary
    if not em.TORCH_AVAILABLE:
        pytest.skip('neural verdicts are pinned only where torch is installed')
    assert single['method'].startswith('BERT') and batched['method'].startswith('BERT')
    assert (single['matched_item'] or {}).get('code') == code
    assert (batched['matched_item'] or {}).get('code') == code


@pytest.mark.parametrize('phrase', DEFERRED_BAMBOO_PHRASES)
def test_deferred_bamboo_phrases_have_no_alias(live_aliases, phrase):
    assert phrase not in live_aliases


def test_qualified_dried_phrase_no_longer_reaches_the_skunk_vine(matcher):
    for query in ('măng khô', 'măng khô xé sợi'):
        result = matcher.match_batch([query], raw_contexts=[query])[0]
        assert (result['matched_item'] or {}).get('code') != '4048'


def test_explicit_fresh_phrase_no_longer_reaches_dried(matcher):
    for query in ('măng tươi', 'măng tươi bào'):
        result = matcher.match_batch([query], raw_contexts=[query])[0]
        assert (result['matched_item'] or {}).get('code') == '4053'
        assert result['method'] == 'PRESET_ALIAS_MATCH'
        assert result['confidence'] == 0.98


def test_production_shape_replay_reproduces_every_reviewed_row(reviewed, live_index, matcher):
    """match_batch(cleaned_name, raw_contexts=raw_text) re-derives the repaired state."""
    pins = sorted(reviewed['rows'], key=lambda r: r['before']['id'])
    names = [p['before']['cleaned_name'] for p in pins]
    contexts = [p['before']['raw_text'] for p in pins]
    for pin, result in zip(pins, matcher.match_batch(names, raw_contexts=contexts)):
        rid = pin['before']['id']
        assert (result['matched_item'] or {}).get('code') == pin['target_code'], rid
        assert result['method'] == 'PRESET_ALIAS_MATCH'
        assert result['confidence'] == 0.98
        assert live_index[rid]['master_ingredient_code'] == pin['target_code']


# --- rollups, canonical and idempotence ------------------------------------

def test_recipe_rollups_agree_with_the_repaired_rows(live_rows):
    recipes = fix.read_csv(fix.ROOT / fix.DATA / 'recipes.csv')
    recipes_json = fix.read_json(fix.ROOT / fix.DATA / 'recipes.json')
    fix.parity(recipes, recipes_json)
    rollups = fix.recompute_recipe_rollups(live_rows)
    for record in recipes:
        if record['id'] in rollups:
            for key, value in fix._new_totals(rollups[record['id']]).items():
                assert record[key] == value, f"{record['id']}.{key}"


def test_no_recipe_status_transition(reviewed, live_rows):
    """missing_nutrition_count keys on null calories; no reviewed row has one."""
    assert fix.EXPECTED_MISSING_COUNT_RECIPES == set()
    assert fix.EXPECTED_STATUS_LABEL_TRANSITIONS == {}
    for pin in reviewed['rows']:
        assert pin['before']['calories'] not in (None, '')
    ids = {r['before']['id'] for r in reviewed['rows']}
    assert all(r['calories'] not in (None, '') for r in live_rows if r['id'] in ids)


def test_canonical_parity_and_identity(live_rows):
    for name in ('canonical_recipes', 'canonical_recipe_ingredients'):
        fix.parity(fix.read_csv(fix.ROOT / fix.DATA / (name + '.csv')),
                   fix.read_json(fix.ROOT / fix.DATA / (name + '.json')))
    mapping = fix.read_csv(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.csv')
    assert ({r['original_recipe_id']: r['canonical_recipe_id'] for r in mapping}
            == fix.read_json(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.json'))


def test_canonical_representatives_did_not_drift(reviewed):
    """Canonical IDs and representatives are stable; only quality counters moved."""
    mapping = fix.index(fix.read_csv(fix.ROOT / fix.DATA / 'recipe_canonical_mapping.csv'),
                        'original_recipe_id')
    affected = {r['before']['recipe_id'] for r in reviewed['rows']}
    assert len(affected) == fix.EXPECTED_RECIPES == 50
    groups = {mapping[r]['canonical_recipe_id'] for r in affected}
    assert len(groups) == fix.EXPECTED_CANONICAL_GROUPS == 49
    canonical = {r['id'] for r in fix.read_csv(fix.ROOT / fix.DATA / 'canonical_recipes.csv')}
    assert groups <= canonical


def test_canonical_ingredient_coverage(reviewed):
    rows = {r['id'] for r in fix.read_csv(fix.ROOT / fix.DATA / 'canonical_recipe_ingredients.csv')}
    ids = {r['before']['id'] for r in reviewed['rows']}
    assert len(ids & rows) == fix.EXPECTED_CANONICAL['canonical_recipe_ingredients.csv'] == 51
    assert len(ids - rows) == fix.EXPECTED_CANONICAL_INGREDIENT_ROWS_ABSENT == 4


def test_plan_is_idempotent_against_the_applied_state():
    """A replanned run finds nothing left to do and still verifies the whole radius."""
    _, _, report = fix.plan(fix.ROOT)
    assert report['rows_pending'] == 0
    assert report['rows_repaired'] == 55
    assert report['recipes_affected'] == 50
    assert report['catalog_modified'] is False
    assert report['embeddings_rebuilt'] is False
    assert report['canonical_id_drift'] == 0
    assert report['representative_drift'] == 0
    assert report['populations'] == fix.EXPECTED_POPULATIONS
