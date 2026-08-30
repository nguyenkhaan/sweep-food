import json
from abc import abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from secrets import token_urlsafe
from typing import ClassVar, Protocol
from uuid import UUID, uuid4

from src.core.setting import (
    DEFAULT_OTP,
    OTP_CHALLENGE_TTL_SECONDS,
    OTP_DESTINATION_REQUEST_LIMIT,
    OTP_FAILED_ATTEMPT_COOLDOWN_SECONDS,
    OTP_GRANT_TTL_SECONDS,
    OTP_IP_REQUEST_LIMIT,
    OTP_MAX_VERIFICATION_ATTEMPTS,
    OTP_REQUEST_WINDOW_SECONDS,
    OTP_RESEND_COOLDOWN_SECONDS,
)
from src.helper.otp import generate_otp
from src.helper.pwd_hash import compare_hash, hashing
from src.model.enum_model import OTPChannel, OTPPurpose


class OTPStore(Protocol):
    """Redis operations required by the OTP domain service."""

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """Return a text value for a key when it exists."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """Store text with a positive TTL."""
        raise NotImplementedError

    @abstractmethod
    async def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        """Store text only when a key is absent."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a key if it exists."""
        raise NotImplementedError

    @abstractmethod
    async def increment(self, key: str, ttl_seconds: int) -> int:
        """Increment a counter with TTL."""
        raise NotImplementedError

    @abstractmethod
    async def ttl(self, key: str) -> int:
        """Return the remaining key TTL."""
        raise NotImplementedError


class OTPDomainError(ValueError):
    """Base class for stable OTP domain errors."""

    code: ClassVar[str] = "OTP_ERROR"


class OTPChallengeNotFoundError(OTPDomainError):
    """Raised when an OTP challenge is missing or expired."""

    code = "OTP_CHALLENGE_NOT_FOUND"


class OTPPurposeMismatchError(OTPDomainError):
    """Raised when OTP data is used with a different scope."""

    code = "OTP_PURPOSE_MISMATCH"


class OTPInvalidCodeError(OTPDomainError):
    """Raised when an OTP code does not match its challenge."""

    code = "OTP_INVALID_CODE"


class OTPAttemptsExceededError(OTPDomainError):
    """Raised after too many invalid attempts for one challenge."""

    code = "OTP_ATTEMPTS_EXCEEDED"


class OTPResendCooldownError(OTPDomainError):
    """Raised when a destination requests another OTP too soon."""

    code = "OTP_RESEND_COOLDOWN"


class OTPRateLimitError(OTPDomainError):
    """Raised when destination or IP request limits are exceeded."""

    code = "OTP_RATE_LIMITED"


class OTPAttemptsCooldownError(OTPDomainError):
    """Raised when a destination/purpose is cooling down after failed attempts."""

    code = "OTP_ATTEMPTS_COOLDOWN"


class OTPGrantNotFoundError(OTPDomainError):
    """Raised when a verification grant is missing, expired, or consumed."""

    code = "OTP_GRANT_NOT_FOUND"


@dataclass(frozen=True, slots=True)
class OTPRequestRateLimit:
    """Destination/IP request thresholds in one shared time window."""

    destination_request_limit: int
    ip_request_limit: int
    request_window_seconds: int


@dataclass(frozen=True, slots=True)
class OTPPolicy:
    """Configurable OTP expiration, verification, and request-limit policy."""

    challenge_ttl_seconds: int
    grant_ttl_seconds: int
    resend_cooldown_seconds: int
    max_verification_attempts: int
    failed_attempt_cooldown_seconds: int
    request_rate_limit: OTPRequestRateLimit


DEFAULT_OTP_POLICY = OTPPolicy(
    challenge_ttl_seconds=OTP_CHALLENGE_TTL_SECONDS,
    grant_ttl_seconds=OTP_GRANT_TTL_SECONDS,
    resend_cooldown_seconds=OTP_RESEND_COOLDOWN_SECONDS,
    max_verification_attempts=OTP_MAX_VERIFICATION_ATTEMPTS,
    failed_attempt_cooldown_seconds=OTP_FAILED_ATTEMPT_COOLDOWN_SECONDS,
    request_rate_limit=OTPRequestRateLimit(
        destination_request_limit=OTP_DESTINATION_REQUEST_LIMIT,
        ip_request_limit=OTP_IP_REQUEST_LIMIT,
        request_window_seconds=OTP_REQUEST_WINDOW_SECONDS,
    ),
)


