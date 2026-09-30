"""Shared recommendation response mappings."""

from src.model.recipe_model import RecipeModel
from src.module.recipes.recipe_dto import RecipeNutritionDTO
from src.module.recommendations.recommendation_dto import (
    RecommendationRecipeSummaryDTO,
)


def to_recipe_summary(recipe: RecipeModel) -> RecommendationRecipeSummaryDTO:
    """Map a catalog recipe to the recommendation card contract."""
    return RecommendationRecipeSummaryDTO(
        id=recipe.id,
        name=recipe.name,
        media_url=recipe.media_url,
        estimated_cooking_minutes=recipe.estimated_cooking_minutes,
        default_servings=recipe.default_servings,
        nutrition=RecipeNutritionDTO(
            calories=recipe.total_calories,
            protein_g=recipe.total_protein_g,
            fat_g=recipe.total_fat_g,
            carbs_g=recipe.total_carbs_g,
            sugar_g=recipe.total_sugar_g,
            other_nutrients=recipe.other_nutrients,
        ),
    )
