"""Unit tests for deterministic FreshCheck mapping candidates."""

from uuid import UUID
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.freshcheck_mapping_service import (
    CatalogIngredient,
    FreshCheckIngredientReference,
    FreshCheckMappingSeedService,
    MappingManifestValidationError,
    MappingSeedError,
    build_mapping_candidates,
    parse_mapping_manifest,
)


def test_build_mapping_candidates_only_emits_unambiguous_exact_names() -> None:
    """Exact names are proposed, while ambiguous and unknown names stay unseeded."""
    catalog = (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000001"), "Cá hồi"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000002"), "Nấm"),
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000003"), "Không rõ"),
    )
    freshcheck = (
        FreshCheckIngredientReference("FC-SALMON", ("Cá hồi",)),
        FreshCheckIngredientReference("FC-MUSHROOM-A", ("Nấm",)),
        FreshCheckIngredientReference("FC-MUSHROOM-B", ("Nấm",)),
    )

    report = build_mapping_candidates(catalog, freshcheck)

    assert [(item.master_ingredient_id, item.freshcheck_ingredient_id) for item in report.exact_name] == [
        (UUID("00000000-0000-0000-0000-000000000001"), "FC-SALMON")
    ]
    assert report.ambiguous[0].master_ingredient_id == UUID(
        "00000000-0000-0000-0000-000000000002"
    )
    assert report.ambiguous[0].freshcheck_ingredient_ids == (
        "FC-MUSHROOM-A",
        "FC-MUSHROOM-B",
    )
    assert report.unmapped == (
        CatalogIngredient(UUID("00000000-0000-0000-0000-000000000003"), "Không rõ"),
    )


def test_parse_mapping_manifest_rejects_null_and_duplicate_master_ids() -> None:
    """A review manifest has complete records and one mapping per catalog item."""
    valid_master_id = "00000000-0000-0000-0000-000000000001"
    manifest = {
        "kb_version": "1.2.3",
        "mappings": [
            {
                "master_ingredient_id": valid_master_id,
                "freshcheck_ingredient_id": "FC-SALMON",
                "match_method": "EXACT_NAME",
                "reviewed_by": "reviewer",
            }
        ],
    }

    parsed_manifest = parse_mapping_manifest(manifest)

    assert parsed_manifest.kb_version == "1.2.3"
    assert parsed_manifest.mappings[0].master_ingredient_id == UUID(valid_master_id)

    manifest["mappings"].append(
        {
            "master_ingredient_id": valid_master_id,
            "freshcheck_ingredient_id": None,
            "match_method": "EXACT_NAME",
            "reviewed_by": "reviewer",
        }
    )
    with pytest.raises(MappingManifestValidationError, match="null"):
        parse_mapping_manifest(manifest)

    manifest["mappings"][1]["freshcheck_ingredient_id"] = "FC-OTHER"
    with pytest.raises(MappingManifestValidationError, match="duplicate"):
        parse_mapping_manifest(manifest)


@pytest.mark.anyio
async def test_seed_mapping_validates_foreign_keys_before_insert() -> None:
    """A reviewed mapping is inserted only after both referenced rows exist."""
    manifest = parse_mapping_manifest(
        {
            "kb_version": "1.2.3",
            "mappings": [
                {
                    "master_ingredient_id": "00000000-0000-0000-0000-000000000001",
                    "freshcheck_ingredient_id": "FC-SALMON",
                    "match_method": "EXACT_NAME",
                    "reviewed_by": "reviewer",
                }
            ],
        }
    )
    session = AsyncMock(spec=AsyncSession)
    session.get.side_effect = (object(), object())
    session.scalar.return_value = None
    session.add = Mock()

    inserted_count = await FreshCheckMappingSeedService(session).seed(manifest)

    assert inserted_count == 1
    session.add.assert_called_once()
    session.flush.assert_awaited_once()


@pytest.mark.anyio
async def test_seed_mapping_rejects_a_missing_freshcheck_ingredient() -> None:
    """A manifest cannot create an orphaned mapping foreign key."""
    manifest = parse_mapping_manifest(
        {
            "kb_version": "1.2.3",
            "mappings": [
                {
                    "master_ingredient_id": "00000000-0000-0000-0000-000000000001",
                    "freshcheck_ingredient_id": "FC-MISSING",
                    "match_method": "MANUAL_REVIEW",
                    "reviewed_by": "reviewer",
                }
            ],
        }
    )
    session = AsyncMock(spec=AsyncSession)
    session.get.side_effect = (object(), None)

    with pytest.raises(MappingSeedError, match="missing FreshCheck"):
        await FreshCheckMappingSeedService(session).seed(manifest)
