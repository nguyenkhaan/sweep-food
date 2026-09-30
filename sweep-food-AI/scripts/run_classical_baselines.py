import json
import math
import re
from collections import Counter, defaultdict
import numpy as np
import pandas as pd

# Load benchmark pairs
df = pd.read_csv('data/benchmark/ablation_benchmark_pairs.csv')
with open('data/benchmark/fair_benchmark_100_queries.json', 'r', encoding='utf-8') as f:
    pantries = json.load(f)
with open('data/processed/recipes/recipes.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)
with open('data/processed/recipes/recipe_ingredients.json', 'r', encoding='utf-8') as f:
    ingredients = json.load(f)

# Metrics
def evaluate_ndcg(y_true: np.ndarray, y_score: np.ndarray, k: int = 5) -> float:
    order = np.argsort(y_score)[::-1][:k]
    gains = (2 ** y_true[order] - 1) / np.log2(np.arange(2, len(order) + 2))
    dcg = np.sum(gains)

    ideal_order = np.argsort(y_true)[::-1][:k]
    ideal_gains = (2 ** y_true[ideal_order] - 1) / np.log2(np.arange(2, len(ideal_order) + 2))
    idcg = np.sum(ideal_gains)
    return 0.0 if idcg == 0 else float(dcg / idcg)

def evaluate_mrr(y_true: np.ndarray, y_score: np.ndarray) -> float:
    order = np.argsort(y_score)[::-1]
    for rank_idx, idx in enumerate(order, start=1):
        if y_true[idx] >= 2:
            return 1.0 / rank_idx
    return 0.0

def evaluate_hit_rate(y_true: np.ndarray, y_score: np.ndarray, k: int = 3) -> float:
    order = np.argsort(y_score)[::-1][:k]
    return 1.0 if any(y_true[i] >= 2 for i in order) else 0.0

# 1. Okapi BM25 implementation on recipe ingredients
# Build corpus of recipes: tokens of cleaned ingredient names
recipe_corpus = {}
recipe_ings_map = defaultdict(list)
for ing in ingredients:
    recipe_ings_map[ing['recipe_id']].append(ing)

for r in recipes:
    r_id = r['id']
    r_ings = recipe_ings_map.get(r_id, [])
    tokens = []
    for ing in r_ings:
        name = (ing.get('cleaned_name') or ing.get('name') or '').lower()
        clean = re.sub(r'[^\w\s]', ' ', name)
        tokens.extend([t for t in clean.split() if len(t) > 1])
    recipe_corpus[r_id] = tokens

# Corpus statistics
N = len(recipe_corpus)
avgdl = sum(len(doc) for doc in recipe_corpus.values()) / max(1, N)
df_counts = Counter()
for doc in recipe_corpus.values():
    for token in set(doc):
        df_counts[token] += 1

def compute_bm25_score(query_tokens: list[str], doc_tokens: list[str], k1=1.5, b=0.75) -> float:
    doc_len = len(doc_tokens)
    doc_freq = Counter(doc_tokens)
    score = 0.0
    for q in query_tokens:
        if q not in df_counts:
            continue
        n_q = df_counts[q]
        idf = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1.0)
        f = doc_freq.get(q, 0)
        denom = f + k1 * (1 - b + b * (doc_len / avgdl))
        if denom > 0:
            score += idf * (f * (k1 + 1.0)) / denom
    return score

# Compute BM25 for all rows in ablation_benchmark_pairs
pantry_map = {p['pantry_id']: p for p in pantries}
bm25_scores = []
for idx, row in df.iterrows():
    p = pantry_map.get(row['pantry_id'])
    p_tokens = []
    if p:
        for it in p['items']:
            clean = re.sub(r'[^\w\s]', ' ', (it.get('name') or '').lower())
            p_tokens.extend([t for t in clean.split() if len(t) > 1])
    r_tokens = recipe_corpus.get(row['recipe_id'], [])
    bm25_scores.append(compute_bm25_score(p_tokens, r_tokens))

df['bm25_score'] = bm25_scores

# Benchmark comparison across all models/methods
evaluation_cols = {
    'BM25 (Information Retrieval)': 'bm25_score',
    'Jaccard Set Similarity': 'raw_jaccard_similarity',
    'Token Overlap Ratio': 'raw_token_overlap_ratio',
    'Ingredient Weight Ratio': 'raw_weight_ratio',
    'Domain Expert Heuristic': 'baseline_score',
}

results = {}
for name, col in evaluation_cols.items():
    ndcg1, ndcg3, ndcg5, mrr, hit3 = [], [], [], [], []
    for p_id, group in df.groupby('pantry_id'):
        y_t = group['label'].values
        y_p = group[col].values
        if len(y_t) > 1 and np.sum(y_t) > 0:
            ndcg1.append(evaluate_ndcg(y_t, y_p, k=1))
            ndcg3.append(evaluate_ndcg(y_t, y_p, k=3))
            ndcg5.append(evaluate_ndcg(y_t, y_p, k=5))
            mrr.append(evaluate_mrr(y_t, y_p))
            hit3.append(evaluate_hit_rate(y_t, y_p, k=3))
    results[name] = {
        'NDCG@1': float(np.mean(ndcg1)),
        'NDCG@3': float(np.mean(ndcg3)),
        'NDCG@5': float(np.mean(ndcg5)),
        'MRR': float(np.mean(mrr)),
        'HitRate@3': float(np.mean(hit3)) * 100,
    }

# Also append LightGBM and XGBoost from fair_benchmark_results.json
with open('data/benchmark/fair_benchmark_results.json', 'r', encoding='utf-8') as f:
    fb_res = json.load(f)

for k in ['LightGBM Ranker', 'XGBoost Ranker', 'Ensemble (50/50)']:
    if k in fb_res:
        results[k] = {
            'NDCG@1': fb_res[k]['NDCG@1'],
            'NDCG@3': fb_res[k]['NDCG@3'],
            'NDCG@5': fb_res[k]['NDCG@5'],
            'MRR': fb_res[k]['MRR'],
            'HitRate@3': fb_res[k]['HitRate@3'],
        }

with open('data/benchmark/full_baselines_benchmark_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*85)
print(f"{'Method':<32} | {'NDCG@1':<8} | {'NDCG@3':<8} | {'NDCG@5':<8} | {'MRR':<8} | {'HitRate@3':<10}")
print("="*85)
for name, m in results.items():
    print(f"{name:<32} | {m['NDCG@1']:.4f}   | {m['NDCG@3']:.4f}   | {m['NDCG@5']:.4f}   | {m['MRR']:.4f}   | {m['HitRate@3']:.2f}%")
print("="*85)
