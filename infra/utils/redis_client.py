"""Redis client utilities."""

import os

import redis.asyncio as redis
from redis.asyncio import Redis


_redis_client: Redis | None = None


def get_redis_client() -> Redis | None:
    """Get Redis client instance."""
    global _redis_client

    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                _redis_client = redis.from_url(redis_url)
                # Test connection (skip for sync version)
                # await _redis_client.ping()
            except Exception:
                _redis_client = None

    return _redis_client


async def close_redis_client() -> None:
    """Close Redis connection."""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None
