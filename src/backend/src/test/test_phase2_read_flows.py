"""Focused contracts for the Phase 2 read and mock-response flows."""

from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast
from uuid import UUID

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import (
    MeasurementUnit,
    ShoppingListStatus,
    StorageMode,
    UserRole,
)
from src.model.master_ingredient_model import MasterIngredientModel
from src.model.shopping_list_item_model import ShoppingListItemModel
from src.module.extractions.extraction_dto import ExtractionStatus
from src.module.extractions.extraction_provider import mock_barcode_lookup
from src.module.inventory.inventory_dto import CreateInventoryBatchRequestDTO
from src.module.inventory.inventory_service import InventoryService
from src.module.recommendations.recommendation_dto import RecommendationRequestDTO
from src.module.recommendations.recommendation_service import RecommendationService
from src.module.shopping_lists.shopping_dependency import get_shopping_service
from src.module.shopping_lists.shopping_dto import (
    ShoppingListCollectionResponseDTO,
    ShoppingListQueryDTO,
    ShoppingListSummaryDTO,
    ShoppingPurchaseDTO,
)
from src.module.shopping_lists.shopping_service import ShoppingService

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b101")
LIST_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b103")
ITEM_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b104")
INGREDIENT_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b105")
BATCH_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5b106")
NOW = datetime(2026, 9, 7, 9, 0, tzinfo=UTC)


class FakeShoppingCollectionService:
    """Return a stable owned-list collection without database I/O."""

    query: ShoppingListQueryDTO | None = None

    async def list_lists(
        self,
        user_id: UUID,
        query: ShoppingListQueryDTO,
    ) -> ShoppingListCollectionResponseDTO:
        """Record collection filters and return one summary row."""
        assert user_id == USER_ID
        self.query = query
        return ShoppingListCollectionResponseDTO(
            items=[
                ShoppingListSummaryDTO(
                    id=LIST_ID,
                    meal_plan_id=None,
                    status=ShoppingListStatus.ACTIVE,
                    generated_at=NOW,
                    created_at=NOW,
                    updated_at=NOW,
                )
            ],
            total=1,
            limit=query.limit,
            offset=query.offset,
        )


