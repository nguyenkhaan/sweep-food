"""Repaired display identities, strict row pins, and the coriander seed/powder guard."""
from collections import Counter
from copy import deepcopy

import pytest

from nlp import entity_matcher as em
from scripts.eda import apply_display_name_batch_a_safe_fix as fix

# Every coriander seed/powder spelling the audit found in the corpus. All 20 rows
# must stay UNMATCHED; only the four that carried a code changed state.
SEED_POWDER_PHRASES = (
    'hạt rau mùi', 'bột rau mùi', 'bột và hạt rau mùi corriander', 'bột và hạt rau mùi',
    'hạt ngò', 'hạt ngò khô', 'hạt ngò tươi', 'bột hạt ngò', 'bột ngò ta', 'bột ngò',
    'hột ngò', 'hạt mùi', 'hạt mùi rang', 'hạt mùi hoặc rễ mùi già',
    'coriander seed', 'coriander seeds', 'coriander powder', 'corriander seeds',
)
# Leaf, root, stem and garnish uses -- none of these may ever be guarded.
CORIANDER_LEAF_PHRASES = (
    'rau mùi', 'ngò rí', 'ngò', 'rễ ngò', 'gốc ngò rí', 'lá ngò', 'lá ngò rí',
    'rau nêm ngò rí', 'rễ và gốc rau mùi', 'rau mùi thái nhỏ', 'ngò rí cắt nhuyễn',
    'ngò gai', 'mùi tàu', 'lá ngò gai', 'rau mùi tàu',
)
# Parsley is a different identity and is deliberately out of this guard's scope.
PARSLEY_PHRASES = ('ngò tây', 'mùi tây', 'parsley', 'bột mùi tây', 'rau ngò tây', 'lá ngò tây')
# Unrelated seed/powder spices that must keep resolving.
OTHER_SPICE_PHRASES = (
    'hạt tiêu', 'hạt nêm', 'hạt sen', 'hạt điều', 'hạt ý dĩ', 'hạt mắc khén', 'hạt chia',
    'ngô hạt', 'bột ngọt', 'bột ngô', 'bột canh', 'bột nghệ', 'bột cà ri', 'bột quế',
    'bột năng', 'bột mì', 'bột gạo', 'bột chiên giòn', 'bột ớt paprika', 'bột hạt điều',
)


@pytest.fixture(scope='module')
def reviewed():
    return fix.read_json(fix.REVIEW)


@pytest.fixture(scope='module')
def repaired_catalog(reviewed):
    """Full catalog with the reviewed patches applied; targets live outside the pins."""
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


@pytest.fixture
def matcher():
    return em.VietnameseIngredientMatcher()


# --- catalog ---------------------------------------------------------------

@pytest.mark.parametrize('code,name', [(c, p['name_vi']) for c, p in fix.CATALOG_PATCHES.items()])
def test_applied_catalog_display_names(live_catalog, code, name):
    assert live_catalog[code]['name_vi'] == name


def test_applied_catalog_changes_nothing_but_the_display_name(reviewed, live_catalog):
    for before in reviewed['catalog_before']:
        assert live_catalog[before['code']] == dict(before, **fix.CATALOG_PATCHES[before['code']])
        assert live_catalog[before['code']]['name_en'] == before['name_en']


def test_repaired_names_do_not_collide_and_resolve_the_tom_dong_pair(live_catalog):
    names = Counter(em.normalize_vietnamese_text(r['name_vi']) for r in live_catalog.values())
    for patch in fix.CATALOG_PATCHES.values():
        assert names[em.normalize_vietnamese_text(patch['name_vi'])] == 1
    assert names['tôm đồng'] == 1  # 8050 vacated it; only 8052 keeps it.


@pytest.mark.parametrize('field,value', [('name_vi', 'Unexpected name'), ('name_en', 'wrong identity'),
                                         ('energy_kcal', '1'), ('category_vi', 'wrong category')])
