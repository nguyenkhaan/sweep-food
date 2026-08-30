"""Unit tests for Redis-backed OTP and password-hashing services."""

from dataclasses import dataclass, field

import pytest

from src.helper.pwd_hash import compare_hash, hashing
from src.model.enum_model import OTPChannel, OTPPurpose
from src.service.otp_service import (
    OTPAttemptsCooldownError,
    OTPAttemptsExceededError,
    OTPChallengeNotFoundError,
    OTPGrantNotFoundError,
    OTPInvalidCodeError,
    OTPPolicy,
    OTPPurposeMismatchError,
    OTPRequestRateLimit,
    OTPResendCooldownError,
    OTPService,
)


@dataclass(slots=True)
class FakeOTPStore:
    """Minimal expiry-aware Redis replacement for OTP unit tests."""

    now_seconds: int = 0
    _values: dict[str, tuple[str, int]] = field(default_factory=dict)

    async def get(self, key: str) -> str | None:
        """Return a stored value unless its TTL has expired."""
        self._remove_expired(key)
        item = self._values.get(key)
        return None if item is None else item[0]

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """Store a value with its fake-clock expiration time."""
        self._values[key] = (value, self.now_seconds + ttl_seconds)

    async def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        """Store a value only if it has not been set or has expired."""
        if await self.get(key) is not None:
            return False
        await self.set(key, value, ttl_seconds)
        return True

    async def delete(self, key: str) -> None:
        """Delete a stored key when present."""
        self._values.pop(key, None)

    async def increment(self, key: str, ttl_seconds: int) -> int:
        """Increment an expiring integer counter."""
        value = await self.get(key)
        count = 1 if value is None else int(value) + 1
        if value is None:
            await self.set(key, str(count), ttl_seconds)
        else:
            ttl = await self.ttl(key)
            await self.set(key, str(count), ttl)
        return count

    async def ttl(self, key: str) -> int:
        """Return a Redis-compatible remaining TTL value."""
        self._remove_expired(key)
        item = self._values.get(key)
        if item is None:
            return -2
        return item[1] - self.now_seconds

    def advance(self, seconds: int) -> None:
        """Advance the fake clock to test Redis TTL behavior."""
        self.now_seconds += seconds

    def _remove_expired(self, key: str) -> None:
        item = self._values.get(key)
        if item is not None and item[1] <= self.now_seconds:
            self._values.pop(key, None)


def _policy(
    *,
    challenge_ttl_seconds: int = 300,
    max_verification_attempts: int = 5,
) -> OTPPolicy:
    return OTPPolicy(
        challenge_ttl_seconds=challenge_ttl_seconds,
        grant_ttl_seconds=300,
        resend_cooldown_seconds=60,
        max_verification_attempts=max_verification_attempts,
        failed_attempt_cooldown_seconds=900,
        request_rate_limit=OTPRequestRateLimit(
            destination_request_limit=5,
            ip_request_limit=20,
            request_window_seconds=3600,
        ),
    )


def _service(
    store: FakeOTPStore,
    *,
    policy: OTPPolicy | None = None,
    fixed_otp_code: str | None = "123456",
) -> OTPService:
    return OTPService(
        store,
        policy=policy or _policy(),
        fixed_otp_code=fixed_otp_code,
    )


@pytest.mark.anyio
async def test_local_mock_code_replaces_generated_code() -> None:
    """Local/CI configuration issues the fixed OTP without storing it plainly."""
    issue = await _service(FakeOTPStore()).issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )

    assert issue.otp == "123456"


@pytest.mark.anyio
async def test_production_style_code_is_six_random_digits() -> None:
    """Without the mock configuration, a six-digit code is issued."""
    issue = await _service(FakeOTPStore(), fixed_otp_code=None).issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )

    assert issue.otp.isdigit()
    assert len(issue.otp) == 6


@pytest.mark.anyio
async def test_challenge_expires_after_its_ttl() -> None:
    """An expired challenge cannot be verified."""
    store = FakeOTPStore()
    issue = await _service(
        store, policy=_policy(challenge_ttl_seconds=10)
    ).issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )
    store.advance(10)

    with pytest.raises(OTPChallengeNotFoundError):
        await _service(
            store, policy=_policy(challenge_ttl_seconds=10)
        ).verify_challenge(
            issue.challenge_id,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
            "123456",
        )


@pytest.mark.anyio
async def test_replacement_invalidates_the_previous_challenge() -> None:
    """Issuing another OTP for a scope invalidates the prior challenge."""
    store = FakeOTPStore()
    service = _service(store)
    first_issue = await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )
    store.advance(60)
    second_issue = await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )

    with pytest.raises(OTPChallengeNotFoundError):
        await service.verify_challenge(
            first_issue.challenge_id,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
            "123456",
        )

    grant = await service.verify_challenge(
        second_issue.challenge_id,
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "123456",
    )
    assert grant.grant


@pytest.mark.anyio
async def test_invalid_code_tracks_attempts_and_locks_the_challenge() -> None:
    """Repeated invalid codes consume the challenge at the configured limit."""
    store = FakeOTPStore()
    service = _service(store, policy=_policy(max_verification_attempts=2))
    issue = await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )

    with pytest.raises(OTPInvalidCodeError):
        await service.verify_challenge(
            issue.challenge_id,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
            "000000",
        )
    with pytest.raises(OTPAttemptsExceededError):
        await service.verify_challenge(
            issue.challenge_id,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
            "000000",
        )
    with pytest.raises(OTPAttemptsCooldownError):
        await service.issue_challenge(
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
            "127.0.0.1",
        )


@pytest.mark.anyio
async def test_purpose_mismatch_cannot_verify_or_consume_a_grant() -> None:
    """A registration challenge/grant cannot authorize password reset."""
    service = _service(FakeOTPStore())
    issue = await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )

    with pytest.raises(OTPPurposeMismatchError):
        await service.verify_challenge(
            issue.challenge_id,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.RESET_PASSWORD,
            "123456",
        )

    grant = await service.verify_challenge(
        issue.challenge_id,
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "123456",
    )
    with pytest.raises(OTPPurposeMismatchError):
        await service.consume_grant(
            grant.grant,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.RESET_PASSWORD,
        )


@pytest.mark.anyio
async def test_grant_is_single_use() -> None:
    """A consumed verification grant cannot authorize a second operation."""
    service = _service(FakeOTPStore())
    issue = await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )
    grant = await service.verify_challenge(
        issue.challenge_id,
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "123456",
    )

    await service.consume_grant(
        grant.grant,
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
    )

    with pytest.raises(OTPGrantNotFoundError):
        await service.consume_grant(
            grant.grant,
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
        )


@pytest.mark.anyio
async def test_resend_cooldown_blocks_second_issue_until_expiry() -> None:
    """The destination/purpose cooldown blocks rapid resend requests."""
    store = FakeOTPStore()
    service = _service(store)
    await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )

    with pytest.raises(OTPResendCooldownError):
        await service.issue_challenge(
            OTPChannel.SMS,
            "+84901234567",
            OTPPurpose.REGISTER,
            "127.0.0.1",
        )

    store.advance(60)
    issue = await service.issue_challenge(
        OTPChannel.SMS,
        "+84901234567",
        OTPPurpose.REGISTER,
        "127.0.0.1",
    )
    assert issue.otp == "123456"


def test_password_hash_helper_uses_argon2id_verification() -> None:
    """Passwords are hashed and compared without retaining plaintext."""
    password_hash = hashing("secure-password")

    assert password_hash.startswith("$argon2id$")
    assert compare_hash("secure-password", password_hash)
    assert not compare_hash("incorrect-password", password_hash)
