"""Match pantry batches to recipe ingredients the same way recommendations do.

Recommendations match pantry items to recipe lines by name/synonym, while cooking
used to require the exact master ingredient id. A pantry "Thịt bò" then looked
ready in the recommendation but missing ("Thịt bò nạc") in the cook preview.
Cooking now accepts a batch when its master id is equal or its name aliases
overlap with the recipe line's, using the AI package's own alias expansion.
"""

from sqlalchemy import inspect

from AI.recommendation.candidate_generator import extract_pantry_name_aliases
from src.model.inventory_batch_model import InventoryBatchModel
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.recipe_ingredient_model import RecipeIngredientModel


def _aliases(*names: object) -> frozenset[str]:
    found: set[str] = set()
    for name in names:
        if isinstance(name, str) and name.strip():
            found |= extract_pantry_name_aliases(name)
    return frozenset(found)


def recipe_line_aliases(
    recipe_ingredient: RecipeIngredientModel,
    ingredient: MasterIngredientModel,
) -> frozenset[str]:
    """Names a pantry item may carry to satisfy this recipe line."""
    attributes = recipe_ingredient.ai_attributes or {}
    return _aliases(ingredient.name, attributes.get("cleaned_name"))


def batch_aliases(batch: InventoryBatchModel) -> frozenset[str]:
    """Names under which a pantry batch is known (master name or custom name)."""
    names: list[object] = [batch.custom_name]
    if "master_ingredient" not in inspect(batch).unloaded:
        master = batch.master_ingredient
        if master is not None:
            names.append(master.name)
    return _aliases(*names)


def batch_matches_line(
    batch: InventoryBatchModel,
    recipe_ingredient: RecipeIngredientModel,
    ingredient: MasterIngredientModel,
) -> bool:
    """Return whether a batch can satisfy the recipe line."""
    if batch.master_ingredient_id == ingredient.id:
        return True
    return bool(
        recipe_line_aliases(recipe_ingredient, ingredient) & batch_aliases(batch)
    )
