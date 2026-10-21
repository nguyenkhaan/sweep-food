"""Build scenario ranking data for the curated catalog and train LambdaMART.

Pipeline
--------
1. Load the curated catalog export (recipes + ingredient rows) and the master
   alias index used at serving time.
2. Generate Vietnamese pantry scenarios (`life_scenarios`, student-weighted),
   resolve item names like the web app, retrieve candidates with
   `CandidateGenerator`, compute the nine `FEATURE_COLS` and grade every pair
   with the scenario teacher (`scenario_rules.teacher_grade`), which also uses
   scenario signals the ranker does not see. Training labels add
   deterministic annotator noise; evaluation uses the clean grades.
3. Split query groups 70/15/15 (stratified by scenario), select
   hyperparameters on validation NDCG@5, retrain on train+val, evaluate on test.
4. Report baselines, the previous 9-feature production model (v2.1.0),
   leave-scenario-out generalisation and per-segment metrics.

Usage (needs lightgbm, e.g. the `ocr_env` conda env):
    python -X utf8 scripts/train_recommendation_ranker.py \
        --catalog-dir data/main/catalog
"""

from __future__ import annotations

import argparse
import collections
import csv
import gzip
import json
import math
import random
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.recommendation.candidate_generator import CandidateGenerator
from src.recommendation.contextual_features import FEATURE_COLS, MONOTONE_CONSTRAINTS, extract_contextual_features
from src.recommendation.life_scenarios import SCENARIOS, SCHEDULE, STUDENT, generate_life_pantry
from src.recommendation.pantry_resolver import build_master_alias_index, resolve_pantry_items
from src.recommendation.scenario_rules import MASTER_CSV, noisy_grade, scenario_profile, scenario_signals, teacher_grade

DEFAULT_CATALOG = ROOT / "data" / "main" / "catalog"
MODEL_TXT = ROOT / "data" / "training" / "lgbm_contextual.txt"
METADATA_JSON = ROOT / "data" / "training" / "metadata.json"
DATASET_DIR = ROOT / "data" / "training" / "catalog_ranking"

SEED = 20261019
LABEL_NOISE = 0.08
# Held out entirely for the generalisation experiment (two student situations).
HOLDOUT_SCENARIOS = [
    "sinh_vien_tro_mua_nong",
    "sinh_vien_thuc_tap_mang_com",
    "nguoi_gia_song_mot_minh",
    "me_bau",
    "nha_co_khach_bat_ngo",
]
PREVIOUS_9FEAT_MODEL = ROOT / "data" / "training" / "archive" / "lgbm_contextual_v2.1.0.txt"
GRID = [
    {"num_leaves": nl, "min_data_in_leaf": md}
    for nl in (15, 31, 63) for md in (20, 60)
]


# ----------------------------------------------------------------- metrics
def dcg(labels: list[int], k: int) -> float:
    return sum((2.0 ** rel - 1.0) / math.log2(i + 2) for i, rel in enumerate(labels[:k]))


def ndcg(labels: list[int], scores: list[float], k: int) -> float:
    order = sorted(range(len(labels)), key=lambda i: (-scores[i], i))
    ideal = dcg(sorted(labels, reverse=True), k)
    return dcg([labels[i] for i in order], k) / ideal if ideal > 0 else float("nan")


def evaluate(groups: list[dict[str, Any]], score_fn, label_key: str = "clean") -> dict[str, Any]:
    n5, n10, mrr, viol = [], [], [], []
    for g in groups:
        labels = g[label_key]
        if max(labels) == 0:
            continue
        scores = list(score_fn(g))
        order = sorted(range(len(labels)), key=lambda i: (-scores[i], i))
        n5.append(ndcg(labels, scores, 5))
        n10.append(ndcg(labels, scores, 10))
        rr = 0.0
        for rank, i in enumerate(order, 1):
            if labels[i] == 3:
                rr = 1.0 / rank
                break
        mrr.append(rr)
        top = order[:5]
        viol.append(sum(g["viol"][i] for i in top) / len(top))
    rng = np.random.default_rng(SEED)
    arr = np.array(n5)
    boots = [float(rng.choice(arr, size=len(arr), replace=True).mean()) for _ in range(1000)]
    return {
        "queries": len(n5),
        "ndcg@5": round(float(arr.mean()), 4),
        "ndcg@5_ci95": [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)],
        "ndcg@10": round(float(np.mean(n10)), 4),
        "mrr_grade3": round(float(np.mean(mrr)), 4),
        "hard_violation_rate@5": round(float(np.mean(viol)), 4),
    }


