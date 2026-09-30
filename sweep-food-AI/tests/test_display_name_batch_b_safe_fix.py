"""The 4121 -> 4050 -> 4055 display-name chain, strict row pins, and the 20077 deferral."""
from collections import Counter
from copy import deepcopy

import pytest

from nlp import entity_matcher as em
from scripts.eda import apply_display_name_batch_b_safe_fix as fix

# Every kiệu row the corpus carries that this batch deliberately leaves UNMATCHED:
# 11 sweet-sour, 2 fresh, 3 bare/ambiguous, 1 nước củ kiệu, 1 compound.
DEFERRED_KIEU_PHRASES = (
    'kiệu tươi', 'củ kiệu', 'kiệu', 'nước củ kiệu', 'kiệu ngâm chua',
    'dưa kiệu đã ngâm', 'kiệu chua chẻ làm 4', 'ăn kèm củ kiệu chua',
)
# Bamboo, gourd and pickle siblings that must not move for Batch B.
UNTOUCHED_IDENTITIES = {
    # `măng khô`/`măng tươi` were deferred by Batch B and later repaired by
    # BAMBOO_SHOOT_ALIAS_FIX; bare `măng` remains deferred on 4051.
    'măng tre': '4053', 'măng tre tươi': '4053', 'măng khô': '4051',
    'măng': '4051', 'măng tươi': '4053', 'măng tây': '20033',
    'khổ qua rừng': '4054', 'mướp': '4054', 'mướp hương': '4054', 'mướp nhật bản': '4056',
    'kiệu chua': '20077', 'dưa kiệu': '20077', 'củ kiệu chua ngọt': '20077',
    'hành củ muối': '4120', 'dưa giá đậu xanh': '4119',
}


@pytest.fixture(scope='module')
def reviewed():
    return fix.read_json(fix.REVIEW)


@pytest.fixture(scope='module')
def repaired_catalog(reviewed):
    """Full catalog with the reviewed patches applied; 4055 stays as Batch A left it."""
    rows = deepcopy(fix.read_csv(fix.ROOT / fix.CAT))
    by_code = fix.index(rows, 'code')
    for before in reviewed['catalog_before']:
        by_code[before['code']].update(dict(before, **fix.CATALOG_PATCHES[before['code']]))
    return by_code


@pytest.fixture(scope='module')
def live_rows():
    csv_rows = fix.read_csv(fix.ROOT / fix.DATA / 'recipe_ingredients.csv')
    json_rows = fix.read_json(fix.ROOT / fix.DATA / 'recipe_ingredients.json')
    fix.parity(csv_rows, json_rows)
    return csv_rows


@pytest.fixture(scope='module')
def live_catalog():
    return fix.index(fix.read_csv(fix.ROOT / fix.CAT), 'code')


@pytest.fixture(scope='module')
def live_aliases():
    return fix.read_json(fix.ROOT / fix.ALIASES)


@pytest.fixture(scope='module')
def matcher():
    return em.VietnameseIngredientMatcher()


# --- catalog ---------------------------------------------------------------

@pytest.mark.parametrize('code,name', [(c, p['name_vi']) for c, p in fix.CATALOG_PATCHES.items()])
def test_applied_catalog_display_names(live_catalog, code, name):
    assert live_catalog[code]['name_vi'] == name


def test_applied_catalog_changes_nothing_but_the_display_name(reviewed, live_catalog):
    """Code, name_en, category and every nutrition column are immutable here."""
    assert {r['code'] for r in reviewed['catalog_before']} == {'4050', '4121'}
    for before in reviewed['catalog_before']:
        live = live_catalog[before['code']]
        assert live == dict(before, **fix.CATALOG_PATCHES[before['code']])
        assert live['name_vi'] != before['name_vi']
        for field, value in before.items():
            if field != 'name_vi':
                assert live[field] == value, field


def test_4055_is_untouched_by_batch_b(live_catalog):
    assert '4055' not in fix.CATALOG_PATCHES
    assert live_catalog['4055']['name_vi'] == 'Mướp đắng'


