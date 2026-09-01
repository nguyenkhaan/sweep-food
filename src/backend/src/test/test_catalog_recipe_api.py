"""Seeded integration/API coverage for Task 3.3 catalog and recipe reads."""

from collections.abc import AsyncGenerator
from decimal import Decimal
from typing import cast
from uuid import UUID

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from scripts.seed import AdminSeedConfig, seed_dataset
from src.app import app
from src.db import get_db_session
from src.middleware.auth_middleware import AuthenticatedUser, require_authentication
from src.model.enum_model import UserRole

USER_ID = UUID("018f0f90-26e6-7ce7-8f61-8769f9e5a025")


@pytest.fixture(name="seeded_catalog_api")
async def _seeded_catalog_api(
    database_engine: AsyncEngine,
) -> AsyncGenerator[None, None]:
    """Seed the guarded test database and bind its session to read API routes."""
    async with database_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
            """Provide the guarded seeded session to FastAPI dependencies."""
            yield session

        async def override_authenticated_user() -> AuthenticatedUser:
            """Authorize normal users without changing the seed-backed database."""
            return AuthenticatedUser(USER_ID, (UserRole.USER,))

        try:
            report = await seed_dataset(
                session,
                AdminSeedConfig(
                    name="Catalog API Test Admin",
                    phone_e164="+84123456701",
                    email="catalog-api-admin@example.test",
                    password="catalog-api-test-password",
                ),
            )
            assert not report.rejected
            app.dependency_overrides[get_db_session] = override_db_session
            app.dependency_overrides[require_authentication] = (
                override_authenticated_user
            )
            yield
        finally:
            app.dependency_overrides.pop(get_db_session, None)
            app.dependency_overrides.pop(require_authentication, None)
            await session.close()
            await transaction.rollback()


