"""Reviewed catalog identities, strict row pins and every active matcher surface."""
from copy import deepcopy

import pytest

from nlp import entity_matcher as em
from scripts.eda import apply_catalog_integrity_safe_fix as fix


@pytest.fixture(scope='module')
def reviewed():
    return fix.read_json(fix.REVIEW)


@pytest.fixture(scope='module')
def corrected_catalog(reviewed):
    rows = deepcopy(reviewed['catalog_before'])
    for row in rows:
        row.update(fix.CATALOG_PATCHES.get(row['code'], {}))
    return fix.index(rows, 'code')


@pytest.mark.parametrize('cohort', fix.COHORTS)
def test_reviewed_nutrition_and_source_preservation(reviewed, corrected_catalog, cohort):
    pins = [p for p in reviewed['rows'] if p['cohort'] == cohort]
    assert len(pins) == fix.COHORTS[cohort][3]
    for pin in pins:
        before = pin['before']
        after = fix.expected_row(pin, corrected_catalog)
        mutable = set(fix.NUTRIENTS) | {'master_ingredient_code', 'master_ingredient_name', 'match_method', 'match_confidence'}
        assert {k:v for k,v in before.items() if k not in mutable} == {k:v for k,v in after.items() if k not in mutable}
        if cohort == 'chicken_fat':
            assert after['match_method'] == 'UNMATCHED'
            assert all(after[f] is None for f in mutable - {'match_method'})
        else:
            assert after['master_ingredient_code'] == pin['target_code']
        if cohort == 'pork_tail':
            assert float(before['carbs_g']) == 0
            assert after['carbs_g'] is None
        if cohort == 'chicken_heart':
            assert after['match_method'] == 'EXACT_CATALOG_MATCH'
            assert after['carbs_g'] is None
            assert float(after['calories']) == pytest.approx(float(before['estimated_weight_g']) * 1.14)


@pytest.mark.parametrize('field,value', [('raw_text','different ingredient'), ('cleaned_name','gan bò'),
                                        ('recipe_id','different recipe'), ('master_ingredient_code','7045'),
                                        ('calories','99999'), ('estimated_weight_g','1')])
def test_row_drift_fails_before_any_write(monkeypatch, reviewed, field, value):
    original = fix.read_csv
    original_json = fix.read_json
    rid = reviewed['rows'][0]['before']['id']
    def read(path):
        rows = original(path)
        if path.name == 'recipe_ingredients.csv':
            next(r for r in rows if r['id'] == rid)[field] = value
        return rows
    monkeypatch.setattr(fix, 'read_csv', read)
    def read_json(path):
        result = original_json(path)
        if path.name == 'recipe_ingredients.json':
            next(r for r in result if r['id'] == rid)[field] = value
        return result
    monkeypatch.setattr(fix, 'read_json', read_json)
    monkeypatch.setattr(fix, 'write_csv', lambda *a: pytest.fail('wrote before validation'))
    with pytest.raises(fix.DriftError, match='Row drift'):
        fix.plan()


@pytest.mark.parametrize('field,value', [('name_vi','Unexpected name'), ('name_en','wrong identity'),
                                        ('energy_kcal','1'), ('category_vi','wrong category')])
def test_catalog_drift_fails_closed(monkeypatch, field, value):
    original = fix.read_csv
    def read(path):
        rows = original(path)
        if path == fix.ROOT / fix.CAT:
            next(r for r in rows if r['code'] == '7038')[field] = value
        return rows
    monkeypatch.setattr(fix, 'read_csv', read)
    with pytest.raises(fix.DriftError, match='Catalog drift'):
        fix.plan()


@pytest.mark.parametrize('alias', ['gan heo', 'mỡ gà', 'đuôi', 'đuôi bò'])
def test_alias_and_sibling_drift_rejected(monkeypatch, alias):
    original = fix.read_json
    def read(path):
        result = original(path)
        if path == fix.ROOT / fix.ALIASES:
            result[alias] = '99999'
        return result
    monkeypatch.setattr(fix, 'read_json', read)
    with pytest.raises(fix.DriftError, match='Alias drift'):
        fix.plan()


@pytest.fixture
def matcher():
    return em.VietnameseIngredientMatcher()