def test_repaired_names_publish_the_reviewed_subphrase_heads(live_catalog):
    """The comma placement is the policy, not cosmetics.

    The matcher indexes normalize_vietnamese_text(name_vi.split(',')[0]) as a
    subphrase retrieval head. 4050's comma is what publishes `măng chua` and
    recovers 545ef564; 4121 stays comma-less so no bare `kiệu` head exists.
    """
    heads = {code: fix.subphrase_head(live_catalog[code]['name_vi']) for code in fix.CATALOG_PATCHES}
    assert heads == fix.EXPECTED_SUBPHRASE_HEADS == {'4050': 'măng chua', '4121': 'kiệu muối'}
    assert fix.subphrase_head('Kiệu, muối') == fix.FORBIDDEN_SUBPHRASE_HEAD  # the rejected form
    assert not any(fix.subphrase_head(r['name_vi']) == fix.FORBIDDEN_SUBPHRASE_HEAD
                   for r in live_catalog.values())


def test_repaired_names_create_no_new_duplicate(live_catalog):
    names = Counter(em.normalize_vietnamese_text(r['name_vi']) for r in live_catalog.values())
    for patch in fix.CATALOG_PATCHES.values():
        assert names[em.normalize_vietnamese_text(patch['name_vi'])] == 1
    assert {n for n, c in names.items() if c > 1} == fix.DEFERRED_DUPLICATE_NAMES


@pytest.mark.parametrize('field,value', [('name_vi', 'Unexpected name'), ('name_en', 'wrong identity'),
                                         ('energy_kcal', '1'), ('carbs_g', '99'),
                                         ('category_vi', 'wrong category')])
def test_catalog_drift_fails_closed(monkeypatch, field, value):
    original = fix.read_csv

    def read(path):
        rows = original(path)
        if path == fix.ROOT / fix.CAT:
            next(r for r in rows if r['code'] == '4050')[field] = value
        return rows
    monkeypatch.setattr(fix, 'read_csv', read)
    monkeypatch.setattr(fix, 'write_csv', lambda *a: pytest.fail('wrote before validation'))
    with pytest.raises(fix.DriftError):
        fix.plan()


# --- aliases ---------------------------------------------------------------

def test_exactly_nine_aliases_are_repointed():
    assert len(fix.ALIAS_PATCHES) == 9
    assert Counter(fix.ALIAS_PATCHES.values()) == {'4055': 6, '4050': 3}


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_PATCHES.items()))
def test_applied_alias_repoints(live_aliases, alias, code):
    assert live_aliases[alias] == code


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_KEEPS.items()))
def test_reviewed_alias_keeps_are_untouched(live_aliases, alias, code):
    assert live_aliases[alias] == code


def test_alias_map_size_and_membership_unchanged(reviewed, live_aliases):
    """Nothing is added and nothing is removed by THIS batch -- nine targets move.

    The live size is 4680, not the 4672 the manifest froze: DISPLAY_NAME_BATCH_C2
    later removed 3 keys and added 5 (4674), and DISPLAY_NAME_BATCH_C1 then removed
    the 2 spinach/kale keys and added 8 mustard-green/napa/kimchi keys. Both figures
    are asserted, so Batch B's own "adds nothing, removes nothing" invariant stays
    exact.
    """
    assert len(live_aliases) == fix.ALIAS_MAP_SIZE == 4684
    assert reviewed['alias_map_size'] == fix.REVIEWED_ALIAS_MAP_SIZE == 4672
    assert set(fix.ALIAS_PATCHES) <= set(live_aliases)


def test_every_alias_on_a_repaired_code_is_reviewed(live_aliases):
    reviewed_on_patched = {k for k, v in fix.ALIAS_KEEPS.items() if v in fix.CATALOG_PATCHES} | \
                          {k for k, v in fix.ALIAS_PATCHES.items() if v in fix.CATALOG_PATCHES}
    assert {k for k, v in live_aliases.items() if v in fix.CATALOG_PATCHES} == reviewed_on_patched


def test_alias_drift_fails_closed(monkeypatch):
    original = fix.read_json

    def read(path):
        result = original(path)
        if path == fix.ROOT / fix.ALIASES:
            result['khổ qua'] = '99999'
        return result
    monkeypatch.setattr(fix, 'read_json', read)
    with pytest.raises(fix.DriftError, match='Alias drift'):
        fix.plan()


def test_alias_removal_fails_closed(monkeypatch):
    original = fix.read_json

    def read(path):
        result = original(path)
        if path == fix.ROOT / fix.ALIASES:
            result.pop('mướp đắng tươi')
        return result
    monkeypatch.setattr(fix, 'read_json', read)
    with pytest.raises(fix.DriftError):
        fix.plan()


