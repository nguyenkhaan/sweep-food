"""Deep Training Suite for 3-Tier Feature Ablation Study.

Trains LightGBM and XGBoost Rankers across 3 feature tiers:
1. X_raw (16 features)
2. X_engineered (25 features)
3. X_full (30 features)

Saves all 6 models for comprehensive benchmarking:
- data/training/lgbm_raw.txt, data/training/xgb_raw.json
- data/training/lgbm_engineered.txt, data/training/xgb_engineered.json
- data/training/lgbm_full.txt, data/training/xgb_full.json
"""

from __future__ import annotations

import json
import os
import sys
import time
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

import lightgbm as lgb
import xgboost as xgb

DATA_DIR = "data/training"


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


def compute_metrics(df: pd.DataFrame, pred_col: str) -> dict[str, float]:
    ndcg1_list, ndcg3_list, ndcg5_list, mrr_list = [], [], [], []

    for _, group in df.groupby("pantry_id"):
        y_t = group["label"].values
        y_p = group[pred_col].values

        if len(y_t) > 1 and np.sum(y_t) > 0:
            ndcg1_list.append(evaluate_ndcg(y_t, y_p, k=1))
            ndcg3_list.append(evaluate_ndcg(y_t, y_p, k=3))
            ndcg5_list.append(evaluate_ndcg(y_t, y_p, k=5))
            mrr_list.append(evaluate_mrr(y_t, y_p))

    return {
        "NDCG@1": float(np.mean(ndcg1_list)) if ndcg1_list else 0.0,
        "NDCG@3": float(np.mean(ndcg3_list)) if ndcg3_list else 0.0,
        "NDCG@5": float(np.mean(ndcg5_list)) if ndcg5_list else 0.0,
        "MRR": float(np.mean(mrr_list)) if mrr_list else 0.0,
    }