def test_catalog_drift_fails_closed(monkeypatch, field, value):
    original = fix.read_csv

    def read(path):
        rows = original(path)
        if path == fix.ROOT / fix.CAT:
            next(r for r in rows if r['code'] == '4073')[field] = value
        return rows
    monkeypatch.setattr(fix, 'read_csv', read)
    monkeypatch.setattr(fix, 'write_csv', lambda *a: pytest.fail('wrote before validation'))
    with pytest.raises(fix.DriftError):
        fix.plan()


# --- aliases ---------------------------------------------------------------

@pytest.mark.parametrize('alias,code', sorted((k, v) for k, v in fix.ALIAS_PATCHES.items() if v))
def test_applied_alias_repoints(live_aliases, alias, code):
    assert live_aliases[alias] == code


@pytest.mark.parametrize('alias', [k for k, v in fix.ALIAS_PATCHES.items() if v is None])
def test_seed_powder_aliases_removed(live_aliases, alias):
    assert alias not in live_aliases


@pytest.mark.parametrize('alias,code', sorted(fix.ALIAS_KEEPS.items()))
def test_authoritative_raw_aliases_kept_on_repaired_codes(live_aliases, alias, code):
    assert live_aliases[alias] == code


@pytest.mark.parametrize('alias,code', sorted(fix.UNTOUCHED_ALIASES.items()))
def test_deferred_broad_aliases_not_modified(live_aliases, alias, code):
    """The broad khô / đồng aliases remain deferred; Batch A never touched them."""
    assert live_aliases[alias] == code


@pytest.mark.parametrize('alias,code', sorted(fix.BATCH_B_ALIASES_ON_REPAIRED_CODES.items()))
def test_batch_b_repointed_the_bitter_gourd_aliases_onto_4055(live_aliases, alias, code):
    """Deferred by Batch A on 4050, resolved by Batch B onto the repaired 4055."""
    assert live_aliases[alias] == code


def test_no_alias_still_points_at_a_repaired_display_identity(live_aliases):
    reviewed = set(fix.ALIAS_KEEPS) | set(fix.BATCH_B_ALIASES_ON_REPAIRED_CODES)
    stale = {k: v for k, v in live_aliases.items() if v in fix.CATALOG_PATCHES and k not in reviewed}
    assert stale == {}


def test_alias_drift_fails_closed(monkeypatch):
    original = fix.read_json

    def read(path):
        result = original(path)
        if path == fix.ROOT / fix.ALIASES:
            result['ngò gai'] = '99999'
        return result
    monkeypatch.setattr(fix, 'read_json', read)
    with pytest.raises(fix.DriftError, match='Alias drift'):
        fix.plan()


# --- rows ------------------------------------------------------------------

def test_every_reviewed_row_matches_its_full_pin(reviewed, repaired_catalog, live_rows):
    live = fix.index(live_rows)
    assert len(reviewed['rows']) == fix.EXPECTED_ROWS
    for pin in reviewed['rows']:
        assert fix.logical(live[pin['before']['id']]) == fix.logical(fix.expected_row(pin, repaired_catalog))


@pytest.mark.parametrize('cohort,spec', sorted(fix.COHORTS.items()))
def test_reviewed_cohort_decisions_and_source_preservation(reviewed, repaired_catalog, cohort, spec):
    source, target, count = spec
    pins = [p for p in reviewed['rows'] if p['cohort'] == cohort]
    assert len(pins) == count
    for pin in pins:
        before, after = pin['before'], fix.expected_row(pin, repaired_catalog)
        if source is not None:
            assert before['master_ingredient_code'] == source
        mutable = set(fix.NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name',
                                        'match_method', 'match_confidence'}
        # raw_text, cleaned_name, quantity, unit, preparation and weight survive.
        assert {k: v for k, v in before.items() if k not in mutable} == \
               {k: v for k, v in after.items() if k not in mutable}
        if target is None:
            assert after['match_method'] == 'UNMATCHED'
            assert all(after[f] is None for f in mutable - {'match_method'})
        else:
            assert after['master_ingredient_code'] == target
            assert after['master_ingredient_name'] == repaired_catalog[target]['name_vi'] \
                if target in repaired_catalog else True
            assert after['match_method'] == before['match_method']