# --- rows ------------------------------------------------------------------

def test_every_reviewed_row_matches_its_full_pin(reviewed, repaired_catalog, live_rows):
    live = fix.index(live_rows)
    assert len(reviewed['rows']) == fix.EXPECTED_ROWS == 118
    for pin in reviewed['rows']:
        assert fix.logical(live[pin['before']['id']]) == fix.logical(fix.expected_row(pin, repaired_catalog))


@pytest.mark.parametrize('cohort,spec', sorted(fix.COHORTS.items()))
def test_reviewed_cohort_decisions_and_source_preservation(reviewed, repaired_catalog, cohort, spec):
    source, target, count = spec
    pins = [p for p in reviewed['rows'] if p['cohort'] == cohort]
    assert len(pins) == count
    for pin in pins:
        before, after = pin['before'], fix.expected_row(pin, repaired_catalog)
        mutable = {'master_ingredient_code', 'master_ingredient_name',
                   'match_method', 'match_confidence', *fix.NUTRIENTS}
        # raw_text, cleaned_name, quantity, unit, preparation and weight survive.
        assert {k: v for k, v in before.items() if k not in mutable} == \
               {k: v for k, v in after.items() if k not in mutable}
        assert after['master_ingredient_code'] == target
        assert after['master_ingredient_name'] == repaired_catalog[target]['name_vi']
        if source is None:                                   # the reviewed recovery
            assert before['match_method'] == 'UNMATCHED'
            assert after['match_method'] == fix.RECOVERY_MATCH['method']
            assert after['match_confidence'] == str(fix.RECOVERY_MATCH['confidence'])
        else:
            assert before['master_ingredient_code'] == source
            assert after['match_method'] == before['match_method'] == 'PRESET_ALIAS_MATCH'
            assert after['match_confidence'] == before['match_confidence'] == '0.98'


def test_sixty_one_sour_bamboo_rows_land_on_4050(reviewed, live_rows, live_catalog):
    pins = [p for p in reviewed['rows'] if p['cohort'] == 'sour_bamboo_4121_to_4050']
    assert len(pins) == 61
    assert {p['before']['cleaned_name'] for p in pins} == {'măng chua'}
    live = fix.index(live_rows)
    for pin in pins:
        row = live[pin['before']['id']]
        assert row['master_ingredient_code'] == '4050'
        assert row['master_ingredient_name'] == live_catalog['4050']['name_vi'] == 'Măng chua, măng tre'
        assert row['raw_text'] == pin['before']['raw_text']
        assert row['estimated_weight_g'] == pin['before']['estimated_weight_g']


def test_fifty_six_bitter_gourd_rows_land_on_4055(reviewed, live_rows, live_catalog):
    pins = [p for p in reviewed['rows'] if p['cohort'] == 'bitter_gourd_4050_to_4055']
    assert len(pins) == 56
    # The approved cohort, not "everything that looks like a bitter gourd".
    assert {p['before']['cleaned_name'] for p in pins} == {'khổ qua', 'khổ qua bào', 'ăn kèm khổ qua'}
    assert not any('rừng' in p['before']['raw_text'].lower() for p in pins)
    live = fix.index(live_rows)
    for pin in pins:
        row = live[pin['before']['id']]
        assert row['master_ingredient_code'] == '4055'
        assert row['master_ingredient_name'] == live_catalog['4055']['name_vi'] == 'Mướp đắng'


def test_the_reviewed_recovery(reviewed, live_rows, live_catalog):
    pin = next(p for p in reviewed['rows'] if p['before']['id'] == fix.RECOVERY_ROW_ID)
    row = fix.index(live_rows)[fix.RECOVERY_ROW_ID]
    assert pin['before']['match_method'] == 'UNMATCHED'
    assert row['raw_text'] == pin['before']['raw_text'] == fix.RECOVERY_RAW_TEXT
    assert row['cleaned_name'] == pin['before']['cleaned_name'] == fix.RECOVERY_QUERY
    assert row['master_ingredient_code'] == '4050'
    assert row['master_ingredient_name'] == live_catalog['4050']['name_vi']
    assert row['match_method'] == fix.RECOVERY_MATCH['method'] == 'SUBPHRASE_CATALOG_MATCH'
    assert row['match_confidence'] == '0.95'
    assert row['estimated_weight_g'] == pin['before']['estimated_weight_g'] == '500.0'
    assert row['required_quantity'] == pin['before']['required_quantity']
    assert row['unit'] == pin['before']['unit'] and row['unit_vi'] == pin['before']['unit_vi']
    assert {f: row[f] for f in fix.NUTRIENTS} == \
           {'calories': '140.0', 'protein_g': '7.0', 'fat_g': '', 'carbs_g': '27.5'}


