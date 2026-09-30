"""Tests for environment-backed application settings."""

import pytest

from src.core.setting import get_http_base_url_env, get_positive_int_env


def test_http_base_url_uses_normalized_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the local AI URL by default and remove its trailing slash."""
    monkeypatch.delenv("TEST_AI_BASE_URL", raising=False)

    value = get_http_base_url_env(
        "TEST_AI_BASE_URL",
        "http://127.0.0.1:8001/",
    )

    assert value == "http://127.0.0.1:8001"


def test_http_base_url_uses_normalized_environment_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prefer an explicitly configured HTTP(S) AI service URL."""
    monkeypatch.setenv("TEST_AI_BASE_URL", " https://ai.internal/v1/ ")

    value = get_http_base_url_env(
        "TEST_AI_BASE_URL",
        "http://127.0.0.1:8001",
    )

    assert value == "https://ai.internal/v1"


@pytest.mark.parametrize(
    "value",
    ["", "localhost:8001", "ftp://ai.internal", "http://", "http://ai/?key=x"],
)
def test_http_base_url_rejects_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    """Fail during settings import when the AI base URL is malformed."""
    monkeypatch.setenv("TEST_AI_BASE_URL", value)

    with pytest.raises(ValueError, match=r"must be an HTTP\(S\) base URL"):
        get_http_base_url_env("TEST_AI_BASE_URL", "http://127.0.0.1:8001")


def test_positive_timeout_uses_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the operation-specific timeout default when no override exists."""
    monkeypatch.delenv("TEST_AI_TIMEOUT_SECONDS", raising=False)

    assert get_positive_int_env("TEST_AI_TIMEOUT_SECONDS", 3) == 3


def test_positive_timeout_uses_environment_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read a positive timeout override as an integer number of seconds."""
    monkeypatch.setenv("TEST_AI_TIMEOUT_SECONDS", "17")

    assert get_positive_int_env("TEST_AI_TIMEOUT_SECONDS", 3) == 17


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "invalid"])
def test_positive_timeout_rejects_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    """Reject non-positive and non-integer timeout settings."""
    monkeypatch.setenv("TEST_AI_TIMEOUT_SECONDS", value)

    with pytest.raises(
        ValueError, match="Environment variable TEST_AI_TIMEOUT_SECONDS"
    ):
        get_positive_int_env("TEST_AI_TIMEOUT_SECONDS", 3)