# ----------------------------------------------------------------- data
def load_catalog(catalog_dir: Path) -> tuple[list[dict], list[dict], dict]:
    recipes = json.loads((catalog_dir / "recipes.json").read_text(encoding="utf-8"))
    ings = json.loads((catalog_dir / "recipe_ingredients.json").read_text(encoding="utf-8"))
    manifest = json.loads((catalog_dir / "catalog_manifest.json").read_text(encoding="utf-8"))
    return recipes, ings, manifest


def build_groups(n_pantries: int, cg: CandidateGenerator, alias_index: dict) -> tuple[list[dict], list[dict]]:
    groups, pantries = [], []
    for idx in range(n_pantries):
        pantry = generate_life_pantry(idx)
        pantry["items"] = resolve_pantry_items(pantry["items"], alias_index)
        profile = scenario_profile(pantry["scenario_type"])
        cands = cg.retrieve_candidates(pantry["items"], top_n=35)
        rows, clean, noisy, rids, viol = [], [], [], [], []
        for recipe in cands:
            r_ings = cg.recipe_ingredients.get(recipe["id"], [])
            feats = extract_contextual_features(pantry, recipe, r_ings, None)
            signals = scenario_signals(pantry, recipe, r_ings)
            grade = teacher_grade(profile, {**feats, **signals})
            rows.append([feats[c] for c in FEATURE_COLS])
            clean.append(grade)
            noisy.append(noisy_grade(grade, f"{pantry['pantry_id']}|{recipe['id']}", LABEL_NOISE))
            rids.append(recipe["id"])
            viol.append(signals["hard_violation"])
        pantries.append(pantry)
        if len(rows) >= 3:
            groups.append({
                "pantry_id": pantry["pantry_id"], "scenario": pantry["scenario_type"],
                "segment": pantry["scenario_group"], "X": rows, "clean": clean, "noisy": noisy,
                "viol": viol, "recipe_ids": rids, "retrieval_rank": list(range(len(rids))),
            })
    return groups, pantries


def split_groups(groups: list[dict]) -> dict[str, list[dict]]:
    rng = random.Random(SEED)
    by_scen = collections.defaultdict(list)
    for g in groups:
        by_scen[g["scenario"]].append(g)
    split = {"train": [], "val": [], "test": []}
    for scen in sorted(by_scen):
        gs = list(by_scen[scen])
        rng.shuffle(gs)
        n = len(gs)
        n_test, n_val = max(1, round(n * 0.15)), max(1, round(n * 0.15))
        split["test"] += gs[:n_test]
        split["val"] += gs[n_test:n_test + n_val]
        split["train"] += gs[n_test + n_val:]
    for name, gs in split.items():
        for g in gs:
            g["split"] = name
    return split


def trainable(groups: list[dict], label_key: str) -> list[dict]:
    return [g for g in groups if len(set(g[label_key])) > 1]


def to_dataset(groups: list[dict], cols: list[int], label_key: str) -> lgb.Dataset:
    X = np.array([[row[i] for i in cols] for g in groups for row in g["X"]], dtype=float)
    y = np.array([lbl for g in groups for lbl in g[label_key]], dtype=float)
    return lgb.Dataset(X, label=y, group=[len(g[label_key]) for g in groups],
                       feature_name=[FEATURE_COLS[i] for i in cols], free_raw_data=False)


def base_params(cols: list[int]) -> dict[str, Any]:
    return {
        "objective": "lambdarank", "metric": "ndcg", "eval_at": [5, 10],
        "learning_rate": 0.05, "feature_fraction": 0.9, "bagging_fraction": 0.9, "bagging_freq": 1,
        "monotone_constraints": [MONOTONE_CONSTRAINTS[i] for i in cols],
        "lambdarank_truncation_level": 20, "seed": SEED, "deterministic": True,
        "num_threads": 4, "verbose": -1,
    }


def fit(train: list[dict], val: list[dict], cols: list[int]) -> tuple[tuple[float, dict, int], list[dict]]:
    """Grid search on validation NDCG@5 with early stopping."""
    dtrain = to_dataset(trainable(train, "noisy"), cols, "noisy")
    dval = to_dataset(trainable(val, "clean"), cols, "clean")
    trials, best = [], None
    for grid in GRID:
        params = dict(base_params(cols), **grid)
        model = lgb.train(params, dtrain, num_boost_round=600, valid_sets=[dval],
                          callbacks=[lgb.early_stopping(50, verbose=False)])
        score = model.best_score["valid_0"]["ndcg@5"]
        trials.append({**grid, "best_iteration": model.best_iteration, "val_ndcg@5": round(score, 4)})
        if best is None or score > best[0]:
            best = (score, params, model.best_iteration)
    return best, trials