def test_rows_are_pinned_by_id_not_selected_by_code(reviewed, live_rows):
    """Each source population must be exhausted by explicit row ids."""
    pinned = {p['before']['id'] for p in reviewed['rows']}
    assert len(pinned) == 118
    for cohort in fix.COHORTS:
        ids = [p['before']['id'] for p in reviewed['rows'] if p['cohort'] == cohort]
        assert len(set(ids)) == len(ids)
    assert not [r for r in live_rows if r['master_ingredient_code'] == '4121']


@pytest.mark.parametrize('code,count', sorted(fix.EXPECTED_POPULATIONS.items()))
def test_final_populations(live_rows, code, count):
    if code == 'UNMATCHED':
        actual = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
        assert actual == sum(1 for r in live_rows if not (r['master_ingredient_code'] or '').strip())
    else:
        actual = sum(1 for r in live_rows if r['master_ingredient_code'] == code)
    assert actual == count


def test_4050_population_decomposes_into_the_two_approved_sources(reviewed, live_rows):
    on_4050 = {r['id'] for r in live_rows if r['master_ingredient_code'] == '4050'}
    bamboo = {p['before']['id'] for p in reviewed['rows'] if p['cohort'] == 'sour_bamboo_4121_to_4050'}
    assert on_4050 == bamboo | {fix.RECOVERY_ROW_ID}
    assert len(on_4050) == 62


def test_4055_population_is_batch_a_plus_the_approved_cohort(reviewed, live_rows):
    on_4055 = {r['id'] for r in live_rows if r['master_ingredient_code'] == '4055'}
    gourd = {p['before']['id'] for p in reviewed['rows'] if p['cohort'] == 'bitter_gourd_4050_to_4055'}
    # d6f83055 is Batch A's single recovered row and is not re-touched here.
    assert on_4055 - gourd == {'d6f83055-4f09-4e24-8b28-b5e99bab7a52'}
    assert len(on_4055) == 57


def test_no_row_outside_the_reviewed_set_changed_identity(reviewed, live_rows):
    """Every row on a Batch B code is either pinned or the Batch A carry-over."""
    pinned = {p['before']['id'] for p in reviewed['rows']}
    touched = {r['id'] for r in live_rows if r['master_ingredient_code'] in ('4050', '4055', '4121')}
    assert touched - pinned == {'d6f83055-4f09-4e24-8b28-b5e99bab7a52'}


def test_repaired_rows_carry_no_stale_display_name(reviewed, live_rows, live_catalog):
    pinned = {p['before']['id'] for p in reviewed['rows']}
    rows = [r for r in live_rows if r['id'] in pinned]
    assert len(rows) == 118
    assert not [r['id'] for r in rows
                if r['master_ingredient_name'] != live_catalog[r['master_ingredient_code']]['name_vi']]


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


# --- nutrition -------------------------------------------------------------

def test_reviewed_nutrition_delta_and_null_transitions(reviewed, repaired_catalog):
    ordered = sorted(reviewed['rows'], key=lambda p: p['before']['id'])
    report = fix.nutrient_report([p['before'] for p in ordered],
                                 [fix.expected_row(p, repaired_catalog) for p in ordered])
    assert {f: report[f]['known_sum_delta'] for f in fix.NUTRIENTS} == fix.EXPECTED_NUTRITION_DELTA
    assert {f: (report[f]['before_null_count'], report[f]['after_null_count'])
            for f in fix.NUTRIENTS} == fix.EXPECTED_NULL_TRANSITIONS