def main():
    print("=" * 90)
    print("       3-TIER FEATURE ABLATION TRAINING TOURNAMENT (LIGHTGBM vs XGBOOST)")
    print("=" * 90)

    print("\n[STEP 1/3] LOADING DATASETS & METADATA...")
    train_df = pd.read_csv(os.path.join(DATA_DIR, "train_ltr.csv"))
    val_df = pd.read_csv(os.path.join(DATA_DIR, "val_ltr.csv"))
    test_df = pd.read_csv(os.path.join(DATA_DIR, "test_ltr.csv"))

    with open(os.path.join(DATA_DIR, "metadata.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)

    tiers = {
        "X_raw": meta["feature_tiers"]["raw_features"],
        "X_engineered": meta["feature_tiers"]["engineered_features"],
        "X_full": meta["feature_tiers"]["full_features"],
    }

    print(f"  * Train samples: {len(train_df):,} ({train_df['pantry_id'].nunique():,} pantries)")
    print(f"  * Val samples:   {len(val_df):,} ({val_df['pantry_id'].nunique():,} pantries)")
    print(f"  * Test samples:  {len(test_df):,} ({test_df['pantry_id'].nunique():,} pantries)")
    for t_name, f_cols in tiers.items():
        print(f"  * {t_name:<14}: {len(f_cols)} features")

    train_groups = train_df.groupby("pantry_id", sort=False).size().tolist()
    val_groups = val_df.groupby("pantry_id", sort=False).size().tolist()
    test_groups = test_df.groupby("pantry_id", sort=False).size().tolist()

    y_train = train_df["label"].values
    y_val = val_df["label"].values
    y_test = test_df["label"].values

    ablation_results = {}

    print("\n[STEP 2/3] TRAINING & EVALUATING MODELS ACROSS ALL 3 FEATURE TIERS...")

    for tier_name, cols in tiers.items():
        print("\n" + "-" * 75)
        print(f"--> TRAINING ON TIER: {tier_name} ({len(cols)} features)")
        print("-" * 75)

        X_tr = train_df[cols]
        X_va = val_df[cols]
        X_te = test_df[cols]

        # 1. Train LightGBM
        t0_lgb = time.time()
        ranker_lgb = lgb.LGBMRanker(
            objective="lambdarank",
            n_estimators=1000,
            learning_rate=0.03,
            num_leaves=63,
            max_depth=8,
            min_child_samples=15,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.2,
            reg_lambda=0.5,
            random_state=42,
            n_jobs=-1
        )
        ranker_lgb.fit(
            X_tr, y_train,
            group=train_groups,
            eval_set=[(X_va, y_val)],
            eval_group=[val_groups],
            callbacks=[lgb.early_stopping(stopping_rounds=40, verbose=False)]
        )
        lgb_train_time = time.time() - t0_lgb

        # 2. Train XGBoost
        t0_xgb = time.time()
        ranker_xgb = xgb.XGBRanker(
            objective="rank:ndcg",
            eval_metric="ndcg@5",
            n_estimators=600,
            learning_rate=0.04,
            max_depth=6,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.2,
            reg_lambda=0.8,
            random_state=42,
            tree_method="hist",
            early_stopping_rounds=35,
            n_jobs=-1
        )
        ranker_xgb.fit(
            X_tr, y_train,
            group=train_groups,
            eval_set=[(X_va, y_val)],
            eval_group=[val_groups],
            verbose=False
        )
        xgb_train_time = time.time() - t0_xgb

        # Evaluate on Test Set
        te_df = test_df.copy()
        te_df["lgb_pred"] = ranker_lgb.predict(X_te)
        te_df["xgb_pred"] = ranker_xgb.predict(X_te)

        m_lgb = compute_metrics(te_df, "lgb_pred")
        m_xgb = compute_metrics(te_df, "xgb_pred")

        ablation_results[f"{tier_name}_LightGBM"] = {**m_lgb, "time_s": lgb_train_time, "best_tree": ranker_lgb.best_iteration_}
        ablation_results[f"{tier_name}_XGBoost"] = {**m_xgb, "time_s": xgb_train_time, "best_tree": ranker_xgb.best_iteration}

        print(f"  * LightGBM ({tier_name}): NDCG@3 = {m_lgb['NDCG@3']:.4f} | NDCG@5 = {m_lgb['NDCG@5']:.4f} | MRR = {m_lgb['MRR']:.4f} (Time: {lgb_train_time:.1f}s)")
        print(f"  * XGBoost  ({tier_name}): NDCG@3 = {m_xgb['NDCG@3']:.4f} | NDCG@5 = {m_xgb['NDCG@5']:.4f} | MRR = {m_xgb['MRR']:.4f} (Time: {xgb_train_time:.1f}s)")

        # Save model artifacts for each tier
        tier_suffix = tier_name.replace("X_", "")
        lgb_path = os.path.join(DATA_DIR, f"lgbm_{tier_suffix}.txt")
        xgb_path = os.path.join(DATA_DIR, f"xgb_{tier_suffix}.json")
        ranker_lgb.booster_.save_model(lgb_path)
        ranker_xgb.save_model(xgb_path)

        # Also keep lgbm_ranker.txt and xgb_ranker.json pointing to full tier as default
        if tier_name == "X_full":
            ranker_lgb.booster_.save_model(os.path.join(DATA_DIR, "lgbm_ranker.txt"))
            ranker_xgb.save_model(os.path.join(DATA_DIR, "xgb_ranker.json"))

    print("\n" + "=" * 90)
    print("                    HELD-OUT TEST 3-TIER ABLATION RESULTS")
    print("=" * 90)
    print(f"  {'Feature Tier & Model':<28} | {'NDCG@1':<8} | {'NDCG@3':<8} | {'NDCG@5':<8} | {'MRR':<8} | {'Trees':<6}")
    print("  " + "-" * 75)
    for model_key, res in ablation_results.items():
        print(f"  {model_key:<28} | {res['NDCG@1']:<8.4f} | {res['NDCG@3']:<8.4f} | {res['NDCG@5']:<8.4f} | {res['MRR']:<8.4f} | {res['best_tree']:<6}")
    print("=" * 90)

    # Save ablation summary
    with open(os.path.join(DATA_DIR, "ablation_training_summary.json"), "w", encoding="utf-8") as f:
        json.dump(ablation_results, f, indent=2)


if __name__ == "__main__":
    main()
