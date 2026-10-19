"""Pure, typed, testable RecommendationEngine for SweepFood AI."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from AI.catalog.master_index import resolve_pantry_items
from AI.catalog.snapshot import CatalogSnapshot
from AI.recommendation.candidate_generator import CandidateGenerator
from AI.recommendation.formatting import format_candidate_recommendation
from AI.recommendation.ranking import (
    RankerInference,
    feasibility_rank_key,
    select_urgent_round_robin,
)
from AI.recommendation.scenario_rules import filter_candidate

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EngineTimings:
    total_ms: float
    candidate_ms: float
    ranker_ms: float

    def model_dump(self) -> dict[str, float]:
        return {
            "total_ms": self.total_ms,
            "candidate_ms": self.candidate_ms,
            "ranker_ms": self.ranker_ms,
        }


@dataclass(frozen=True)
class EngineIngredient:
    name: str
    code: str | None
    required_g: float

    def model_dump(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "code": self.code,
            "required_g": self.required_g,
        }


@dataclass(frozen=True)
class EngineRankingFeatures:
    core_coverage: float
    core_missing_count: float
    secondary_coverage: float
    shopping_gap_items: float
    rescue_weight_g: float
    nutrition_confidence: float
    kcal_per_serving: float
    protein_per_serving: float
    prep_complexity: float

    def model_dump(self) -> dict[str, float]:
        return {
            "core_coverage": self.core_coverage,
            "core_missing_count": self.core_missing_count,
            "secondary_coverage": self.secondary_coverage,
            "shopping_gap_items": self.shopping_gap_items,
            "rescue_weight_g": self.rescue_weight_g,
            "nutrition_confidence": self.nutrition_confidence,
            "kcal_per_serving": self.kcal_per_serving,
            "protein_per_serving": self.protein_per_serving,
            "prep_complexity": self.prep_complexity,
        }


@dataclass(frozen=True)
class EngineRecommendation:
    id: UUID
    name: str
    rank_score: float
    ranking_features: EngineRankingFeatures
    matched_ingredients: list[EngineIngredient]
    missing_ingredients: list[EngineIngredient]
    optional_ingredients: list[EngineIngredient]
    rescued_items: list[str]
    status_badge: str


@dataclass(frozen=True)
class EngineResult:
    status: Literal["success", "empty"]
    contract_version: str
    model_version: str
    catalog_revision: str
    ranker_model: str
    timings: EngineTimings
    recommendations: list[EngineRecommendation]
    message: str = ""


class RecommendationEngine:
    """Core recommendation pipeline: pantry resolve -> retrieval -> filters -> rank -> format."""

    def __init__(
        self,
        snapshot: CatalogSnapshot,
        model_path: str | Path | None = None,
    ) -> None:
        self.snapshot = snapshot
        self.candidate_generator = CandidateGenerator(
            snapshot.recipes,
            snapshot.ingredients,
        )
        self.ranker = RankerInference(model_path=model_path)
        self.categories_map: dict[str, str] = {
            code: str(m.get("category_vi") or "")
            for code, m in snapshot.master_by_code.items()
        }

    def recommend(self, request: Any) -> EngineResult:
        """Run candidate retrieval, scenario filters, ranker scoring, and tiered selection."""
        t0 = time.perf_counter()

        if hasattr(request, "model_dump"):
            req_dict = request.model_dump()
        elif isinstance(request, dict):
            req_dict = request
        else:
            req_dict = {}

        raw_items: list[dict[str, Any]] = req_dict.get("items", [])
        household_size = float(req_dict.get("household_size") or 4.0)
        scenario_type = str(req_dict.get("scenario_type") or "custom")

        resolved_items = resolve_pantry_items(
            raw_items,
            self.snapshot.master_alias_index,
        )
        pantry_dict: dict[str, Any] = {
            "pantry_id": "live_user_query",
            "scenario_type": scenario_type,
            "items": resolved_items,
            "household_size": household_size,
        }

        # 1. Candidate Retrieval via Inverted Index
        t_cand_start = time.perf_counter()
        raw_candidates = self.candidate_generator.retrieve_candidates(
            pantry_dict["items"],
            top_n=35,
        )
        cand_time_ms = round((time.perf_counter() - t_cand_start) * 1000, 2)

        if not raw_candidates:
            total_time_ms = round((time.perf_counter() - t0) * 1000, 2)
            return EngineResult(
                status="empty",
                contract_version="2",
                model_version=self.ranker.model_version_string,
                catalog_revision=self.snapshot.revision,
                ranker_model=self.ranker.ranker_model_name,
                timings=EngineTimings(
                    total_ms=total_time_ms,
                    candidate_ms=cand_time_ms,
                    ranker_ms=0.0,
                ),
                recommendations=[],
                message="Không tìm thấy món ăn phù hợp với nguyên liệu hiện tại. Thử thêm thịt, cá hoặc rau nhé!",
            )

        # 2. Hard Constraint Filtering Layer
        scenario_clean = scenario_type.lower().strip()
        filtered_candidates: list[dict[str, Any]] = []
        for cand in raw_candidates:
            r_id = str(cand["id"])
            r_ings = self.snapshot.ingredients_by_recipe.get(r_id, [])
            if filter_candidate(cand, scenario_clean, r_ings, self.categories_map):
                filtered_candidates.append(cand)

        if not filtered_candidates:
            total_time_ms = round((time.perf_counter() - t0) * 1000, 2)
            return EngineResult(
                status="empty",
                contract_version="2",
                model_version=self.ranker.model_version_string,
                catalog_revision=self.snapshot.revision,
                ranker_model=self.ranker.ranker_model_name,
                timings=EngineTimings(
                    total_ms=total_time_ms,
                    candidate_ms=cand_time_ms,
                    ranker_ms=0.0,
                ),
                recommendations=[],
                message="Không tìm thấy món ăn phù hợp với yêu cầu dinh dưỡng và nguyên liệu hiện tại.",
            )

        # 3. Model Scoring (LightGBM or Domain Heuristic Fallback)
        t_rank_start = time.perf_counter()
        scores, features_list = self.ranker.score_candidates(
            pantry_dict,
            filtered_candidates,
            self.snapshot.ingredients_by_recipe,
        )
        rank_time_ms = round((time.perf_counter() - t_rank_start) * 1000, 2)

        # 4. Format and Rank Candidates
        scored_candidates: list[dict[str, Any]] = []
        for cand, score, feats in zip(filtered_candidates, scores, features_list):
            r_id = str(cand["id"])
            full_rec = self.snapshot.recipes_by_id.get(r_id, cand)
            r_ings = self.snapshot.ingredients_by_recipe.get(r_id, [])
            formatted = format_candidate_recommendation(
                cand=cand,
                full_rec=full_rec,
                score=score,
                feats=feats,
                r_ings=r_ings,
                pantry_dict=pantry_dict,
                household_size=household_size,
            )
            scored_candidates.append(formatted)

        # Feasibility-First Tiered Sorting
        scored_candidates.sort(key=feasibility_rank_key)

        # Multi-Urgent Round-Robin Diversity Selection
        top_candidates = select_urgent_round_robin(
            scored_candidates,
            pantry_dict["items"],
            top_k=7,
        )

        recommendations: list[EngineRecommendation] = []
        for cand in top_candidates:
            rec_id = UUID(str(cand["id"]))
            feats_dict = cand["ranking_features"]
            recommendations.append(
                EngineRecommendation(
                    id=rec_id,
                    name=str(cand["name"]),
                    rank_score=float(cand["rank_score"]),
                    ranking_features=EngineRankingFeatures(
                        core_coverage=float(feats_dict.get("core_coverage", 0.0)),
                        core_missing_count=float(feats_dict.get("core_missing_count", 0.0)),
                        secondary_coverage=float(feats_dict.get("secondary_coverage", 0.0)),
                        shopping_gap_items=float(feats_dict.get("shopping_gap_items", 0.0)),
                        rescue_weight_g=float(feats_dict.get("rescue_weight_g", 0.0)),
                        nutrition_confidence=float(feats_dict.get("nutrition_confidence", 0.0)),
                        kcal_per_serving=float(feats_dict.get("kcal_per_serving", 0.0)),
                        protein_per_serving=float(feats_dict.get("protein_per_serving", 0.0)),
                        prep_complexity=float(feats_dict.get("prep_complexity", 0.0)),
                    ),
                    matched_ingredients=[
                        EngineIngredient(
                            name=str(ing["name"]),
                            code=str(ing["code"]) if ing.get("code") else None,
                            required_g=float(ing.get("required_g", 0.0)),
                        )
                        for ing in cand.get("matched_ingredients", [])
                    ],
                    missing_ingredients=[
                        EngineIngredient(
                            name=str(ing["name"]),
                            code=str(ing["code"]) if ing.get("code") else None,
                            required_g=float(ing.get("required_g", 0.0)),
                        )
                        for ing in cand.get("missing_ingredients", [])
                    ],
                    optional_ingredients=[
                        EngineIngredient(
                            name=str(ing["name"]),
                            code=str(ing["code"]) if ing.get("code") else None,
                            required_g=float(ing.get("required_g", 0.0)),
                        )
                        for ing in cand.get("optional_ingredients", [])
                    ],
                    rescued_items=[str(x) for x in cand.get("rescued_items", [])],
                    status_badge=str(cand.get("status_badge", "shopping")),
                )
            )

        total_time_ms = round((time.perf_counter() - t0) * 1000, 2)

        return EngineResult(
            status="success",
            contract_version="2",
            model_version=self.ranker.model_version_string,
            catalog_revision=self.snapshot.revision,
            ranker_model=self.ranker.ranker_model_name,
            timings=EngineTimings(
                total_ms=total_time_ms,
                candidate_ms=cand_time_ms,
                ranker_ms=rank_time_ms,
            ),
            recommendations=recommendations,
        )