def predictor(model: lgb.Booster, cols: list[int]):
    return lambda g: model.predict(np.array([[row[i] for i in cols] for row in g["X"]], dtype=float))


# ----------------------------------------------------------------- outputs
def write_dataset(groups: list[dict], pantries: list[dict], catalog_dir: Path) -> dict[str, Any]:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(DATASET_DIR / "pantries.jsonl.gz", "wt", encoding="utf-8", newline="\n") as fh:
        for p in pantries:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    with gzip.open(DATASET_DIR / "pairs.csv.gz", "wt", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["pantry_id", "scenario", "segment", "split", "retrieval_rank", "recipe_id",
                    "grade_clean", "grade_noisy", *FEATURE_COLS])
        for g in groups:
            for i, rid in enumerate(g["recipe_ids"]):
                w.writerow([g["pantry_id"], g["scenario"], g["segment"], g["split"], i, rid,
                            g["clean"][i], g["noisy"][i], *g["X"][i]])
    return {
        "pantries_file": str((DATASET_DIR / "pantries.jsonl.gz").relative_to(ROOT)).replace("\\", "/"),
        "pairs_file": str((DATASET_DIR / "pairs.csv.gz").relative_to(ROOT)).replace("\\", "/"),
        "catalog_dir": str(catalog_dir.relative_to(ROOT)).replace("\\", "/"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--catalog-dir", type=Path, default=DEFAULT_CATALOG)
    ap.add_argument("--pantries", type=int, default=len(SCHEDULE) * 50)
    ap.add_argument("--report-dir", type=Path, default=None)
    args = ap.parse_args()
    t0 = time.time()
    catalog_dir = args.catalog_dir.resolve()
    report_dir = args.report_dir or ROOT / "reports" / "eda" / f"catalog_ranker_{time.strftime('%Y%m%dT%H%M%S')}"
    report_dir.mkdir(parents=True, exist_ok=True)

    recipes, ings, manifest = load_catalog(catalog_dir)
    with MASTER_CSV.open(encoding="utf-8", newline="") as fh:
        alias_index = build_master_alias_index(list(csv.DictReader(fh)))
    cg = CandidateGenerator(recipes, ings)
    print(f"Catalog {catalog_dir.name}: {len(recipes)} recipes, {len(ings)} ingredient rows")

    groups, pantries = build_groups(args.pantries, cg, alias_index)
    split = split_groups(groups)
    dataset_info = write_dataset(groups, pantries, catalog_dir)
    grade_dist = collections.Counter(l for g in groups for l in g["clean"])
    print(f"{len(pantries)} pantries -> {len(groups)} query groups, "
          f"{sum(len(g['clean']) for g in groups)} pairs, grades {dict(sorted(grade_dist.items()))}")

    all_cols = list(range(len(FEATURE_COLS)))

    # Hyperparameters on validation, then refit on train+val with the best iteration.
    (best_score, best_params, best_iter), trials = fit(split["train"], split["val"], all_cols)
    final = lgb.train(best_params, to_dataset(trainable(split["train"] + split["val"], "noisy"), all_cols, "noisy"),
                      num_boost_round=best_iter)

    test = split["test"]
    rand = random.Random(SEED)
    model_key = f"lambdamart_{len(FEATURE_COLS)}feat"
    results = {
        model_key: evaluate(test, predictor(final, all_cols)),
        "random": evaluate(test, lambda g: [rand.random() for _ in g["clean"]]),
        "retrieval_order": evaluate(test, lambda g: [-r for r in g["retrieval_rank"]]),
        "core_coverage": evaluate(test, lambda g: [row[0] for row in g["X"]]),
        "core_coverage_minus_violation": evaluate(
            test, lambda g: [row[0] - 2 * v for row, v in zip(g["X"], g["viol"])]),
    }
    if PREVIOUS_9FEAT_MODEL.exists():
        old = lgb.Booster(model_file=str(PREVIOUS_9FEAT_MODEL))
        results["previous_production_v2.1.0"] = evaluate(test, predictor(old, all_cols))
    results["label_noise_ceiling"] = evaluate(test, lambda g: [l + 1e-6 * -i for i, l in enumerate(g["noisy"])])

    segments = {}
    for seg in sorted({g["segment"] for g in test}):
        sub = [g for g in test if g["segment"] == seg]
        segments[seg] = {"model": evaluate(sub, predictor(final, all_cols)),
                         "core_coverage": evaluate(sub, lambda g: [row[0] for row in g["X"]])}
    per_scenario = {}
    for scen in sorted({g["scenario"] for g in test}):
        sub = [g for g in test if g["scenario"] == scen]
        per_scenario[scen] = evaluate(sub, predictor(final, all_cols))["ndcg@5"]

    # Leave-scenario-out: train without the held-out situations, test on all their groups.
    seen = lambda gs: [g for g in gs if g["scenario"] not in HOLDOUT_SCENARIOS]
    (_, h_params, h_iter), _ = fit(seen(split["train"]), seen(split["val"]), all_cols)
    h_model = lgb.train(h_params, to_dataset(trainable(seen(split["train"] + split["val"]), "noisy"), all_cols, "noisy"),
                        num_boost_round=h_iter)
    unseen = [g for g in groups if g["scenario"] in HOLDOUT_SCENARIOS]
    generalisation = {
        "holdout_scenarios": HOLDOUT_SCENARIOS,
        "model_trained_without_them": evaluate(unseen, predictor(h_model, all_cols)),
        "core_coverage": evaluate(unseen, lambda g: [row[0] for row in g["X"]]),
    }

    gains = final.feature_importance(importance_type="gain")
    feat_gain = {c: round(float(v), 1) for c, v in sorted(zip(FEATURE_COLS, gains), key=lambda x: -x[1])}

    # Persist model (previous one archived once) and metadata.
    if MODEL_TXT.exists():
        archive = MODEL_TXT.parent / "archive"
        archive.mkdir(exist_ok=True)
        old_meta = json.loads(METADATA_JSON.read_text(encoding="utf-8")) if METADATA_JSON.exists() else {}
        tag = f"v{old_meta.get('version', 'unknown')}"
        if not (archive / f"lgbm_contextual_{tag}.txt").exists():
            shutil.copy2(MODEL_TXT, archive / f"lgbm_contextual_{tag}.txt")
            if METADATA_JSON.exists():
                shutil.copy2(METADATA_JSON, archive / f"metadata_{tag}.json")
    final.save_model(str(MODEL_TXT))
    n_student = sum(1 for p in pantries if p["scenario_group"] == STUDENT)
    metadata = {
        "version": "3.1.0",
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "recipe_set": "curated catalog",
        "catalog_export": catalog_dir.name,
        "catalog_fingerprint": manifest.get("corpus_fingerprint"),
        "catalog_recipes": len(recipes),
        "scenarios_count": len(SCENARIOS),
        "student_scenarios": sum(1 for s in SCENARIOS if s["group"] == STUDENT),
        "pantries": len(pantries),
        "student_pantry_share": round(n_student / len(pantries), 3),
        "query_groups": {k: len(v) for k, v in split.items()},
        "pairs": sum(len(g["clean"]) for g in groups),
        "grade_distribution": {str(k): v for k, v in sorted(grade_dist.items())},
        "label": "scenario_rules.teacher_grade (0-3); training labels with deterministic noise rate "
                 f"{LABEL_NOISE}, evaluation on clean grades",
        "feature_cols": FEATURE_COLS,
        "monotone_constraints": MONOTONE_CONSTRAINTS,
        "params": {k: v for k, v in best_params.items() if k not in ("monotone_constraints",)},
        "num_boost_round": best_iter,
        "test": results[model_key],
        "feature_gain": feat_gain,
        "dataset": dataset_info,
    }
    METADATA_JSON.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "metadata": metadata,
        "validation_grid": trials,
        "test_results": results,
        "segments": segments,
        "per_scenario_ndcg@5": per_scenario,
        "leave_scenario_out": generalisation,
        "runtime_s": round(time.time() - t0, 1),
    }
    (report_dir / "eval.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Best grid {best_params['num_leaves']} leaves / {best_params['min_data_in_leaf']} min_data, "
          f"{best_iter} rounds, val NDCG@5 {best_score:.4f}")
    for name, r in results.items():
        print(f"  {name:32s} NDCG@5 {r['ndcg@5']:.4f} {r['ndcg@5_ci95']}  NDCG@10 {r['ndcg@10']:.4f}  "
              f"MRR {r['mrr_grade3']:.4f}  viol@5 {r['hard_violation_rate@5']:.4f}")
    g = generalisation["model_trained_without_them"]
    print(f"  leave-scenario-out               NDCG@5 {g['ndcg@5']:.4f} vs core_coverage "
          f"{generalisation['core_coverage']['ndcg@5']:.4f}")
    print(f"Saved {MODEL_TXT.relative_to(ROOT)}, {METADATA_JSON.relative_to(ROOT)}, {report_dir.relative_to(ROOT)}/eval.json")


if __name__ == "__main__":
    main()