def test_the_117_identity_remaps_make_no_null_transition(reviewed, repaired_catalog):
    ordered = sorted((p for p in reviewed['rows'] if p['before']['id'] != fix.RECOVERY_ROW_ID),
                     key=lambda p: p['before']['id'])
    assert len(ordered) == 117
    report = fix.nutrient_report([p['before'] for p in ordered],
                                 [fix.expected_row(p, repaired_catalog) for p in ordered])
    assert {f: report[f]['known_sum_delta'] for f in fix.NUTRIENTS} == fix.EXPECTED_BASE_NUTRITION_DELTA
    assert {f: (report[f]['before_null_count'], report[f]['after_null_count'])
            for f in fix.NUTRIENTS} == fix.EXPECTED_BASE_NULL_TRANSITIONS
    for field in fix.NUTRIENTS:
        assert report[field]['value_to_null'] == report[field]['null_to_value'] == 0, field


def test_recovery_supplies_every_null_to_value_transition(reviewed, repaired_catalog):
    pin = next(p for p in reviewed['rows'] if p['before']['id'] == fix.RECOVERY_ROW_ID)
    after = fix.expected_row(pin, repaired_catalog)
    for field in ('calories', 'protein_g', 'carbs_g'):
        assert pin['before'][field] == ''
        assert after[field] not in (None, '')
    assert pin['before']['fat_g'] == '' and after['fat_g'] is None   # null -> null


def test_missing_fat_is_never_coerced_to_zero(reviewed, repaired_catalog, live_rows, live_catalog):
    """Neither 4050 nor 4055 carries a fat value, so all 118 rows keep a null."""
    assert live_catalog['4050']['fat_g'] == live_catalog['4055']['fat_g'] == ''
    for pin in reviewed['rows']:
        assert fix.expected_row(pin, repaired_catalog)['fat_g'] is None
    pinned = {p['before']['id'] for p in reviewed['rows']}
    assert all(r['fat_g'] == '' for r in live_rows if r['id'] in pinned)