def test_4073_and_4055_split_by_semantics_not_by_source_code(reviewed):
    """Both displaced codes feed several targets; neither is a blanket remap."""
    split = Counter((p['before']['master_ingredient_code'], p['target_code'])
                    for p in reviewed['rows']
                    if p['before']['master_ingredient_code'] in ('4073', '4055'))
    assert split == {('4073', '4081'): 785, ('4073', '4082'): 43, ('4073', '20036'): 2,
                     ('4073', None): 1, ('4055', '4082'): 215, ('4055', '4081'): 21}


def test_bitter_gourd_recovery_row_is_intact(live_rows, live_catalog):
    """Batch A's single recovery. Batch B added the other 56 and did not re-touch it."""
    row = fix.index(live_rows)[fix.BITTER_GOURD_ROW_ID]
    assert row['master_ingredient_code'] == '4055'
    assert row['master_ingredient_name'] == live_catalog['4055']['name_vi'] == 'Mướp đắng'
    assert row['raw_text'] == 'Mướp đắng 1 trái'


def test_the_khô_qua_rows_were_moved_to_4055_by_batch_b(live_rows):
    """Batch A deferred these 56 rows on 4050; Batch B moved them and added one recovery."""
    assert sum(1 for r in live_rows if r['master_ingredient_code'] == '4055') == 57
    assert sum(1 for r in live_rows if r['master_ingredient_code'] == '4050') == 62


def test_eight_tep_kho_rows_recovered_onto_8050(reviewed, live_rows, live_catalog):
    pinned = {p['before']['id'] for p in reviewed['rows'] if p['cohort'] == 'tep_kho_5029_to_8050'}
    on_8050 = [r for r in live_rows if r['master_ingredient_code'] == '8050']
    assert len(pinned) == 8 and {r['id'] for r in on_8050} == pinned
    assert all(r['master_ingredient_name'] == live_catalog['8050']['name_vi'] == 'Tép khô' for r in on_8050)
    assert all('tép khô' in r['raw_text'].lower() for r in on_8050)
    assert sum(1 for r in live_rows if r['master_ingredient_code'] == '5029') == 2


@pytest.mark.parametrize('code,count', sorted(fix.EXPECTED_POPULATIONS.items()))
def test_final_populations(live_rows, code, count):
    if code == 'UNMATCHED':
        actual = sum(1 for r in live_rows if r['match_method'] == 'UNMATCHED')
        assert actual == sum(1 for r in live_rows if not (r['master_ingredient_code'] or '').strip())
    else:
        actual = sum(1 for r in live_rows if r['master_ingredient_code'] == code)
    assert actual == count


@pytest.mark.parametrize('row_id', fix.SEED_POWDER_ROW_IDS)
def test_cleared_rows_honour_the_unmatched_contract(live_rows, reviewed, row_id):
    row = fix.index(live_rows)[row_id]
    before = next(p['before'] for p in reviewed['rows'] if p['before']['id'] == row_id)
    assert row['match_method'] == 'UNMATCHED'
    for field in ('master_ingredient_code', 'master_ingredient_name', 'match_confidence', *fix.NUTRIENTS):
        assert row[field] == '', field
    for field in ('raw_text', 'cleaned_name', 'required_quantity', 'unit_vi', 'unit',
                  'preparation_note', 'estimated_weight_g'):
        assert row[field] == before[field], field


def test_no_batch_a_row_or_code_carries_a_stale_display_name(reviewed, live_rows, live_catalog):
    """Every repaired row, and every row on a repaired code, shows the live name."""
    pinned = {p['before']['id'] for p in reviewed['rows']}
    in_scope = [r for r in live_rows
                if (r['id'] in pinned or r['master_ingredient_code'] in fix.CATALOG_PATCHES)
                and (r['master_ingredient_code'] or '').strip()]
    assert len(in_scope) >= fix.EXPECTED_ROWS - len(fix.SEED_POWDER_ROW_IDS)
    stale = {r['id'] for r in in_scope
             if r['master_ingredient_name'] != live_catalog[r['master_ingredient_code']]['name_vi']}
    assert stale == set()


