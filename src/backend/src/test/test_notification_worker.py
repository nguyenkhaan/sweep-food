"""Tests for the Redis-backed notification worker bootstrap."""

import pytest

from src.service.fcm_service import WireMockFCMClient
from src.worker.notification_worker import (
    WorkerSettings,
    build_daily_expiration_cron,
    build_worker_fcm_service,
    deliver_notification_job,
    expiration_scan_job,
    load_fcm_worker_settings,
    load_notification_job_settings,
    notification_worker_health,
)


@pytest.mark.anyio
async def test_notification_worker_health_job_is_executable() -> None:
    """The ARQ process has a deterministic smoke job before scheduled work runs."""
    assert await notification_worker_health({}) == "ready"


def test_notification_worker_registers_health_job_and_redis_settings() -> None:
    """Worker configuration uses the application Redis DSN and known job function."""
    assert notification_worker_health in WorkerSettings.functions
    assert expiration_scan_job in WorkerSettings.functions
    assert deliver_notification_job in WorkerSettings.functions
    assert WorkerSettings.redis_settings.host
    assert WorkerSettings.max_tries == 3


def test_fcm_worker_settings_are_loaded_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Firebase project, credential path, and token key never come from source."""
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "sweep-food-test")
    monkeypatch.setenv("FCM_PROVIDER", "firebase")
    monkeypatch.setenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "/run/secrets/firebase-service-account.json",
    )
    monkeypatch.setenv("FCM_TOKEN_ENCRYPTION_KEY", "environment-fernet-key")

    settings = load_fcm_worker_settings()

    assert settings.project_id == "sweep-food-test"
    assert settings.provider == "firebase"
    assert settings.credential_path == "/run/secrets/firebase-service-account.json"
    assert settings.token_encryption_key == "environment-fernet-key"


def test_worker_builds_wiremock_fcm_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Local/CI selects the mock adapter without reading Firebase credentials."""
    monkeypatch.setenv("FCM_PROVIDER", "wiremock")
    monkeypatch.setenv("WIREMOCK_URL", "http://wiremock:8080")
    monkeypatch.setenv("FCM_TOKEN_ENCRYPTION_KEY", "environment-fernet-key")

    service = build_worker_fcm_service(load_fcm_worker_settings())

    assert isinstance(service.client, WireMockFCMClient)


def test_notification_job_settings_are_validated_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Schedule and retry controls are configurable without source changes."""
    monkeypatch.setenv("NOTIFICATION_DEFAULT_WARNING_DAYS", "4")
    monkeypatch.setenv("NOTIFICATION_MAX_RETRIES", "3")
    monkeypatch.setenv("NOTIFICATION_SCAN_HOUR_LOCAL", "8")

    settings = load_notification_job_settings()

    assert settings.default_warning_days == 4
    assert settings.max_retries == 3
    assert settings.scan_hour_local == 8


def test_daily_expiration_cron_converts_ho_chi_minh_hour_to_utc() -> None:
    """The daily 08:00 product schedule is registered at 01:00 UTC."""
    cron_job = build_daily_expiration_cron(8)

    assert cron_job.hour == 1
    assert cron_job.minute == 0
    assert cron_job.unique is True