@pytest.mark.anyio
async def test_ingredient_search_matches_canonical_name_and_alias(
    api_client: httpx.AsyncClient,
    seeded_catalog_api: None,
) -> None:
    """The curated seed aliases resolve to their canonical catalog ingredient."""
    assert seeded_catalog_api is None
    canonical_response = await api_client.get(
        "/api/ingredients", params={"q": "spinach"}
    )
    alias_response = await api_client.get(
        "/api/ingredients",
        params={"q": "BABY SPINACH"},
    )

    assert canonical_response.status_code == 200
    assert alias_response.status_code == 200
    canonical_item = canonical_response.json()["items"][0]
    alias_item = alias_response.json()["items"][0]
    assert canonical_item["name"] == "Spinach"
    assert alias_item["id"] == canonical_item["id"]
    assert alias_item["aliases"] == ["Baby spinach"]

    detail_response = await api_client.get(f"/api/ingredients/{canonical_item['id']}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["name"] == "Spinach"
    assert Decimal(detail["nutrition"]["calories"]) == Decimal("23.000")
    assert detail["aliases"] == ["Baby spinach"]
    assert {rule["storage_mode"] for rule in detail["shelf_life_rules"]} == {
        "REFRIGERATED"
    }


@pytest.mark.anyio
async def test_ingredient_pagination_and_category_filter_are_stable(
    api_client: httpx.AsyncClient,
    seeded_catalog_api: None,
) -> None:
    """Pages use normalized name plus ID order and filters keep their own total."""
    assert seeded_catalog_api is None
    first_page = await api_client.get(
        "/api/ingredients",
        params={"category": "PROTEIN FOODS", "page": 1, "per_page": 1},
    )
    repeated_first_page = await api_client.get(
        "/api/ingredients",
        params={"category": "PROTEIN FOODS", "page": 1, "per_page": 1},
    )
    second_page = await api_client.get(
        "/api/ingredients",
        params={"category": "PROTEIN FOODS", "page": 2, "per_page": 1},
    )

    assert first_page.status_code == 200
    assert repeated_first_page.status_code == 200
    assert second_page.status_code == 200
    assert first_page.json()["total"] == 2
    assert first_page.json()["items"] == repeated_first_page.json()["items"]
    assert first_page.json()["items"][0]["name"] == "Chicken breast"
    assert second_page.json()["items"][0]["name"] == "Tofu"


@pytest.mark.anyio
async def test_recipe_list_detail_ingredients_and_serving_scaling(
    api_client: httpx.AsyncClient,
    seeded_catalog_api: None,
) -> None:
    """A seeded recipe exposes stable filtering and exact scaled requirements."""
    assert seeded_catalog_api is None
    recipe_list = await api_client.get(
        "/api/recipes",
        params={"q": "spinach", "tag": "vegetarian", "max_cooking_minutes": 20},
    )

    assert recipe_list.status_code == 200
    assert recipe_list.json()["total"] == 2
    spinach_soup = next(
        item for item in recipe_list.json()["items"] if item["name"] == "Spinach soup"
    )
    detail = await api_client.get(
        f"/api/recipes/{spinach_soup['id']}",
        params={"servings": "4.00"},
    )

    assert detail.status_code == 200
    body = detail.json()
    assert Decimal(body["servings"]) == Decimal("4.00")
    assert Decimal(body["nutrition"]["calories"]) == Decimal("396.000")
    assert Decimal(body["nutrition"]["protein_g"]) == Decimal("44.000")
    assert body["nutrition"]["other_nutrients"] == {"fiber_g": 10.0}
    expected_ingredients = {
        "Spinach": (Decimal("400.000"), "GRAM"),
        "Tofu": (Decimal("400.000"), "GRAM"),
    }
    assert len({item["recipe_ingredient_id"] for item in body["ingredients"]}) == len(
        body["ingredients"]
    )
    for name, expected in expected_ingredients.items():
        persisted_rows = [item for item in body["ingredients"] if item["name"] == name]
        assert persisted_rows
        assert {
            (Decimal(item["required_quantity"]), item["unit"])
            for item in persisted_rows
        } == {expected}


@pytest.mark.anyio
async def test_catalog_and_recipe_reads_require_authentication(
    api_client: httpx.AsyncClient,
    seeded_catalog_api: None,
) -> None:
    """Read-only catalog endpoints remain unavailable without an access token."""
    assert seeded_catalog_api is None
    app.dependency_overrides.pop(require_authentication, None)
    ingredient_response = await api_client.get("/api/ingredients")
    recipe_response = await api_client.get("/api/recipes")

    assert ingredient_response.status_code == 401
    assert recipe_response.status_code == 401
    assert ingredient_response.json()["detail"] == "Invalid or missing bearer token"
    assert recipe_response.json()["detail"] == "Invalid or missing bearer token"


def test_catalog_recipe_openapi_documents_queries_schemas_and_read_only_methods() -> (
    None
):
    """OpenAPI exposes auth, filtering, pagination, and response-model contracts."""
    app.openapi_schema = None
    schema = app.openapi()
    paths = cast(dict[str, object], schema["paths"])
    ingredient_route = cast(dict[str, object], paths["/api/ingredients"])
    recipe_route = cast(dict[str, object], paths["/api/recipes"])
    recipe_detail_route = cast(dict[str, object], paths["/api/recipes/{recipe_id}"])

    ingredient_get = cast(dict[str, object], ingredient_route["get"])
    recipe_get = cast(dict[str, object], recipe_route["get"])
    recipe_detail_get = cast(dict[str, object], recipe_detail_route["get"])

    assert set(ingredient_route) == {"get"}
    assert set(recipe_route) == {"get"}
    assert set(recipe_detail_route) == {"get"}
    assert ingredient_get["security"] == [{"BearerAuth": []}]
    assert recipe_get["security"] == [{"BearerAuth": []}]
    assert recipe_detail_get["security"] == [{"BearerAuth": []}]
    assert _parameter_names(ingredient_get) == {"q", "category", "page", "per_page"}
    assert _parameter_names(recipe_get) == {
        "q",
        "tag",
        "max_cooking_minutes",
        "page",
        "per_page",
    }
    assert _parameter_names(recipe_detail_get) == {"recipe_id", "servings"}
    assert _response_schema_ref(ingredient_get) == (
        "#/components/schemas/IngredientListResponseDTO"
    )
    assert (
        _response_schema_ref(recipe_get) == "#/components/schemas/RecipeListResponseDTO"
    )
    assert (
        _response_schema_ref(recipe_detail_get)
        == "#/components/schemas/RecipeDetailDTO"
    )


def _parameter_names(operation: dict[str, object]) -> set[str]:
    """Extract documented query and path parameter names from one operation."""
    parameters = cast(list[dict[str, object]], operation["parameters"])
    return {cast(str, parameter["name"]) for parameter in parameters}


def _response_schema_ref(operation: dict[str, object]) -> str:
    """Extract the documented successful JSON response model reference."""
    responses = cast(dict[str, object], operation["responses"])
    response = cast(dict[str, object], responses["200"])
    content = cast(dict[str, object], response["content"])
    application_json = cast(dict[str, object], content["application/json"])
    schema = cast(dict[str, object], application_json["schema"])
    return cast(str, schema["$ref"])
