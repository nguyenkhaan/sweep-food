"""Generates 3-Tier Decoupled Learning-to-Rank (LTR) Datasets.

Produces:
- data/training/train_ltr.csv
- data/training/val_ltr.csv
- data/training/test_ltr.csv
- data/training/metadata.json (stores definitions for X_raw, X_engineered, X_full)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from src.recommendation.candidate_generator import CandidateGenerator
from src.recommendation.pantry_simulator import generate_vietnamese_pantry
from src.recommendation.feature_extractor import (
    extract_all_features,
    RAW_FEATURE_COLS,
    ENGINEERED_FEATURE_COLS,
    FULL_FEATURE_COLS
)
from src.recommendation.ground_truth_utility import compute_ground_truth_utility

RECIPES_JSON = "data/processed/recipes/recipes.json"
ING_JSON = "data/processed/recipes/recipe_ingredients.json"
OUTPUT_DIR = "data/training"


def main():
    parser = argparse.ArgumentParser(description="Generate Decoupled 3-Tier LTR Dataset")
    parser.add_argument("--samples", type=int, default=50000, help="Target total query-candidate ranking samples")
    parser.add_argument("--pantries", type=int, default=0, help="Exact number of pantries")
    args = parser.parse_args()

    target_samples = args.samples
    exact_pantries = args.pantries

    print("=" * 85)
    print("   GENERATING 3-TIER DECOUPLED LEARNING-TO-RANK DATASET (ZERO LEAKAGE)")
    if exact_pantries > 0:
        print(f"Target: {exact_pantries:,} simulated pantries across 8 culinary personas")
    else:
        print(f"Target: {target_samples:,} rich query-candidate ranking pairs across 8 culinary personas")
    print("=" * 85)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n1. Loading recipe knowledge base...")
    t0 = time.time()
    with open(RECIPES_JSON, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    with open(ING_JSON, "r", encoding="utf-8") as f:
        ingredients = json.load(f)
    print(f"   Loaded {len(recipes):,} recipes and {len(ingredients):,} ingredient lines in {time.time() - t0:.2f}s.")

    print("\n2. Initializing Inverted Index Candidate Generator...")
    cg = CandidateGenerator(recipes, ingredients)
    recipe_ings_map = cg.recipe_ingredients

    print("\n3. Simulating realistic pantries & generating decoupled (X, y) pairs...")
    t1 = time.time()

    all_rows = []
    pantry_groups = []
    label_distribution = Counter()
    persona_distribution = Counter()

    pantry_idx = 0
    while True:
        pantry = generate_vietnamese_pantry(pantry_idx)
        p_id = pantry["pantry_id"]
        persona = pantry["scenario_type"]
        candidates = cg.retrieve_candidates(pantry["items"], top_n=30)

        group_size = 0
        for cand in candidates:
            r_id = cand["id"]
            r_ings = recipe_ings_map.get(r_id, [])

            # Extract full 30-feature observable dictionary
            feats = extract_all_features(pantry, cand, r_ings)

            # Compute ground-truth human satisfaction independently
            latent_u, label = compute_ground_truth_utility(pantry, cand, r_ings, add_stochastic_noise=True)

            label_distribution[label] += 1
            persona_distribution[persona] += 1

            row = {
                "pantry_id": p_id,
                "recipe_id": r_id,
                "scenario_type": persona,
                "recipe_name": cand["name"],
                "latent_utility": round(latent_u, 4),
                "label": label,
                **feats
            }
            all_rows.append(row)
            group_size += 1

        if group_size > 0:
            pantry_groups.append({"pantry_id": p_id, "size": group_size})

        pantry_idx += 1

        if pantry_idx % 500 == 0:
            print(f"   Simulated {pantry_idx:,} pantries -> {len(all_rows):,} samples generated...")

        if exact_pantries > 0 and pantry_idx >= exact_pantries:
            break
        elif exact_pantries == 0 and len(all_rows) >= target_samples:
            break

    print(f"\n   Generation finished: {len(all_rows):,} samples from {pantry_idx:,} pantries in {time.time() - t1:.2f}s.")

    print("\n   Persona Distribution:")
    for p_name, cnt in persona_distribution.most_common():
        pct = (cnt / len(all_rows)) * 100
        print(f"    * {p_name:<25}: {cnt:>6,} samples ({pct:>5.1f}%)")

    print("\n   Label Distribution:")
    total_pairs = len(all_rows)
    for lbl in sorted(label_distribution.keys(), reverse=True):
        cnt = label_distribution[lbl]
        pct = (cnt / total_pairs) * 100
        desc = {
            3: "Grade 3 (Optimal zero-waste hero)",
            2: "Grade 2 (Highly feasible ready-to-cook)",
            1: "Grade 1 (Marginal / Needs minor shopping)",
            0: "Grade 0 (Infeasible / Irrelevant)"
        }.get(lbl, "")
        print(f"    * Label {lbl}: {cnt:>7,} ({pct:>5.1f}%) - {desc}")

    print("\n4. Splitting data strictly by Query Group (pantry_id) to prevent leakage...")
    n_groups = len(pantry_groups)
    train_end = int(n_groups * 0.70)
    val_end = int(n_groups * 0.85)

    train_pids = set(g["pantry_id"] for g in pantry_groups[:train_end])
    val_pids = set(g["pantry_id"] for g in pantry_groups[train_end:val_end])
    test_pids = set(g["pantry_id"] for g in pantry_groups[val_end:])

    train_rows = [r for r in all_rows if r["pantry_id"] in train_pids]
    val_rows = [r for r in all_rows if r["pantry_id"] in val_pids]
    test_rows = [r for r in all_rows if r["pantry_id"] in test_pids]

    train_groups = [g["size"] for g in pantry_groups[:train_end]]
    val_groups = [g["size"] for g in pantry_groups[train_end:val_end]]
    test_groups = [g["size"] for g in pantry_groups[val_end:]]

    print(f"   Train Set: {len(train_rows):,} pairs across {len(train_pids):,} pantry queries.")
    print(f"   Val Set:   {len(val_rows):,} pairs across {len(val_pids):,} pantry queries.")
    print(f"   Test Set:  {len(test_rows):,} pairs across {len(test_pids):,} pantry queries.")

    print("\n5. Saving datasets to data/training/...")
    fieldnames = list(all_rows[0].keys())

    def write_csv(filepath, rows):
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(os.path.join(OUTPUT_DIR, "train_ltr.csv"), train_rows)
    write_csv(os.path.join(OUTPUT_DIR, "val_ltr.csv"), val_rows)
    write_csv(os.path.join(OUTPUT_DIR, "test_ltr.csv"), test_rows)

    metadata = {
        "total_pairs": len(all_rows),
        "total_pantries": pantry_idx,
        "feature_tiers": {
            "raw_features": RAW_FEATURE_COLS,
            "engineered_features": ENGINEERED_FEATURE_COLS,
            "full_features": FULL_FEATURE_COLS,
        },
        "feature_counts": {
            "X_raw": len(RAW_FEATURE_COLS),
            "X_engineered": len(ENGINEERED_FEATURE_COLS),
            "X_full": len(FULL_FEATURE_COLS)
        },
        "train_query_count": len(train_pids),
        "val_query_count": len(val_pids),
        "test_query_count": len(test_pids),
        "train_groups": train_groups,
        "val_groups": val_groups,
        "test_groups": test_groups
    }

    with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 85)
    print(f"DATASET GENERATION COMPLETE! Total samples: {len(all_rows):,}")
    print(f"Tier 1 (X_raw):        {len(RAW_FEATURE_COLS)} features")
    print(f"Tier 2 (X_engineered): {len(ENGINEERED_FEATURE_COLS)} features")
    print(f"Tier 3 (X_full):       {len(FULL_FEATURE_COLS)} features")
    print("Stored in: data/training/")
    print("=" * 85)


if __name__ == "__main__":
    main()
