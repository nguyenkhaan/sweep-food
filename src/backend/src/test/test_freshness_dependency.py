"""Dependency wiring tests for FreshCheck write transactions."""

from typing import get_args, get_type_hints

from fastapi.params import Depends as DependsParameter

from src.db import get_db_session
from src.module.freshness.freshness_dependency import (
    get_freshness_assessment_service,
)


def test_assessment_service_uses_a_fresh_session_after_authentication() -> None:
    """Authentication's read transaction must not be reused by the assessment write."""
    annotation = get_type_hints(
        get_freshness_assessment_service,
        include_extras=True,
    )["session"]
    dependency = next(
        metadata
        for metadata in get_args(annotation)[1:]
        if isinstance(metadata, DependsParameter)
    )

    assert dependency.dependency is get_db_session
    assert dependency.use_cache is False
