from dataclasses import dataclass
from datetime import UTC, datetime
from typing import ClassVar, TypeVar, cast
from uuid import UUID

from arq import cron
from arq.connections import ArqRedis, RedisSettings
from arq.cron import CronJob
from arq.typing import WorkerCoroutine

from src.core.setting import (
    DATABASE_URL,
    REDIS_URL,
    WIREMOCK_URL,
    get_env_var,
    get_positive_int_env,
)
from src.db import DatabaseSessionManager
from src.module.notification.notification_job_service import (
    PRODUCT_TIMEZONE,
    ExpirationNotificationService,
    NotificationDeliveryService,
)
from src.module.notification.notification_service import FernetTokenCipher
from src.service.fcm_service import (
    FCMService,
    build_fcm_service,
    build_wiremock_fcm_service,
)

ContextValue = TypeVar("ContextValue")


@dataclass(frozen=True, slots=True)
class FCMWorkerEnvironment:
    """Sensitive FCM runtime values loaded exclusively from the environment."""

    provider: str
    project_id: str
    credential_path: str
    token_encryption_key: str
    wiremock_url: str
    timeout_seconds: int


@dataclass(frozen=True, slots=True)
class NotificationJobSettings:
    """Non-sensitive notification schedule and retry controls."""

    default_warning_days: int
    max_retries: int
    scan_hour_local: int


def load_fcm_worker_settings() -> FCMWorkerEnvironment:
    """Read required Firebase and token-protection values at worker startup."""
    provider = get_env_var("FCM_PROVIDER", "firebase").lower()
    if provider not in {"firebase", "wiremock"}:
        raise ValueError("FCM_PROVIDER must be firebase or wiremock")
    project_id = get_env_var("FIREBASE_PROJECT_ID", "")
    credential_path = get_env_var("GOOGLE_APPLICATION_CREDENTIALS", "")
    if provider == "firebase" and (not project_id or not credential_path):
        raise ValueError(
            "Firebase FCM requires project ID and application credentials",
        )
    return FCMWorkerEnvironment(
        provider=provider,
        project_id=project_id,
        credential_path=credential_path,
        token_encryption_key=get_env_var("FCM_TOKEN_ENCRYPTION_KEY"),
        wiremock_url=WIREMOCK_URL,
        timeout_seconds=get_positive_int_env("FCM_DELIVERY_TIMEOUT_SECONDS", 5),
    )


def build_worker_fcm_service(settings: FCMWorkerEnvironment) -> FCMService:
    """Select the environment-configured local or production FCM adapter."""
    if settings.provider == "wiremock":
        return build_wiremock_fcm_service(
            settings.wiremock_url,
            settings.timeout_seconds,
        )
    return build_fcm_service(settings.project_id, settings.credential_path)


def load_notification_job_settings() -> NotificationJobSettings:
    """Load and validate schedule/retry configuration from environment values."""
    scan_hour = int(get_env_var("NOTIFICATION_SCAN_HOUR_LOCAL", "8"))
    if not 0 <= scan_hour <= 23:
        raise ValueError("NOTIFICATION_SCAN_HOUR_LOCAL must be between 0 and 23")
    return NotificationJobSettings(
        default_warning_days=get_positive_int_env(
            "NOTIFICATION_DEFAULT_WARNING_DAYS",
            3,
        ),
        max_retries=get_positive_int_env("NOTIFICATION_MAX_RETRIES", 3),
        scan_hour_local=scan_hour,
    )


def build_daily_expiration_cron(local_hour: int) -> CronJob:
    """Schedule the daily product-timezone scan using ARQ's UTC cron clock."""
    if not 0 <= local_hour <= 23:
        raise ValueError("Local notification scan hour must be between 0 and 23")
    local_time = datetime(2026, 1, 1, local_hour, tzinfo=PRODUCT_TIMEZONE)
    utc_hour = local_time.astimezone(UTC).hour
    return cron(
        cast(WorkerCoroutine, expiration_scan_job),
        hour=utc_hour,
        minute=0,
        unique=True,
        max_tries=1,
    )


