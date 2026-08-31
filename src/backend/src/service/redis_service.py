"""Asynchronous Redis client lifecycle and primitive operations."""

from redis.asyncio import Redis, from_url
from redis.exceptions import RedisError


class RedisService:
    """Manage one asynchronous Redis client for application services."""

    def __init__(self) -> None:
        self._client: Redis | None = None

    async def initialize(self, redis_url: str) -> None:
        """Connect to Redis and verify the configured service is reachable."""
        if self._client is not None:
            return

        client = from_url(redis_url, decode_responses=True)
        try:
            await client.ping()
        except RedisError:
            await client.aclose()
            raise
        self._client = client

    async def close(self) -> None:
        """Close the Redis client during application shutdown."""
        client = self._client
        self._client = None
        if client is not None:
            await client.aclose()

    async def get(self, key: str) -> str | None:
        """Return a string value for ``key`` when present."""
        value = await self._get_client().get(key)
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("Redis value must be decoded as text")
        return value

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        """Store a text value with a positive expiration time."""
        self._validate_ttl(ttl_seconds)
        await self._get_client().set(key, value, ex=ttl_seconds)

    async def set_if_absent(self, key: str, value: str, ttl_seconds: int) -> bool:
        """Store a text value only when absent and return whether it was stored."""
        self._validate_ttl(ttl_seconds)
        was_set = await self._get_client().set(key, value, ex=ttl_seconds, nx=True)
        return bool(was_set)

    async def delete(self, key: str) -> None:
        """Delete a key if it exists."""
        await self._get_client().delete(key)

    async def increment(self, key: str, ttl_seconds: int) -> int:
        """Increment a counter and set TTL when this creates its first value."""
        self._validate_ttl(ttl_seconds)
        client = self._get_client()
        count = await client.incr(key)
        if count == 1:
            await client.expire(key, ttl_seconds)
        return count

    async def ttl(self, key: str) -> int:
        """Return remaining key TTL using Redis' standard sentinel values."""
        return await self._get_client().ttl(key)

    def _get_client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis service has not been initialized.")
        return self._client

    @staticmethod
    def _validate_ttl(ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            raise ValueError("Redis TTL must be greater than zero")


redis_service = RedisService()