def test_corpus_wide_stale_display_names_remain_the_measured_deferral(live_rows, live_catalog):
    """Batch A repaired four identities, not the whole display-name family.

    417 rows elsewhere still carry a master_ingredient_name that disagrees with
    their code's live name_vi (96 on 4019, 57 on 10015, 43 on 13018, 35 on 4081
    ...), and 39 rows sit on codes 5074/13038 which are not in the catalog at
    all. Both are reviewed deferrals, pinned here so a later batch has a
    baseline and so this fix cannot silently widen them.

    The baseline was 433 when Batch A landed. DISPLAY_NAME_BATCH_C2 narrowed it
    by exactly 16: every QWEN-sourced row on 4010 stored `Cải bắp` while the
    catalog published `Cần tây`, and C2 repaired the catalog to `Cải bắp trắng`
    and refreshed, cleared or moved all 16.

    DISPLAY_NAME_BATCH_C1 then narrowed it by exactly 30 more, 433 -> 417 -> 387.
    All 22 QWEN-sourced rows on 4016 stored `Cải bẹ trắng (cải thìa/thảo)` while
    the catalog published `Dưa chuột (dưa leo)`; C1 repaired the catalog to
    `Cải xanh` and refreshed, cleared or moved every one of them. Eight of the 14
    rows on 4015 storing `Cải bẹ xanh` against a live `Cải thìa (cải trắng)` also
    left, five onto the repaired 4016 and three cleared; the remaining six are the
    unresolved 4015/4135 bok-choy duplicate and stay deferred. The deferral only
    ever shrinks here, so the assertion is still exact and nothing was weakened.
    """
    linked = [r for r in live_rows if (r['master_ingredient_code'] or '').strip()]
    dangling = [r for r in linked if r['master_ingredient_code'] not in live_catalog]
    assert Counter(r['master_ingredient_code'] for r in dangling) == {'13038': 32, '5074': 7}
    stale = [r for r in linked if r['master_ingredient_code'] in live_catalog
             and r['master_ingredient_name'] != live_catalog[r['master_ingredient_code']]['name_vi']]
    assert len(stale) == 387
    assert not any(r['master_ingredient_code'] in fix.CATALOG_PATCHES for r in stale)


def test_target_populations_decompose_into_pins_plus_untouched_rows(reviewed, live_rows):
    """Nothing outside the reviewed set arrived on, or left, a Batch A target."""
    pins = {p['before']['id']: p for p in reviewed['rows']}
    for target in ('4081', '4082', '20036', '5046', '8052'):
        live_ids = {r['id'] for r in live_rows if r['master_ingredient_code'] == target}
        arrived = {rid for rid, p in pins.items() if p['target_code'] == target}
        left = {rid for rid, p in pins.items() if p['before']['master_ingredient_code'] == target}
        assert arrived <= live_ids
        assert not left & live_ids
        assert len(live_ids - arrived) == fix.EXPECTED_POPULATIONS[target] - len(arrived)


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


def test_corpus_null_counts_and_no_zero_coercion(live_rows):
    assert {f: sum(1 for r in live_rows if r[f] == '') for f in fix.NUTRIENTS} == fix.EXPECTED_CORPUS_NULLS
    on_5046 = [r for r in live_rows if r['master_ingredient_code'] == '5046']
    assert all(r['fat_g'] == '' for r in on_5046)          # 5046 has no fat value.
    on_8052 = [r for r in live_rows if r['master_ingredient_code'] == '8052']
    assert all(r['carbs_g'] == '' for r in on_8052)        # 8052 has no carbs value.


def test_recipe_rollups_and_the_single_status_transition():
    recipes = fix.index(fix.read_json(fix.ROOT / fix.DATA / 'recipes.json'))
    fix.parity(fix.read_csv(fix.ROOT / fix.DATA / 'recipes.csv'), list(recipes.values()))
    assert recipes[fix.STATUS_TRANSITION_RECIPE]['nutrition_status'] == 'PARTIAL'
    assert recipes[fix.STATUS_TRANSITION_RECIPE]['missing_nutrition_count'] == 1


# --- matcher ---------------------------------------------------------------

@pytest.mark.parametrize('query,code', fix.PROBES.items())
def test_real_single_and_batch_matches(matcher, query, code):
    for result in (matcher.match(query, raw_context=query),
                   matcher.match_batch([query], raw_contexts=[query])[0]):
        assert (result['matched_item'] or {}).get('code') == code


