"""AI Recommendation package providing candidate generation, ranker inference, and engine."""

from AI.recommendation.candidate_generator import CandidateGenerator
from AI.recommendation.contextual_features import (
    FEATURE_COLS,
    extract_contextual_features,
)
from AI.recommendation.engine import (
    EngineIngredient,
    EngineRankingFeatures,
    EngineRecommendation,
    EngineResult,
    EngineTimings,
    RecommendationEngine,
)
from AI.recommendation.heuristic_baseline import compute_domain_heuristic_score
from AI.recommendation.ingredient_roles import IngredientRole, classify_ingredient_role
from AI.recommendation.quantity_elasticity import compute_quantity_elasticity
from AI.recommendation.ranking import RankerInference
from AI.recommendation.scenario_rules import (
    has_animal_ingredients,
    has_gout_forbidden_ingredients,
)

__all__ = [
    "FEATURE_COLS",
    "CandidateGenerator",
    "EngineIngredient",
    "EngineRankingFeatures",
    "EngineRecommendation",
    "EngineResult",
    "EngineTimings",
    "IngredientRole",
    "RankerInference",
    "RecommendationEngine",
    "classify_ingredient_role",
    "compute_domain_heuristic_score",
    "compute_quantity_elasticity",
    "extract_contextual_features",
    "has_animal_ingredients",
    "has_gout_forbidden_ingredients",
]