worker_db_session = DatabaseSessionManager()


async def notification_worker_startup(context: dict[str, object]) -> None:
    """Initialize worker database, Firebase, and token-protection dependencies."""
    settings = load_fcm_worker_settings()
    await worker_db_session.initialize(DATABASE_URL)
    try:
        context["database_manager"] = worker_db_session
        context["fcm_service"] = build_worker_fcm_service(settings)
        context["token_cipher"] = FernetTokenCipher(settings.token_encryption_key)
        context["notification_job_settings"] = load_notification_job_settings()
    except (FileNotFoundError, ValueError):
        await worker_db_session.close()
        raise


async def notification_worker_shutdown(_context: dict[str, object]) -> None:
    """Close database resources owned by the worker process."""
    await worker_db_session.close()


async def notification_worker_health(_context: dict[str, object]) -> str:
    """Return a deterministic result for worker smoke verification."""
    return "ready"


async def expiration_scan_job(context: dict[str, object]) -> dict[str, int]:
    """Create deduplicated expiration notifications and enqueue their delivery."""
    database_manager = _context_value(
        context,
        "database_manager",
        DatabaseSessionManager,
    )
    settings = _context_value(
        context,
        "notification_job_settings",
        NotificationJobSettings,
    )
    redis = _context_value(context, "redis", ArqRedis)
    async with database_manager.session() as db_session:
        result = await ExpirationNotificationService(
            db_session,
            default_warning_days=settings.default_warning_days,
        ).scan()
    for notification_id in result.created_notification_ids:
        await redis.enqueue_job(
            deliver_notification_job.__name__,
            str(notification_id),
            _job_id=f"notification-delivery:{notification_id}",
        )
    return {
        "selected_count": result.selected_count,
        "candidate_count": result.candidate_count,
        "created_count": len(result.created_notification_ids),
    }


async def deliver_notification_job(
    context: dict[str, object],
    notification_id: str,
) -> dict[str, int | bool]:
    """Deliver one persisted notification with service-level bounded retries."""
    database_manager = _context_value(
        context,
        "database_manager",
        DatabaseSessionManager,
    )
    settings = _context_value(
        context,
        "notification_job_settings",
        NotificationJobSettings,
    )
    fcm_service = _context_value(context, "fcm_service", FCMService)
    token_cipher = _context_value(context, "token_cipher", FernetTokenCipher)
    async with database_manager.session() as db_session:
        result = await NotificationDeliveryService(
            db_session,
            token_cipher,
            fcm_service,
            max_retries=settings.max_retries,
        ).deliver(UUID(notification_id))
    return {
        "sent_device_count": result.sent_device_count,
        "invalid_device_count": result.invalid_device_count,
        "failed_device_count": result.failed_device_count,
        "already_sent": result.already_sent,
    }


def _context_value(
    context: dict[str, object],
    key: str,
    expected_type: type[ContextValue],
) -> ContextValue:
    """Return one validated worker dependency without untyped context access."""
    value = context.get(key)
    if not isinstance(value, expected_type):
        raise TypeError(f"Notification worker context is missing {key}")
    return value


class WorkerSettings:
    """ARQ runtime settings for notification background work."""

    _job_settings = load_notification_job_settings()
    functions: ClassVar[list[object]] = [
        notification_worker_health,
        expiration_scan_job,
        deliver_notification_job,
    ]
    cron_jobs: ClassVar[list[CronJob]] = [
        build_daily_expiration_cron(_job_settings.scan_hour_local),
    ]
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    on_startup = notification_worker_startup
    on_shutdown = notification_worker_shutdown
    max_jobs = 10
    max_tries = _job_settings.max_retries
    job_timeout = 30
    health_check_interval = 30
