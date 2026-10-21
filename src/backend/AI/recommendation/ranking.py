"""Feasibility tiering, urgent round-robin diversity, and ranker scoring."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
from lightgbm.basic import LightGBMError

from AI.recommendation.candidate_generator import extract_pantry_name_aliases
from AI.recommendation.contextual_features import (
    FEATURE_COLS,
    extract_contextual_features,
)
from AI.recommendation.heuristic_baseline import compute_domain_heuristic_score

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "training" / "lgbm_contextual.txt"
)
DEFAULT_METADATA_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "training" / "metadata.json"
)


def feasibility_rank_key(c: dict[str, Any]) -> tuple[int, int, float]:
    """Generate sorting tuple for feasibility-first tiered ranking."""
    badge = c.get("status_badge", "shopping")
    is_hero = c.get("is_zero_waste_hero", False)
    n_missing = len(c.get("missing_ingredients", []))
    p_used = c.get("pantry_used_count", 0)

    if badge == "ready" and is_hero:
        tier = 0
    elif badge == "ready":
        tier = 1
    elif is_hero:
        tier = 2
    elif badge == "elastic" and n_missing <= 1:
        tier = 3
    else:
        tier = 4 + min(n_missing, 10)

    score = float(c.get("score") or c.get("rank_score") or 0.0)
    return (tier, -p_used, -score)


def select_urgent_round_robin(
    scored_candidates: list[dict[str, Any]],
    pantry_items: list[dict[str, Any]],
    top_k: int = 7,
) -> list[dict[str, Any]]:
    """Interleave recommendations across urgent expiring items to prevent starvation."""
    urgent_pantry_items = sorted(
        [
            it for it in pantry_items
            if not it.get("is_staple") and float(it.get("hours_to_expire") or 999.0) <= 24.0
        ],
        key=lambda x: float(x.get("hours_to_expire") or 999.0),
    )

    if len(urgent_pantry_items) < 2:
        return scored_candidates[:top_k]

    top_recommendations: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Priority 0: Super-Hero dishes that rescue multiple urgent items
    super_heroes = [
        c for c in scored_candidates
        if len(c.get("rescued_items", [])) >= 2 and c.get("status_badge") in ("ready", "elastic")
    ]
    for sh in super_heroes[:2]:
        top_recommendations.append(sh)
        seen_ids.add(sh["id"])

    # Buckets for each urgent item
    buckets: dict[str, list[dict[str, Any]]] = {
        str(u["name"]).lower(): [] for u in urgent_pantry_items
    }
    for c in scored_candidates:
        if c["id"] in seen_ids:
            continue
        rescued_aliases_list = [
            extract_pantry_name_aliases(r) | {r.strip().lower()}
            for r in c.get("rescued_items", [])
        ]
        for u in urgent_pantry_items:
            u_name = str(u["name"]).lower()
            u_aliases = extract_pantry_name_aliases(u_name) | {u_name.strip()}
            if any(bool(u_aliases & r_aliases) for r_aliases in rescued_aliases_list):
                buckets[u_name].append(c)
                break

    # Round-robin selection across urgent buckets
    max_rounds = 4
    for round_idx in range(max_rounds):
        for u in urgent_pantry_items:
            u_name = str(u["name"]).lower()
            b_list = buckets.get(u_name, [])
            if round_idx < len(b_list):
                cand = b_list[round_idx]
                if cand["id"] not in seen_ids:
                    top_recommendations.append(cand)
                    seen_ids.add(cand["id"])
            if len(top_recommendations) >= top_k:
                break
        if len(top_recommendations) >= top_k:
            break

    # Fill any remaining slots with top scored candidates
    for c in scored_candidates:
        if len(top_recommendations) >= top_k:
            break
        if c["id"] not in seen_ids:
            top_recommendations.append(c)
            seen_ids.add(c["id"])

    return top_recommendations


class RankerInference:
    """Manages the LightGBM Booster and falls back to Domain Heuristic when needed."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        metadata_path: str | Path | None = None,
    ) -> None:
        self.model_path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH
        self.metadata_path = Path(metadata_path) if metadata_path is not None else DEFAULT_METADATA_PATH

        self.booster: Any = None
        self.version: str = "3.1.0"
        self._load_metadata()
        self._load_booster()

    def _load_metadata(self) -> None:
        if self.metadata_path.exists():
            try:
                with self.metadata_path.open("r", encoding="utf-8") as fh:
                    meta = json.load(fh)
                    self.version = str(meta.get("version", "3.1.0"))
            except (json.JSONDecodeError, OSError, KeyError, TypeError) as exc:
                logger.warning("Could not read ranker metadata: %s", exc)

    def _load_booster(self) -> None:
        if not self.model_path.exists():
            logger.info("Model file %s not found; using domain heuristic fallback.", self.model_path)
            self.booster = None
            return

        try:
            booster = lgb.Booster(model_file=str(self.model_path))
            feature_names = booster.feature_name()
            if feature_names != FEATURE_COLS:
                logger.warning(
                    "Booster feature names %s mismatch expected %s; using domain heuristic fallback.",
                    feature_names,
                    FEATURE_COLS,
                )
                self.booster = None
                return
            self.booster = booster
            logger.info("LightGBM ranker loaded successfully (%d features).", len(FEATURE_COLS))
        except (LightGBMError, OSError, ValueError) as exc:
            logger.warning("Failed to load LightGBM ranker (%s); using domain heuristic fallback.", exc)
            self.booster = None

    @property
    def ranker_model_name(self) -> str:
        if self.booster is not None:
            return f"LightGBM LambdaMART ({len(FEATURE_COLS)}-Feature Contextual)"
        return "Domain Heuristic"

    @property
    def model_version_string(self) -> str:
        if self.booster is not None:
            return f"lgbm-contextual-v{self.version}"
        return f"domain-heuristic-v{self.version}"

    def score_candidates(
        self,
        pantry_dict: dict[str, Any],
        candidates: list[dict[str, Any]],
        recipe_ings_map: dict[str, list[dict[str, Any]]],
    ) -> tuple[list[float], list[dict[str, float]]]:
        """Compute ranking scores and extract contextual features for all candidates."""
        features_list: list[dict[str, float]] = []
        lgbm_matrix: list[list[float]] = []

        for cand in candidates:
            r_id = str(cand["id"])
            r_ings = recipe_ings_map.get(r_id, [])
            feats = extract_contextual_features(pantry_dict, cand, r_ings, steps=None)
            features_list.append(feats)
            if self.booster is not None:
                lgbm_matrix.append([feats[col] for col in FEATURE_COLS])

        if self.booster is not None and lgbm_matrix:
            try:
                scores_arr = self.booster.predict(np.array(lgbm_matrix, dtype=np.float64))
                scores = [float(s) for s in scores_arr]
            except (LightGBMError, ValueError, TypeError) as exc:
                logger.warning("LightGBM prediction failed: %s; falling back to domain heuristic.", exc)
                scores = [
                    compute_domain_heuristic_score(
                        pantry_dict,
                        cand,
                        recipe_ings_map.get(str(cand["id"]), []),
                    )
                    for cand in candidates
                ]
        else:
            scores = [
                compute_domain_heuristic_score(
                    pantry_dict,
                    cand,
                    recipe_ings_map.get(str(cand["id"]), []),
                )
                for cand in candidates
            ]

        return scores, features_list
