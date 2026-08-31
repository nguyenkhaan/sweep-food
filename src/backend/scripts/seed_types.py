"""Typed seed-pipeline inputs and reporting structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.model.enum_model import MeasurementUnit, ShelfLifeRuleScope, StorageMode


@dataclass(frozen=True)
class AdminSeedConfig:
    """Environment-provided identity for the single bootstrap administrator."""

    name: str
    phone_e164: str
    email: str
    password: str


@dataclass(frozen=True)
class CategorySeed:
    """Natural-keyed category input."""

    key: str
    name: str
    description: str | None


@dataclass(frozen=True)
class NutritionSeed:
    """Approved catalog nutrition values shared by ingredients and recipes."""

    calories: Decimal | None = None
    protein_g: Decimal | None = None
    fat_g: Decimal | None = None
    carbs_g: Decimal | None = None
    sugar_g: Decimal | None = None
    sodium_mg: Decimal | None = None
    other_nutrients: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class IngredientSeed:
    """Natural-keyed master ingredient input."""

    key: str
    category_key: str
    name: str
    description: str
    canonical_unit: MeasurementUnit
    default_storage_mode: StorageMode | None
    nutrition: NutritionSeed = field(default_factory=NutritionSeed)


@dataclass(frozen=True)
class AliasSeed:
    """Natural-keyed alias input."""

    normalized_alias: str
    alias: str
    ingredient_key: str


@dataclass(frozen=True)
class ShelfLifeRuleSeed:
    """One category- or ingredient-scoped shelf-life input."""

    scope: ShelfLifeRuleScope
    target_key: str
    storage_mode: StorageMode
    min_days: int
    max_days: int
    default_days: int


@dataclass(frozen=True)
class RecipeDetailsSeed:
    """Non-key recipe values kept together for one deterministic upsert."""

    description: str
    instructions: dict[str, object]
    default_servings: Decimal
    estimated_cooking_minutes: int
    estimated_cost: float | None
    nutrition: NutritionSeed = field(default_factory=NutritionSeed)
    tags: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RecipeSeed:
    """Natural-keyed recipe input."""

    key: str
    name: str
    details: RecipeDetailsSeed


@dataclass(frozen=True)
class RecipeIngredientSeed:
    """Natural-keyed recipe ingredient input."""

    recipe_key: str
    ingredient_key: str
    required_quantity: Decimal
    unit: MeasurementUnit
    is_optional: bool = False
    preparation_note: str | None = None


@dataclass(frozen=True)
class SeedDataset:
    """The catalog release unit applied atomically by this seed entry point."""

    categories: tuple[CategorySeed, ...]
    ingredients: tuple[IngredientSeed, ...]
    aliases: tuple[AliasSeed, ...]
    shelf_life_rules: tuple[ShelfLifeRuleSeed, ...]
    recipes: tuple[RecipeSeed, ...]
    recipe_ingredients: tuple[RecipeIngredientSeed, ...]


@dataclass
class SeedReport:
    """Classified outcomes for a seed validation or application run."""

    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)

    def add(self, outcome: str, record: str) -> None:
        """Add one classified record outcome."""
        getattr(self, outcome).append(record)

    def summary(self) -> str:
        """Return a secret-free report summary suitable for command output."""
        return (
            f"created={len(self.created)} updated={len(self.updated)} "
            f"unchanged={len(self.unchanged)} rejected={len(self.rejected)}"
        )


@dataclass(frozen=True)
class SeedRunContext:
    """Mutable-operation context shared by all ordered natural-key upserts."""

    session: AsyncSession
    report: SeedReport
    dry_run: bool


class SeedValidationError(ValueError):
    """Expose all rejected seed records without revealing secrets."""

    def __init__(self, report: SeedReport) -> None:
        self.report = report
        details = "; ".join(report.rejected)
        super().__init__(f"Seed validation failed: {details}")