@pytest.fixture(name="phase2_shopping_routes")
async def _phase2_shopping_routes() -> AsyncGenerator[FakeShoppingCollectionService, None]:
    """Expose the collection route with authenticated fake dependencies."""
    service = FakeShoppingCollectionService()

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    def get_service() -> FakeShoppingCollectionService:
        return service

    app.dependency_overrides[require_authentication] = get_authenticated_user
    app.dependency_overrides[get_shopping_service] = get_service
    try:
        yield service
    finally:
        app.dependency_overrides.pop(require_authentication, None)
        app.dependency_overrides.pop(get_shopping_service, None)
        app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_shopping_collection_returns_summaries_and_validates_queries(
    api_client: httpx.AsyncClient,
    phase2_shopping_routes: FakeShoppingCollectionService,
) -> None:
    """The collection route accepts only bounded, user-scoped query values."""
    response = await api_client.get(
        "/api/shopping-lists",
        params={"status": "ACTIVE", "limit": 1, "offset": 0},
    )
    invalid = await api_client.get(
        "/api/shopping-lists",
        params={"status": "UNKNOWN", "limit": 101},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == str(LIST_ID)
    assert response.json()["items"][0].get("items") is None
    assert phase2_shopping_routes.query is not None
    assert phase2_shopping_routes.query.list_status is ShoppingListStatus.ACTIVE
    assert invalid.status_code == 422


class FakeInventoryService:
    """Capture a staged purchase request without persisting inventory."""

    requests: list[CreateInventoryBatchRequestDTO]

    def __init__(self) -> None:
        self.requests = []

    async def stage_batch(
        self,
        _user_id: UUID,
        body: CreateInventoryBatchRequestDTO,
        _idempotency_key: str,
        *,
        reason: str,
    ) -> object:
        """Retain the resolved request and return a batch-like object."""
        assert reason == "Shopping item purchase"
        self.requests.append(body)
        return type("StagedBatch", (), {"id": BATCH_ID})()


def _shopping_item() -> ShoppingListItemModel:
    """Build an unchecked catalog-backed shopping line for purchase tests."""
    return ShoppingListItemModel(
        id=ITEM_ID,
        shopping_list_id=LIST_ID,
        master_ingredient_id=INGREDIENT_ID,
        custom_name=None,
        required_quantity=200.0,
        available_quantity=0.0,
        missing_quantity=200.0,
        unit=MeasurementUnit.GRAM,
        estimated_cost=None,
        is_checked=False,
        source_metadata={"generated": False, "recipe_ids": []},
    )


@pytest.mark.anyio
async def test_purchase_uses_catalog_default_and_rejects_missing_default() -> None:
    """An omitted storage mode resolves only from a catalog ingredient default."""
    inventory = FakeInventoryService()
    service = ShoppingService(
        cast(AsyncSession, object()),
        cast(InventoryService, inventory),
    )
    ingredient = MasterIngredientModel(
        id=INGREDIENT_ID,
        default_storage_mode=StorageMode.REFRIGERATED,
    )
    item = _shopping_item()

    await service._check_item(USER_ID, item, ingredient, ShoppingPurchaseDTO(), "key")

    assert item.is_checked is True
    assert inventory.requests[0].storage_mode is StorageMode.REFRIGERATED

    with pytest.raises(HTTPException, match="storage_mode") as error:
        await service._check_item(
            USER_ID,
            _shopping_item(),
            None,
            ShoppingPurchaseDTO(),
            "missing-default",
        )

    assert error.value.status_code == 422
    assert len(inventory.requests) == 1


class FakeRecipe:
    """Contain exactly the recipe card data read by recommendation mapping."""

    def __init__(self) -> None:
        self.id = INGREDIENT_ID
        self.name = "Spinach soup"
        self.media_url = None
        self.estimated_cooking_minutes = 15
        self.default_servings = Decimal("2.00")
        self.total_calories = Decimal("198.000")
        self.total_protein_g = Decimal("22.000")
        self.total_fat_g = Decimal("10.400")
        self.total_carbs_g = Decimal("11.000")
        self.total_sugar_g = Decimal("2.000")
        self.other_nutrients = {"fiber_g": 5.0}


class FakeRecommendationResult:
    """Expose the scalar result used by the mock recommendation query."""

    def scalars(self) -> "FakeRecommendationResult":
        """Return this result as its scalar collection."""
        return self

    def all(self) -> list[FakeRecipe]:
        """Return one already-loaded recipe card."""
        return [FakeRecipe()]


class FakeRecommendationSession:
    """Count recipe queries while returning an already-loaded recipe."""

    calls: int = 0

    async def execute(self, _statement: object) -> FakeRecommendationResult:
        """Record the single catalog query used by recommendation mapping."""
        self.calls += 1
        return FakeRecommendationResult()


@pytest.mark.anyio
async def test_mock_recommendation_populates_recipe_summary_without_extra_query() -> None:
    """Each mock item reuses its selected RecipeModel as the display card."""
    session = FakeRecommendationSession()
    service = RecommendationService(cast(AsyncSession, session))

    response = await service.recommend(USER_ID, RecommendationRequestDTO(request="Súp"))

    summary = response.items[0].recipe_summary
    assert summary is not None
    assert summary.id == INGREDIENT_ID
    assert summary.default_servings == Decimal("2.00")
    assert summary.nutrition.calories == Decimal("198.000")
    assert session.calls == 1


@pytest.fixture(name="phase2_extraction_routes")
def _phase2_extraction_routes() -> Generator[None, None, None]:
    """Authenticate the barcode route without reaching external services."""

    async def get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(USER_ID, (UserRole.USER,))

    app.dependency_overrides[require_authentication] = get_authenticated_user
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_authentication, None)


@pytest.mark.anyio
async def test_unknown_barcode_is_a_failed_mock_response(
    api_client: httpx.AsyncClient,
    phase2_extraction_routes: None,
) -> None:
    """A documented miss keeps HTTP 200 while returning no product fields."""
    response = await api_client.post(
        "/api/extractions/barcode",
        params={"barcode": "unknown-barcode"},
    )
    missing_query = await api_client.post("/api/extractions/barcode")

    direct = mock_barcode_lookup("unknown-barcode")
    assert phase2_extraction_routes is None
    assert response.status_code == 200
    assert response.json()["status"] == ExtractionStatus.FAILED.value
    assert response.json()["fields"]["barcode"] == "unknown-barcode"
    assert response.json()["fields"]["product_name"] is None
    assert response.json()["persisted"] is False
    assert direct.status is ExtractionStatus.FAILED
    assert missing_query.status_code == 422