@pytest.mark.parametrize('query,code', fix.PROBES.items())
def test_real_single_and_batch_matches(matcher, monkeypatch, query, code):
    monkeypatch.setattr(matcher, '_init_model', lambda: pytest.fail('unexpected neural fallthrough'))
    for result in (matcher.match(query), matcher.match_batch([query])[0]):
        assert (result['matched_item'] or {}).get('code') == code


@pytest.mark.parametrize('query,context', [('mỡ gà',''), ('Mỡ gà tươi',''), ('mỡ','2 muỗng mỡ gà')])
def test_chicken_fat_guard_prevents_neural_and_stale_alias(matcher, monkeypatch, query, context):
    matcher.alias_dict[em.normalize_vietnamese_text(query)] = 0
    monkeypatch.setattr(matcher, '_init_model', lambda: pytest.fail('chicken fat reached neural'))
    for result in (matcher.match(query, raw_context=context), matcher.match_batch([query],raw_contexts=[context])[0]):
        assert not result['matched_item']
        assert result['method'] == 'UNMATCHED'


def test_deprecated_code_retained_but_removed_from_all_indexes(matcher):
    idx = next(i for i,r in enumerate(matcher.catalog) if r['code']=='20079')
    assert len(matcher.catalog)==750
    assert matcher.catalog[idx]['name_vi']==em.DEPRECATED_CATALOG_IDENTITIES['20079']
    assert matcher.catalog[idx]['name_en']==''
    assert idx not in matcher.normalized_to_index.values()
    assert idx not in matcher.alias_dict.values()
    assert idx not in [x[3] for x in matcher.catalog_subphrase_items]
    assert 'pig tail' not in matcher.normalized_to_index


def test_neural_ranking_excludes_deprecated_even_when_it_scores_highest(matcher, monkeypatch):
    torch = pytest.importorskip('torch')
    vectors = torch.zeros((750, 2))
    old = next(i for i,r in enumerate(matcher.catalog) if r['code']=='20079')
    target = next(i for i,r in enumerate(matcher.catalog) if r['code']=='7038')
    vectors[old,0], vectors[target,0] = 1.0, 0.9
    matcher.catalog_embeddings = vectors
    monkeypatch.setattr(matcher, '_init_model', lambda: None)
    monkeypatch.setattr(matcher, 'encode_text', lambda q: torch.tensor([[1.0,0.0]]))
    monkeypatch.setattr(matcher, 'encode_batch', lambda q,**k: torch.tensor([[1.0,0.0]]))
    for query in ('pig tail', em.DEPRECATED_CATALOG_IDENTITIES['20079']):
        for result in (matcher.match(query,top_k=750),matcher.match_batch([query],top_k=750)[0]):
            assert result['matched_item']['code']=='7038'
            assert len(result['top_candidates'])==749
            assert all(r['code']!='20079' for r in result['top_candidates'])


def test_no_torch_overlap_cannot_return_deprecated(matcher, monkeypatch):
    monkeypatch.setattr(em, 'TORCH_AVAILABLE', False)
    result = matcher.match(em.DEPRECATED_CATALOG_IDENTITIES['20079'])
    assert result['matched_item']['code'] != '20079'


def test_applied_real_data_matches_every_full_pin(reviewed, corrected_catalog):
    csv_rows = fix.read_csv(fix.ROOT/fix.DATA/'recipe_ingredients.csv')
    json_rows = fix.read_json(fix.ROOT/fix.DATA/'recipe_ingredients.json')
    fix.parity(csv_rows,json_rows)
    live = fix.index(csv_rows)
    for pin in reviewed['rows']:
        assert fix.logical(live[pin['before']['id']]) == fix.logical(fix.expected_row(pin,corrected_catalog))
    assert not any(r['master_ingredient_code']=='20079' for r in csv_rows)
    aliases = fix.read_json(fix.ROOT/fix.ALIASES)
    assert '20079' not in aliases.values()
    assert 'mỡ gà' not in aliases
    assert 'tim gà' not in aliases


def test_applied_catalog_preserves_all_non_display_columns(reviewed):
    catalog = fix.index(fix.read_csv(fix.ROOT/fix.CAT),'code')
    for before in reviewed['catalog_before']:
        assert catalog[before['code']] == dict(before, **fix.CATALOG_PATCHES.get(before['code'],{}))