@dataclass(frozen=True, slots=True)
class OTPChallengeIssue:
    """Internal challenge issuance result for a future delivery adapter."""

    challenge_id: UUID
    otp: str
    expires_in_seconds: int


@dataclass(frozen=True, slots=True)
class OTPVerificationGrant:
    """Short-lived verification grant returned after a successful OTP check."""

    grant: str
    expires_in_seconds: int


@dataclass(frozen=True, slots=True)
class _OTPChallengeRecord:
    """Stored challenge data that intentionally excludes plaintext OTP data."""

    channel: OTPChannel
    destination_hash: str
    purpose: OTPPurpose
    otp_hash: str
    attempts: int


@dataclass(frozen=True, slots=True)
class _OTPGrantRecord:
    """Stored grant metadata bound to one destination and purpose."""

    channel: OTPChannel
    destination_hash: str
    purpose: OTPPurpose


class OTPService:
    """Issue, verify, and consume short-lived OTP authorization state."""

    def __init__(
        self,
        store: OTPStore,
        policy: OTPPolicy = DEFAULT_OTP_POLICY,
        fixed_otp_code: str | None = DEFAULT_OTP,
    ) -> None:
        """Create an OTP service with a Redis-compatible store and policy."""
        self._store = store
        self._policy = policy
        self._fixed_otp_code = fixed_otp_code
        self._validate_configuration()

    async def issue_challenge(
        self,
        channel: OTPChannel,
        destination: str,
        purpose: OTPPurpose,
        ip_address: str | None,
    ) -> OTPChallengeIssue:
        """Create a scoped OTP challenge after enforcing request limits."""
        destination_hash = self._hash_destination(destination)
        scope_key = self._scope_key(channel, destination_hash, purpose)
        await self._enforce_request_limits(scope_key, destination_hash, ip_address)

        previous_challenge_id = await self._store.get(
            self._challenge_index_key(scope_key)
        )
        if previous_challenge_id is not None:
            await self._store.delete(self._challenge_key(previous_challenge_id))

        challenge_id = uuid4()
        generated_otp = generate_otp()
        otp = self._fixed_otp_code or generated_otp
        record = _OTPChallengeRecord(
            channel=channel,
            destination_hash=destination_hash,
            purpose=purpose,
            otp_hash=hashing(otp),
            attempts=0,
        )
        await self._store.set(
            self._challenge_key(str(challenge_id)),
            self._serialize_challenge(record),
            self._policy.challenge_ttl_seconds,
        )
        await self._store.set(
            self._challenge_index_key(scope_key),
            str(challenge_id),
            self._policy.challenge_ttl_seconds,
        )
        return OTPChallengeIssue(
            challenge_id=challenge_id,
            otp=otp,
            expires_in_seconds=self._policy.challenge_ttl_seconds,
        )

    async def verify_challenge(
        self,
        challenge_id: UUID,
        channel: OTPChannel,
        destination: str,
        purpose: OTPPurpose,
        otp: str,
    ) -> OTPVerificationGrant:
        """Consume a matching OTP challenge and create a single-use grant."""
        challenge_key = self._challenge_key(str(challenge_id))
        raw_record = await self._store.get(challenge_key)
        if raw_record is None:
            raise OTPChallengeNotFoundError()

        record = self._deserialize_challenge(raw_record)
        destination_hash = self._hash_destination(destination)
        if (
            record.channel is not channel
            or record.destination_hash != destination_hash
            or record.purpose is not purpose
        ):
            raise OTPPurposeMismatchError()

        if not compare_hash(otp, record.otp_hash):
            await self._record_failed_attempt(challenge_key, record)
            raise OTPInvalidCodeError()

        await self._delete_challenge(challenge_id, channel, destination_hash, purpose)
        return await self._create_grant(channel, destination_hash, purpose)

    async def consume_grant(
        self,
        grant: str,
        channel: OTPChannel,
        destination: str,
        purpose: OTPPurpose,
    ) -> None:
        """Consume a grant only when its destination and purpose still match."""
        grant_key = self._grant_key(grant)
        raw_record = await self._store.get(grant_key)
        if raw_record is None:
            raise OTPGrantNotFoundError()

        record = self._deserialize_grant(raw_record)
        if (
            record.channel is not channel
            or record.destination_hash != self._hash_destination(destination)
            or record.purpose is not purpose
        ):
            raise OTPPurposeMismatchError()
        await self._store.delete(grant_key)

    async def _enforce_request_limits(
        self,
        scope_key: str,
        destination_hash: str,
        ip_address: str | None,
    ) -> None:
        cooldown_key = f"otp:cooldown:{scope_key}"
        if await self._store.get(self._failed_attempt_cooldown_key(scope_key)):
            raise OTPAttemptsCooldownError()
        if not await self._store.set_if_absent(
            cooldown_key,
            "1",
            self._policy.resend_cooldown_seconds,
        ):
            raise OTPResendCooldownError()

        destination_count = await self._store.increment(
            f"otp:request:destination:{destination_hash}",
            self._policy.request_rate_limit.request_window_seconds,
        )
        if (
            destination_count
            > self._policy.request_rate_limit.destination_request_limit
        ):
            await self._store.delete(cooldown_key)
            raise OTPRateLimitError()

        if ip_address is None:
            return

        ip_count = await self._store.increment(
            f"otp:request:ip:{self._hash_value(ip_address)}",
            self._policy.request_rate_limit.request_window_seconds,
        )
        if ip_count > self._policy.request_rate_limit.ip_request_limit:
            await self._store.delete(cooldown_key)
            raise OTPRateLimitError()

    async def _record_failed_attempt(
        self,
        challenge_key: str,
        record: _OTPChallengeRecord,
    ) -> None:
        remaining_ttl = await self._store.ttl(challenge_key)
        if remaining_ttl <= 0:
            await self._store.delete(challenge_key)
            raise OTPChallengeNotFoundError()

        failed_record = _OTPChallengeRecord(
            channel=record.channel,
            destination_hash=record.destination_hash,
            purpose=record.purpose,
            otp_hash=record.otp_hash,
            attempts=record.attempts + 1,
        )
        if failed_record.attempts >= self._policy.max_verification_attempts:
            await self._store.delete(challenge_key)
            await self._store.delete(
                self._challenge_index_key(
                    self._scope_key(
                        record.channel,
                        record.destination_hash,
                        record.purpose,
                    )
                )
            )
            await self._store.set(
                self._failed_attempt_cooldown_key(
                    self._scope_key(
                        record.channel,
                        record.destination_hash,
                        record.purpose,
                    )
                ),
                "1",
                self._policy.failed_attempt_cooldown_seconds,
            )
            raise OTPAttemptsExceededError()
        await self._store.set(
            challenge_key,
            self._serialize_challenge(failed_record),
            remaining_ttl,
        )

    async def _delete_challenge(
        self,
        challenge_id: UUID,
        channel: OTPChannel,
        destination_hash: str,
        purpose: OTPPurpose,
    ) -> None:
        challenge_id_text = str(challenge_id)
        await self._store.delete(self._challenge_key(challenge_id_text))
        index_key = self._challenge_index_key(
            self._scope_key(channel, destination_hash, purpose)
        )
        if await self._store.get(index_key) == challenge_id_text:
            await self._store.delete(index_key)

    async def _create_grant(
        self,
        channel: OTPChannel,
        destination_hash: str,
        purpose: OTPPurpose,
    ) -> OTPVerificationGrant:
        grant = token_urlsafe(32)
        record = _OTPGrantRecord(
            channel=channel,
            destination_hash=destination_hash,
            purpose=purpose,
        )
        await self._store.set(
            self._grant_key(grant),
            self._serialize_grant(record),
            self._policy.grant_ttl_seconds,
        )
        return OTPVerificationGrant(
            grant=grant,
            expires_in_seconds=self._policy.grant_ttl_seconds,
        )

    @staticmethod
    def _serialize_challenge(record: _OTPChallengeRecord) -> str:
        return json.dumps(
            {
                "channel": record.channel.value,
                "destination_hash": record.destination_hash,
                "purpose": record.purpose.value,
                "otp_hash": record.otp_hash,
                "attempts": record.attempts,
            },
            separators=(",", ":"),
        )

    @staticmethod
    def _deserialize_challenge(raw_record: str) -> _OTPChallengeRecord:
        record = OTPService._load_json_object(raw_record)
        raw_channel = record.get("channel")
        raw_destination_hash = record.get("destination_hash")
        raw_purpose = record.get("purpose")
        raw_otp_hash = record.get("otp_hash")
        raw_attempts = record.get("attempts")
        if (
            not isinstance(raw_channel, str)
            or not isinstance(raw_destination_hash, str)
            or not isinstance(raw_purpose, str)
            or not isinstance(raw_otp_hash, str)
            or not isinstance(raw_attempts, int)
        ):
            raise OTPChallengeNotFoundError()
        try:
            return _OTPChallengeRecord(
                channel=OTPChannel(raw_channel),
                destination_hash=raw_destination_hash,
                purpose=OTPPurpose(raw_purpose),
                otp_hash=raw_otp_hash,
                attempts=raw_attempts,
            )
        except ValueError as error:
            raise OTPChallengeNotFoundError() from error

    @staticmethod
    def _serialize_grant(record: _OTPGrantRecord) -> str:
        return json.dumps(
            {
                "channel": record.channel.value,
                "destination_hash": record.destination_hash,
                "purpose": record.purpose.value,
            },
            separators=(",", ":"),
        )

    @staticmethod
    def _deserialize_grant(raw_record: str) -> _OTPGrantRecord:
        record = OTPService._load_json_object(raw_record)
        raw_channel = record.get("channel")
        raw_destination_hash = record.get("destination_hash")
        raw_purpose = record.get("purpose")
        if (
            not isinstance(raw_channel, str)
            or not isinstance(raw_destination_hash, str)
            or not isinstance(raw_purpose, str)
        ):
            raise OTPGrantNotFoundError()
        try:
            return _OTPGrantRecord(
                channel=OTPChannel(raw_channel),
                destination_hash=raw_destination_hash,
                purpose=OTPPurpose(raw_purpose),
            )
        except ValueError as error:
            raise OTPGrantNotFoundError() from error

    @staticmethod
    def _load_json_object(raw_record: str) -> dict[str, object]:
        try:
            value: object = json.loads(raw_record)
        except json.JSONDecodeError as error:
            raise OTPChallengeNotFoundError() from error
        if not isinstance(value, dict):
            raise OTPChallengeNotFoundError()
        record: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise OTPChallengeNotFoundError()
            record[key] = item
        return record

    @staticmethod
    def _hash_destination(destination: str) -> str:
        normalized_destination = destination.strip().lower()
        if not normalized_destination:
            raise ValueError("OTP destination is required")
        return OTPService._hash_value(normalized_destination)

    @staticmethod
    def _hash_value(value: str) -> str:
        return sha256(value.encode()).hexdigest()

    @staticmethod
    def _scope_key(
        channel: OTPChannel,
        destination_hash: str,
        purpose: OTPPurpose,
    ) -> str:
        return f"{channel.value}:{purpose.value}:{destination_hash}"

    @staticmethod
    def _challenge_key(challenge_id: str) -> str:
        return f"otp:challenge:{challenge_id}"

    @staticmethod
    def _challenge_index_key(scope_key: str) -> str:
        return f"otp:challenge-index:{scope_key}"

    @staticmethod
    def _grant_key(grant: str) -> str:
        return f"otp:grant:{OTPService._hash_value(grant)}"

    @staticmethod
    def _failed_attempt_cooldown_key(scope_key: str) -> str:
        return f"otp:failed-attempt-cooldown:{scope_key}"

    def _validate_configuration(self) -> None:
        if self._fixed_otp_code is not None and (
            len(self._fixed_otp_code) != 6 or not self._fixed_otp_code.isdigit()
        ):
            raise ValueError("OTP mock code must be six numeric digits")
        if (
            min(
                self._policy.challenge_ttl_seconds,
                self._policy.grant_ttl_seconds,
                self._policy.resend_cooldown_seconds,
                self._policy.max_verification_attempts,
                self._policy.failed_attempt_cooldown_seconds,
                self._policy.request_rate_limit.destination_request_limit,
                self._policy.request_rate_limit.ip_request_limit,
                self._policy.request_rate_limit.request_window_seconds,
            )
            <= 0
        ):
            raise ValueError("All OTP policy values must be greater than zero")
