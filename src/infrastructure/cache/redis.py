import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from redis.asyncio import Redis

from src.config import settings

logger = logging.getLogger(__name__)

_redis_client: Redis | None = None


async def get_redis() -> AsyncIterator[Redis | None]:
    """FastAPI dependency that yields a Redis connection (or None if unavailable)."""
    global _redis_client  # noqa: PLW0603
    if _redis_client is None:
        try:
            _redis_client = Redis.from_url(
                settings.redis_url,
                socket_connect_timeout=1,
                socket_timeout=3,
                decode_responses=True,
            )
            await _redis_client.ping()  # type: ignore[misc]
        except Exception:
            logger.warning("Redis is unavailable, caching disabled")
            _redis_client = None
    yield _redis_client


async def close_redis() -> None:
    global _redis_client  # noqa: PLW0603
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def cache_set(redis: Redis, key: str, data: Any, ttl: int | None = None) -> None:
    """Serialize and store data in Redis."""
    try:
        await redis.set(key, json.dumps(data, default=str), ex=ttl or settings.redis_cache_ttl)
    except Exception:
        logger.warning("Failed to set cache key=%s", key)


async def cache_get(redis: Redis, key: str) -> Any | None:
    """Retrieve and deserialize data from Redis."""
    try:
        raw = await redis.get(key)
        if raw is not None:
            return json.loads(raw)
    except Exception:
        logger.warning("Failed to get cache key=%s", key)
    return None


async def cache_invalidate(redis: Redis, pattern: str) -> None:
    """Delete all keys matching a pattern."""
    try:
        async for key in redis.scan_iter(match=pattern):
            await redis.delete(key)
    except Exception:
        logger.warning("Failed to invalidate cache pattern=%s", pattern)