@pytest.mark.parametrize('phrase', SEED_POWDER_PHRASES)
def test_seed_powder_is_unmatched_on_both_routes(matcher, monkeypatch, phrase):
    monkeypatch.setattr(matcher, '_init_model', lambda: pytest.fail('seed/powder reached neural'))
    single = matcher.match(phrase, raw_context=phrase)
    batched = matcher.match_batch([phrase], raw_contexts=[phrase])[0]
    for result in (single, batched):
        assert result['method'] == 'UNMATCHED'
        assert not result['matched_item']
        assert result['confidence'] is None
        assert result['guard'] == em.CORIANDER_SEED_POWDER_GUARD_REASON
    assert single == batched          # match()/match_batch() parity.


def test_guard_survives_a_reintroduced_alias_and_the_subphrase_head(matcher, monkeypatch):
    """Removal alone reaches SUBPHRASE 4081; the guard must outrank every route."""
    monkeypatch.setattr(matcher, '_init_model', lambda: pytest.fail('seed/powder reached neural'))
    for phrase in ('bột rau mùi', 'hạt rau mùi'):
        matcher.alias_dict[em.normalize_vietnamese_text(phrase)] = \
            next(i for i, r in enumerate(matcher.catalog) if r['code'] == '4081')
        for result in (matcher.match(phrase), matcher.match_batch([phrase])[0]):
            assert result['method'] == 'UNMATCHED'


def test_guard_reads_raw_context_not_only_the_cleaned_name(matcher):
    result = matcher.match('ngò', raw_context='Bột và hạt rau mùi Corriander 1 muỗng cà phê')
    assert result['method'] == 'UNMATCHED'
    assert result['guard'] == em.CORIANDER_SEED_POWDER_GUARD_REASON


@pytest.mark.parametrize('phrase', CORIANDER_LEAF_PHRASES + PARSLEY_PHRASES + OTHER_SPICE_PHRASES)
def test_guard_never_blocks_leaf_parsley_or_unrelated_spices(matcher, phrase):
    assert not em.is_coriander_seed_powder_text(phrase)
    for result in (matcher.match(phrase, raw_context=phrase),
                   matcher.match_batch([phrase], raw_contexts=[phrase])[0]):
        assert result['method'] != 'UNMATCHED', phrase
        assert result['matched_item']


@pytest.mark.parametrize('phrase,code', [('rau mùi', '4081'), ('ngò rí', '4081'), ('rễ ngò', '4081'),
                                         ('gốc ngò rí', '4081'), ('ngò gai', '4082'), ('mùi tàu', '4082'),
                                         ('ngò tây', '20036'), ('mùi tây', '20036')])
def test_leaf_and_herb_identities_resolve_to_the_repaired_targets(matcher, phrase, code):
    assert matcher.match(phrase)['matched_item']['code'] == code


def test_live_corpus_guard_radius_is_exactly_the_reviewed_twenty(live_rows):
    guarded = [r for r in live_rows if em.is_coriander_seed_powder_text(r['raw_text'], r['cleaned_name'])]
    assert len(guarded) == 20
    assert all(r['match_method'] == 'UNMATCHED' for r in guarded)
    assert all(not (r['master_ingredient_code'] or '').strip() for r in guarded)
    assert set(fix.SEED_POWDER_ROW_IDS) <= {r['id'] for r in guarded}


def test_no_live_alias_or_catalog_name_is_caught_by_the_guard(live_aliases, live_catalog):
    assert [k for k in live_aliases if em.is_coriander_seed_powder_text(k)] == []
    assert [r['name_vi'] for r in live_catalog.values() if em.is_coriander_seed_powder_text(r['name_vi'])] == []


def test_qwen_mapper_rule_follows_the_repaired_coriander_identity(live_catalog):
    from nlp.qwen_matching import build_mapper_rules
    active, _ = build_mapper_rules(live_catalog)
    ngo = [(terms, code, name) for terms, code, name in active if 'ngò rí' in terms]
    assert ngo == [(('rau mùi', 'ngò rí', 'ngò'), '4081', 'Rau mùi')]
