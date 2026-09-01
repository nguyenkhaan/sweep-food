"""Request and response DTOs for the master-ingredient catalog."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.model.enum_model import MeasurementUnit, ShelfLifeRuleScope, StorageMode


class IngredientCategoryDTO(BaseModel):
    """The public category associated with one catalog ingredient."""

    id: UUID
    name: str


class IngredientNutritionDTO(BaseModel):
    """Nutrition values supplied by the curated ingredient catalog."""

    calories: Decimal | None
    protein_g: Decimal | None
    fat_g: Decimal | None
    carbs_g: Decimal | None
    sugar_g: Decimal | None
    sodium_mg: Decimal | None
    other_nutrients: dict[str, object]


class ShelfLifeRuleDTO(BaseModel):
    """One seeded shelf-life rule applicable to an ingredient or category."""

    scope: ShelfLifeRuleScope
    storage_mode: StorageMode
    min_days: int
    max_days: int
    default_days: int


class IngredientListItemDTO(BaseModel):
    """Compact catalog ingredient returned by authenticated search."""

    id: UUID
    name: str
    category: IngredientCategoryDTO
    default_unit: MeasurementUnit
    default_storage_mode: StorageMode | None
    aliases: list[str]


class IngredientDetailDTO(IngredientListItemDTO):
    """Complete public catalog details for one canonical ingredient."""

    description: str
    default_media_url: str | None
    nutrition: IngredientNutritionDTO
    shelf_life_rules: list[ShelfLifeRuleDTO]


class IngredientListResponseDTO(BaseModel):
    """A stable page of catalog search results."""

    items: list[IngredientListItemDTO]
    total: int
    page: int
    per_page: int
