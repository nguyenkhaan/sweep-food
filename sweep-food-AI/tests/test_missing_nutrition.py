"""Regression tests without loading GPU models or running destructive pipelines."""

import ast
import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from nlp.nutrition import NUTRITION_FIELDS, nutrition_value, restore_missing_nutrition, scale_nutrition
from scripts.eda.validate_missing_nutrition import inconsistent

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('missing', [None, '', '  ', 'NaN', float('nan')])
@pytest.mark.parametrize('factor', [0, 0.1, 2.5])
def test_missing_scaling(missing, factor):
    assert nutrition_value(missing) is None
    assert scale_nutrition(missing, factor) is None


@pytest.mark.parametrize('zero', [0, 0.0, '0', '0.0'])
def test_true_zero(zero):
    assert scale_nutrition(zero, 2.5) == 0


def test_known_values_and_rounding():
    assert scale_nutrition('12.34', 2.5) == round(12.34 * 2.5, 2)
    assert scale_nutrition('12.34', 2.5, 1) == round(12.34 * 2.5, 1)


def test_restore_and_serialization():
    master = {'energy_kcal': '100', 'protein_g': 'NaN', 'fat_g': '0', 'carbs_g': '20'}
    row = {'id': 'i', 'master_ingredient_code': 'm', 'calories': '250', 'protein_g': '0', 'fat_g': '0', 'carbs_g': '50', 'fiber_g': '3', 'match_method': 'UNMATCHED', 'estimated_weight_g': '10'}
    restored = restore_missing_nutrition([row], {'m': master})[0]
    assert restored == {**row, 'protein_g': None}
    assert row['protein_g'] == '0'
    assert restore_missing_nutrition([row], {}) == [row]
    assert restore_missing_nutrition([restored], {'m': master}) == [restored]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(restored)
    assert list(csv.DictReader(io.StringIO(stream.getvalue())))[0]['protein_g'] == ''
    assert json.loads(json.dumps(restored, allow_nan=False))['protein_g'] is None


def execute_nodes(nodes, namespace):
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<production nutrition>', 'exec'), namespace)


@pytest.mark.parametrize('missing', ['', float('nan')])
def test_single_and_batch_production_paths(missing):
    # Compile the actual class, excluding heavyweight module-level model imports.
    tree = ast.parse((ROOT / 'nlp/pipeline.py').read_text(encoding='utf-8'))
    namespace = {'scale_nutrition': scale_nutrition}
    future = ast.parse('from __future__ import annotations').body
    execute_nodes(future + [n for n in tree.body if isinstance(n, ast.ClassDef)], namespace)
    cls = namespace['IngredientProcessingPipeline']
    pipeline = cls.__new__(cls)
    parsed = SimpleNamespace(name='ingredient', quantity=250, canonical_unit='GRAM', to_dict=lambda: {})
    match = {'matched_item': {'energy_kcal': '100', 'protein_g': missing, 'fat_g': '0', 'carbs_g': '20'}, 'confidence': 1, 'method': 'fixture', 'top_candidates': []}
    pipeline.parser = SimpleNamespace(parse=lambda _: parsed, parse_batch=lambda *a, **k: [parsed])
    pipeline.matcher = SimpleNamespace(match=lambda *a, **k: match, match_batch=lambda *a, **k: [match])
    expected = {'calories_kcal': 250.0, 'protein_g': None, 'fat_g': 0.0, 'carbs_g': 50.0}
    assert pipeline.process('250g ingredient')['estimated_portion_nutrition'] == expected
    assert pipeline.process_batch(['250g ingredient'])[0]['estimated_portion_nutrition'] == expected


def test_crawler_scaling_and_legacy_totals():
    tree = ast.parse((ROOT / 'crawler/post_processing.py').read_text(encoding='utf-8'))
    conversion = next(n for n in ast.walk(tree) if isinstance(n, ast.Try) and ast.unparse(n.body[0]).startswith('c_kcal ='))
    portion = next(n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == 'factor is not None and nut')
    namespace = {'nutrition_value': nutrition_value, 'scale_nutrition': scale_nutrition,
                 'matched_item': {'energy_kcal': '100', 'protein_g': '', 'fat_g': '0', 'carbs_g': '20'}}
    execute_nodes([conversion], namespace)
    namespace.update(nut=dict(zip(['calories', 'protein', 'fat', 'carbs'], [namespace[k] for k in ['c_kcal', 'c_p', 'c_f', 'c_c']])), factor=2.5,
                     tot_cal=1, tot_prot=2, tot_fat=3, tot_carbs=4)
    execute_nodes([portion], namespace)
    assert [namespace[k] for k in ['portion_cal', 'portion_prot', 'portion_fat', 'portion_carbs']] == [250, None, 0, 50]
    assert [namespace[k] for k in ['tot_cal', 'tot_prot', 'tot_fat', 'tot_carbs']] == [251, 2, 3, 54]


def test_qwen_recalculation():
    """The nutrition-recalculation-on-match-acceptance behavior this test
    protected now lives in nlp.matching_integrity.stage_qwen_update (used by
    scripts/run_qwen_line_pipeline.py); see tests/test_matching_integrity.py
    and tests/test_qwen_matching.py for its full regression coverage."""
    from nlp.matching_integrity import MATCH_FIELDS, stage_qwen_update

    master_dict = {'m': {'name_vi': 'Test item', 'energy_kcal': '100', 'protein_g': '', 'fat_g': '0', 'carbs_g': '20'}}
    match_fields = dict(zip(MATCH_FIELDS, ('m', 'Test item', 'QWEN_LLM_MATCH', '0.98')))
    updates = stage_qwen_update({}, master_dict, 250, match_fields=match_fields)
    assert updates['calories'] == '250.0'
    assert updates['protein_g'] is None
    assert updates['fat_g'] == '0.0'
    assert updates['carbs_g'] == '50.0'
    assert updates['match_confidence'] == '0.98'


def test_comparison_excludes_missing_macros():
    row = dict(calories='100', protein_g='0', fat_g='0', carbs_g='0')
    assert inconsistent(row)
    assert not inconsistent({**row, 'protein_g': None})
    assert not inconsistent({**row, 'calories': '0'})