def test_corpus_null_counts(live_rows):
    assert {f: sum(1 for r in live_rows if r[f] == '') for f in fix.NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS


# --- recipes ---------------------------------------------------------------

def test_recipe_radius_is_measured_not_assumed(reviewed):
    recipes = {p['before']['recipe_id'] for p in reviewed['rows']}
    base = {p['before']['recipe_id'] for p in reviewed['rows'] if p['before']['id'] != fix.RECOVERY_ROW_ID}
    assert len(base) == 109                     # the previously measured 117-row radius
    assert len(recipes) == fix.EXPECTED_RECIPES == 110
    assert fix.RECOVERY_RECIPE_ID not in base   # the recovery adds a genuinely new recipe


def test_recipe_rollups_agree_with_the_repaired_ingredient_rows(live_rows):
    recipes_json = fix.read_json(fix.ROOT / fix.DATA / 'recipes.json')
    fix.parity(fix.read_csv(fix.ROOT / fix.DATA / 'recipes.csv'), recipes_json)
    rollups = fix.recompute_recipe_rollups(live_rows)
    records = fix.index(recipes_json)
    for rid in {r['recipe_id'] for r in live_rows if r['master_ingredient_code'] in ('4050', '4055')}:
        for key, value in fix._new_totals(rollups[rid]).items():
            assert records[rid][key] == value, (rid, key)


def test_recovery_recipe_status_is_recomputed_not_forced(live_rows):
    recipes = fix.index(fix.read_json(fix.ROOT / fix.DATA / 'recipes.json'))
    status = fix.nutrition_status(live_rows, list(recipes.values()))
    label, missing = status[fix.RECOVERY_RECIPE_ID]
    assert missing == 1                     # was 2 of 11 before the recovery
    assert label == 'PARTIAL'               # 1/11 and 2/11 both sit under the 0.3 threshold
    assert recipes[fix.RECOVERY_RECIPE_ID]['missing_nutrition_count'] == missing
    assert recipes[fix.RECOVERY_RECIPE_ID]['nutrition_status'] == label


def test_no_recipe_status_label_transition_is_expected():
    assert fix.EXPECTED_STATUS_LABEL_TRANSITIONS == {}
    assert fix.EXPECTED_MISSING_COUNT_RECIPES == {fix.RECOVERY_RECIPE_ID}


# --- matcher ---------------------------------------------------------------

@pytest.mark.parametrize('query,code', sorted(fix.PROBES.items()))
def test_real_single_and_batch_matches(matcher, query, code):
    for result in (matcher.match(query, raw_context=query),
                   matcher.match_batch([query], raw_contexts=[query])[0]):
        assert (result['matched_item'] or {}).get('code') == code


def test_recovery_verdict_is_reproduced_by_the_real_matcher(matcher):
    """545ef564's method and confidence are measured, not hard-coded."""
    for result in (matcher.match(fix.RECOVERY_QUERY, raw_context=fix.RECOVERY_RAW_TEXT),
                   matcher.match_batch([fix.RECOVERY_QUERY], raw_contexts=[fix.RECOVERY_RAW_TEXT])[0]):
        assert result['matched_item']['code'] == fix.RECOVERY_MATCH['code']
        assert result['method'] == fix.RECOVERY_MATCH['method']
        assert result['confidence'] == fix.RECOVERY_MATCH['confidence']


@pytest.mark.parametrize('query,code', sorted(UNTOUCHED_IDENTITIES.items()))
def test_sibling_identities_did_not_move(matcher, query, code):
    for result in (matcher.match(query, raw_context=query),
                   matcher.match_batch([query], raw_contexts=[query])[0]):
        assert (result['matched_item'] or {}).get('code') == code


@pytest.mark.parametrize('query,pinned', sorted(fix.KNOWN_ROUTE_DIVERGENCE.items()))
def test_pre_existing_route_divergence_is_not_fixed(matcher, query, pinned):
    """Out of scope, and pinned so the bare-kiệu single-route shift stays visible."""
    single = (matcher.match(query, raw_context=query)['matched_item'] or {}).get('code')
    batched = (matcher.match_batch([query], raw_contexts=[query])[0]['matched_item'] or {}).get('code')
    assert single == pinned['single_after']
    assert batched == pinned['batch']
    assert single != batched


def test_production_shape_replay_reproduces_every_repaired_row(matcher, reviewed, live_rows):
    """match_batch(cleaned_name, raw_contexts=raw_text), exactly as the pipeline calls it."""
    pins = {p['before']['id']: p for p in reviewed['rows']}
    rows = [r for r in live_rows if r['id'] in pins]
    assert len(rows) == 118
    results = matcher.match_batch([r['cleaned_name'] for r in rows],
                                  raw_contexts=[r['raw_text'] for r in rows])
    for row, result in zip(rows, results):
        assert (result['matched_item'] or {}).get('code') == pins[row['id']]['target_code'], row['raw_text']
        assert result['matched_item']['code'] == row['master_ingredient_code']


def test_qwen_rule_sets_are_unchanged_by_the_renames(live_catalog):
    """No dormant rule wakes up and no active rule changes target."""
    from nlp.qwen_matching import build_mapper_rules
    active, disabled = build_mapper_rules(live_catalog)
    assert (len(active), len(disabled)) == (29, 20)
    assert not [r for r in active if r[1] in fix.CATALOG_PATCHES]
    assert not [r for r in disabled if r[1] in fix.CATALOG_PATCHES]


# The one nlp module a later batch legitimately edited, and why. Batch B's claim
# is that IT added no guard and changed no matcher code; it is not a claim that
# no other batch may ever touch the package. DISPLAY_NAME_BATCH_C1 hardening
# added a reviewed catalog-gap exclusion to the Qwen recovery guard in
# nlp/qwen_matching.py -- to stop a future Qwen pass restating C1's reviewed
# dried-salted-napa clear as a wrong match -- and nlp/entity_matcher.py, the
# matcher this test is actually about, is still byte-identical to HEAD.
# Named explicitly rather than widening the sweep, so any OTHER nlp edit still
# fails this test closed.
C1_HARDENED_NLP_MODULE = 'nlp/qwen_matching.py'


def test_no_guard_is_added_and_no_matcher_code_changes_for_batch_b():
    """Batch B is a pure data repair: it adds no guard and edits no matcher module.

    Stated against HEAD rather than a hand-listed guard set, so a guard added by
    any other work cannot quietly satisfy it. The single named exception above is
    C1's, is asserted by path, and does not touch the matcher.
    """
    import subprocess
    changed = subprocess.run(['git', 'status', '--porcelain', '--', 'nlp'],
                             cwd=fix.ROOT, capture_output=True, text=True, check=True).stdout
    touched = {line[3:].strip().replace('\\', '/') for line in changed.splitlines() if line.strip()}
    assert touched <= {C1_HARDENED_NLP_MODULE}, touched
    matcher_changed = subprocess.run(
        ['git', 'status', '--porcelain', '--', 'nlp/entity_matcher.py'],
        cwd=fix.ROOT, capture_output=True, text=True, check=True).stdout
    assert matcher_changed.strip() == ''
    head = subprocess.run(['git', 'show', 'HEAD:nlp/entity_matcher.py'],
                          cwd=fix.ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    live = {name for name in dir(em) if name.endswith('_GUARD_REASON')}
    assert live == {name for name in live if f'{name} =' in head}


def test_batch_a_coriander_guard_still_holds(matcher):
    for phrase in ('hạt rau mùi', 'bột rau mùi', 'coriander seeds'):
        result = matcher.match(phrase, raw_context=phrase)
        assert result['method'] == 'UNMATCHED'
        assert result['guard'] == em.CORIANDER_SEED_POWDER_GUARD_REASON


# --- 20077 deferral --------------------------------------------------------

def test_20077_identity_rows_and_aliases_are_untouched(live_rows, live_aliases, live_catalog):
    state = fix.deferred_kieu_state(live_rows, live_aliases, live_catalog)
    assert state['rows_on_20077'] == 29
    assert len(state['aliases_on_20077']) == 11
    assert live_catalog['20077']['name_vi'] == 'Củ kiệu muối (Dưa kiệu chua ngọt)'


def test_no_20077_alias_was_repointed(live_aliases):
    assert not set(fix.ALIAS_PATCHES) & {k for k, v in live_aliases.items() if v == '20077'}


def test_20077_rows_keep_their_own_nutrition(live_rows, live_catalog):
    """Nothing inherited 4121's profile: 20077 is 55 kcal/100 g, 4121 is 29."""
    assert live_catalog['20077']['energy_kcal'] == '55'
    assert live_catalog['4121']['energy_kcal'] == '29'
    for row in (r for r in live_rows if r['master_ingredient_code'] == '20077'):
        expected = round(55.0 * float(row['estimated_weight_g']) / 100.0, 1)
        assert float(row['calories']) == expected


def test_deferred_kieu_rows_remain_unmatched(live_rows):
    deferred = [r for r in live_rows if r['match_method'] == 'UNMATCHED'
                and 'kiệu' in em.normalize_vietnamese_text(f"{r['raw_text']} {r['cleaned_name']}")]
    assert len(deferred) == fix.EXPECTED_UNMATCHED_KIEU_ROWS == 18
    for row in deferred:
        assert row['master_ingredient_code'] == '' and row['master_ingredient_name'] == ''
        assert row['match_confidence'] == ''
        assert all(row[f] == '' for f in fix.NUTRIENTS)


@pytest.mark.parametrize('phrase', DEFERRED_KIEU_PHRASES)
def test_fresh_and_ambiguous_kieu_rows_were_not_recovered(live_rows, phrase):
    rows = [r for r in live_rows if r['cleaned_name'] == phrase]
    if rows:
        assert all(r['match_method'] == 'UNMATCHED' for r in rows), phrase


def test_deferral_is_recorded_in_the_applied_report():
    report = fix.read_json(fix.OUT / 'applied_fix.json')
    deferral = report[fix.DEFERRAL_KEY]
    assert deferral['status'] == 'DEFERRED_NEEDS_DOMAIN_REVIEW'
    for key in ('4121_raw_authority', '20077_authored_provenance', 'preparation_ambiguity',
                'nutrition_difference', 'reason_no_automatic_merge'):
        assert deferral[key].strip()
    assert deferral['measured']['rows_on_20077'] == 29
    assert len(deferral['measured']['aliases_on_20077']) == 11


# --- blast radius and idempotence -----------------------------------------

def test_interim_data_is_out_of_scope(reviewed):
    """Batch B touches processed data only; data/interim is historical."""
    import subprocess
    changed = subprocess.run(['git', 'status', '--porcelain', '--', 'data/interim'],
                             cwd=fix.ROOT, capture_output=True, text=True, check=True).stdout
    assert changed.strip() == ''


def test_canonical_radius_is_pinned():
    report = fix.read_json(fix.OUT / 'applied_fix.json')
    assert {k: v['changed_count'] for k, v in report['canonical'].items()} == fix.EXPECTED_CANONICAL
    assert report['canonical_id_drift'] == 0
    assert report['representative_drift'] == 0


def test_plan_is_idempotent_and_reports_nothing_pending():
    assert fix.plan()[2]['rows_pending'] == 0
