"""Gold-Standard 3-Tier Ablation Benchmark Tournament (100 Unseen Scenarios).

Evaluates the performance gain of feature engineering across 3 distinct tiers:
1. Tier 1: X_raw (16 features)
2. Tier 2: X_engineered (25 features)
3. Tier 3: X_full (30 features)

Across:
- Heuristic Baseline
- LightGBM Ranker
- XGBoost Ranker

Evaluated on 100 stratified, fair, zero-leakage benchmark pantry scenarios.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import lightgbm as lgb
import xgboost as xgb

from src.recommendation.candidate_generator import CandidateGenerator
from src.recommendation.benchmark_generator import generate_100_fair_benchmark_pantries
from src.recommendation.feature_extractor import extract_all_features
from src.recommendation.ground_truth_utility import compute_ground_truth_utility
from src.recommendation.heuristic_baseline import compute_domain_heuristic_score

RECIPES_JSON = "data/processed/recipes/recipes.json"
ING_JSON = "data/processed/recipes/recipe_ingredients.json"
DATA_DIR = "data/training"
BENCHMARK_DIR = "data/benchmark"


def evaluate_ndcg(y_true: np.ndarray, y_score: np.ndarray, k: int = 5) -> float:
    order = np.argsort(y_score)[::-1][:k]
    gains = (2 ** y_true[order] - 1) / np.log2(np.arange(2, len(order) + 2))
    dcg = np.sum(gains)

    ideal_order = np.argsort(y_true)[::-1][:k]
    ideal_gains = (2 ** y_true[ideal_order] - 1) / np.log2(np.arange(2, len(ideal_order) + 2))
    idcg = np.sum(ideal_gains)

    if idcg == 0:
        return 0.0
    return float(dcg / idcg)


def evaluate_mrr(y_true: np.ndarray, y_score: np.ndarray) -> float:
    order = np.argsort(y_score)[::-1]
    for rank_idx, idx in enumerate(order, start=1):
        if y_true[idx] >= 2:
            return 1.0 / rank_idx
    return 0.0


def evaluate_hit_rate(y_true: np.ndarray, y_score: np.ndarray, k: int = 3) -> float:
    order = np.argsort(y_score)[::-1][:k]
    return 1.0 if any(y_true[i] >= 2 for i in order) else 0.0


def main():
    print("=" * 95)
    print("      SWEEPFOOD AI: 3-TIER FEATURE ABLATION BENCHMARK TOURNAMENT (100 SCENARIOS)")
    print("=" * 95)

    os.makedirs(BENCHMARK_DIR, exist_ok=True)

    # 1. Load Knowledge Base
    print("\n[STEP 1/5] LOADING PRODUCTION KNOWLEDGE BASE...")
    with open(RECIPES_JSON, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    with open(ING_JSON, "r", encoding="utf-8") as f:
        ingredients = json.load(f)
    print(f"  * Loaded {len(recipes):,} recipes and {len(ingredients):,} ingredient lines.")

    cg = CandidateGenerator(recipes, ingredients)
    recipe_ings_map = cg.recipe_ingredients

    # 2. Generate 100 Stratified Unseen Pantries
    print("\n[STEP 2/5] GENERATING 100 STRATIFIED UNSEEN PANTRY BENCHMARK QUERIES...")
    pantries = generate_100_fair_benchmark_pantries(seed=2026)
    print(f"  * Generated {len(pantries)} queries partitioned across 9 Vietnamese personas.")

    # 3. Load Feature Tiers & Trained Models
    print("\n[STEP 3/5] LOADING FEATURE TIERS & TRAINED ABLATION MODELS...")
    with open(os.path.join(DATA_DIR, "metadata.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)

    tiers = {
        "raw": meta["feature_tiers"]["raw_features"],
        "engineered": meta["feature_tiers"]["engineered_features"],
        "full": meta["feature_tiers"]["full_features"],
    }

    models = {}
    for tier_name in ["raw", "engineered", "full"]:
        lgb_p = os.path.join(DATA_DIR, f"lgbm_{tier_name}.txt")
        xgb_p = os.path.join(DATA_DIR, f"xgb_{tier_name}.json")
        models[f"LGBM_{tier_name}"] = lgb.Booster(model_file=lgb_p)
        xgb_b = xgb.Booster()
        xgb_b.load_model(xgb_p)
        models[f"XGB_{tier_name}"] = xgb_b

    print("  * Successfully loaded all 6 models across 3 feature tiers.")

    # 4. Execute Benchmark Inference
    print("\n[STEP 4/5] EXECUTING 100-QUERY ABLATION INFERENCE...")

    all_query_data = []
    benchmark_rows = []

    for p in pantries:
        p_id = p["pantry_id"]
        scenario = p["scenario_type"]
        candidates = cg.retrieve_candidates(p["items"], top_n=30)

        if not candidates:
            continue

        q_rows = []
        for cand in candidates:
            r_id = cand["id"]
            r_ings = recipe_ings_map.get(r_id, [])

            feats = extract_all_features(p, cand, r_ings)
            latent_u, label = compute_ground_truth_utility(p, cand, r_ings, add_stochastic_noise=True)

            # Handcrafted Domain Expert Heuristic Baseline (Formula using domain elasticity & deficits)
            baseline_score = compute_domain_heuristic_score(p, cand, r_ings)

            row = {
                "pantry_id": p_id,
                "recipe_id": r_id,
                "recipe_name": cand["name"],
                "scenario_type": scenario,
                "latent_utility": latent_u,
                "label": label,
                "baseline_score": baseline_score,
                **feats
            }
            q_rows.append(row)
            benchmark_rows.append(row)

        q_df = pd.DataFrame(q_rows)

        # Predictions for all models
        preds = {"Heuristic": q_df["baseline_score"].values}
        for tier_name in ["raw", "engineered", "full"]:
            cols = tiers[tier_name]
            X_tier = q_df[cols]
            preds[f"LGBM_{tier_name}"] = models[f"LGBM_{tier_name}"].predict(X_tier)
            preds[f"XGB_{tier_name}"] = models[f"XGB_{tier_name}"].predict(xgb.DMatrix(X_tier))

        all_query_data.append({
            "pantry_id": p_id,
            "scenario": scenario,
            "y_true": q_df["label"].values,
            "preds": preds
        })

    print(f"  * Completed evaluation for {len(all_query_data)} queries ({len(benchmark_rows):,} candidate pairs).")

    # 5. Compute Benchmark Metrics
    model_keys = [
        "Heuristic",
        "LGBM_raw", "LGBM_engineered", "LGBM_full",
        "XGB_raw", "XGB_engineered", "XGB_full"
    ]

    benchmark_summary = {}
    for mk in model_keys:
        ndcg1_list, ndcg3_list, ndcg5_list, mrr_list, hit3_list = [], [], [], [], []

        for q in all_query_data:
            y_t = q["y_true"]
            y_p = q["preds"][mk]

            if len(y_t) > 1 and np.sum(y_t) > 0:
                ndcg1_list.append(evaluate_ndcg(y_t, y_p, k=1))
                ndcg3_list.append(evaluate_ndcg(y_t, y_p, k=3))
                ndcg5_list.append(evaluate_ndcg(y_t, y_p, k=5))
                mrr_list.append(evaluate_mrr(y_t, y_p))
                hit3_list.append(evaluate_hit_rate(y_t, y_p, k=3))

        benchmark_summary[mk] = {
            "NDCG@1": float(np.mean(ndcg1_list)),
            "NDCG@3": float(np.mean(ndcg3_list)),
            "NDCG@5": float(np.mean(ndcg5_list)),
            "MRR": float(np.mean(mrr_list)),
            "HitRate@3": float(np.mean(hit3_list)) * 100,
        }

    # Print Official Comparison Table
    print("\n" + "=" * 95)
    print("               3-TIER FEATURE ABLATION BENCHMARK RESULTS (100 QUERIES)")
    print("=" * 95)
    print(f"  {'Model & Feature Tier':<26} | {'NDCG@1':<8} | {'NDCG@3':<8} | {'NDCG@5':<8} | {'MRR':<8} | {'Hit@3 (%)'}")
    print("  " + "-" * 75)
    for mk in model_keys:
        m = benchmark_summary[mk]
        print(f"  {mk:<26} | {m['NDCG@1']:<8.4f} | {m['NDCG@3']:<8.4f} | {m['NDCG@5']:<8.4f} | {m['MRR']:<8.4f} | {m['HitRate@3']:>7.1f}%")
    print("=" * 95)

    # Performance Improvement Breakdown (Ablation Story)
    print("\n[STEP 5/5] CONTROLLED ABLATION PERFORMANCE GAIN (DELTA NDCG@5):")
    xgb_raw = benchmark_summary["XGB_raw"]["NDCG@5"]
    xgb_eng = benchmark_summary["XGB_engineered"]["NDCG@5"]
    xgb_full = benchmark_summary["XGB_full"]["NDCG@5"]
    print(f"  * XGBoost Gain (Raw -> Engineered) : +{xgb_eng - xgb_raw:.4f}")
    print(f"  * XGBoost Gain (Engineered -> Full): +{xgb_full - xgb_eng:.4f}")
    print(f"  * XGBoost Total Gain (Raw -> Full) : +{xgb_full - xgb_raw:.4f}")
    print(f"  * Total Improvement over Heuristic : +{xgb_full - benchmark_summary['Heuristic']['NDCG@5']:.4f}")

    # Save artifacts
    results_path = os.path.join(BENCHMARK_DIR, "ablation_benchmark_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    df_bench = pd.DataFrame(benchmark_rows)
    df_bench.to_csv(os.path.join(BENCHMARK_DIR, "ablation_benchmark_pairs.csv"), index=False, encoding="utf-8-sig")

    print(f"\nSaved ablation benchmark results to: {BENCHMARK_DIR}/")
    print("=" * 95)


if __name__ == "__main__":
    main()
