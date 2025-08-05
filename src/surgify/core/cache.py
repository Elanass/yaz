"""
Redis Cache Implementation for Surgify Platform
Provides caching decorators and utilities for high-performance endpoints
"""

import asyncio
import hashlib
import json
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

import redis.asyncio as redis
from pydantic import BaseModel
from redis.asyncio import Redis

from .config.unified_config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheConfig:
    """Cache configuration constants"""

    DEFAULT_TTL = 300  # 5 minutes
    LIST_TTL = 60  # 1 minute for list endpoints
    DETAIL_TTL = 600  # 10 minutes for detail endpoints
    KEY_PREFIX = "surgify"


class CacheClient:
    """Redis cache client wrapper with fallback support"""

    def __init__(self):
        self._client: Optional[Redis] = None
        self._connected = False

    async def _get_client(self) -> Optional[Redis]:
        """Get Redis client with connection handling"""
        if self._client is None:
            try:
                # Try to connect to Redis
                if hasattr(settings, "redis_url") and settings.redis_url:
                    self._client = redis.from_url(settings.redis_url)
                else:
                    # Default Redis connection
                    self._client = redis.Redis(
                        host=getattr(settings, "redis_host", "localhost"),
                        port=getattr(settings, "redis_port", 6379),
                        db=getattr(settings, "redis_db", 0),
                        decode_responses=True,
                    )

                # Test connection
                await self._client.ping()
                self._connected = True
                logger.info("Redis cache connected successfully")

            except Exception as e:
                logger.warning(
                    f"Redis connection failed, falling back to no-cache mode: {e}"
                )
                self._client = None
                self._connected = False

        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            client = await self._get_client()
            if client and self._connected:
                value = await client.get(key)
                if value:
                    return deserialize_response(value)
        except Exception as e:
            logger.warning(f"Cache GET error for key {key}: {e}")
        return None

    async def set(
        self, key: str, value: Any, ttl: int = CacheConfig.DEFAULT_TTL
    ) -> bool:
        """Set value in cache with TTL"""
        try:
            client = await self._get_client()
            if client and self._connected:
                # Serialize value to JSON string
                if isinstance(value, str):
                    serialized_value = value
                else:
                    serialized_value = serialize_response(value)
                await client.setex(key, ttl, serialized_value)
                return True
        except Exception as e:
            logger.warning(f"Cache SET error for key {key}: {e}")
        return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            client = await self._get_client()
            if client and self._connected:
                await client.delete(key)
                return True
        except Exception as e:
            logger.warning(f"Cache DELETE error for key {key}: {e}")
        return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            client = await self._get_client()
            if client and self._connected:
                keys = await client.keys(pattern)
                if keys:
                    return await client.delete(*keys)
                return 0
        except Exception as e:
            logger.warning(f"Cache DELETE_PATTERN error for pattern {pattern}: {e}")
        return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern (alias for delete_pattern)"""
        return await self.delete_pattern(pattern)


# Global cache client instance
cache_client = CacheClient()


def generate_cache_key(resource: str, **params) -> str:
    """Generate consistent cache key from resource and parameters"""
    # Sort parameters for consistent hashing
    sorted_params = sorted(params.items())
    params_str = json.dumps(sorted_params, sort_keys=True)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

    return f"{CacheConfig.KEY_PREFIX}:{resource}:{params_hash}"


def serialize_response(data: Any) -> str:
    """Serialize response data for caching"""
    if isinstance(data, BaseModel):
        return data.model_dump_json()
    elif isinstance(data, list) and data and isinstance(data[0], BaseModel):
        return json.dumps([item.model_dump() for item in data])
    else:
        return json.dumps(data, default=str)


def deserialize_response(data_str: str, response_model: Optional[type] = None) -> Any:
    """Deserialize cached response data"""
    try:
        data = json.loads(data_str)

        if response_model and issubclass(response_model, BaseModel):
            if isinstance(data, list):
                return [response_model(**item) for item in data]
            else:
                return response_model(**data)

        return data
    except Exception as e:
        logger.warning(f"Cache deserialization error: {e}")
        return None


def cache_response(
    resource: str,
    ttl: int = CacheConfig.DEFAULT_TTL,
    key_params: Optional[list] = None,
    response_model: Optional[type] = None,
):
    """
    Cache decorator for API endpoints

    Args:
        resource: Resource name for cache key generation
        ttl: Time to live in seconds
        key_params: List of parameter names to include in cache key
        response_model: Pydantic model for response serialization
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract parameters for cache key
            cache_params = {}
            if key_params:
                for param in key_params:
                    if param in kwargs:
                        cache_params[param] = kwargs[param]

            # Add pagination parameters if they exist
            for param in ["page", "limit", "offset", "skip"]:
                if param in kwargs:
                    cache_params[param] = kwargs[param]

            # Generate cache key
            cache_key = generate_cache_key(resource, **cache_params)

            # Try to get from cache
            try:
                cached_data = await cache_client.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache HIT for key: {cache_key}")
                    result = deserialize_response(cached_data, response_model)
                    if result is not None:
                        return result
            except Exception as e:
                logger.warning(f"Cache retrieval error: {e}")

            # Cache miss - execute function
            logger.debug(f"Cache MISS for key: {cache_key}")
            result = await func(*args, **kwargs)

            # Cache the result
            try:
                serialized_result = serialize_response(result)
                await cache_client.set(cache_key, serialized_result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache storage error: {e}")

            return result

        return wrapper

    return decorator


# Convenience decorators
def cache_list_endpoint(resource: str, ttl: int = CacheConfig.LIST_TTL):
    """Cache decorator for list endpoints"""
    return cache_response(
        resource, ttl=ttl, key_params=["page", "limit", "search", "filter"]
    )


def cache_detail_endpoint(resource: str, ttl: int = CacheConfig.DETAIL_TTL):
    """Cache decorator for detail endpoints"""
    return cache_response(resource, ttl=ttl, key_params=["id"])


async def invalidate_cache(resource: str, **params):
    """Invalidate cache entries for a resource"""
    if params:
        # Invalidate specific cache entry
        cache_key = generate_cache_key(resource, **params)
        await cache_client.delete(cache_key)
        logger.debug(f"Invalidated cache key: {cache_key}")
    else:
        # Invalidate all entries for resource
        pattern = f"{CacheConfig.KEY_PREFIX}:{resource}:*"
        count = await cache_client.delete_pattern(pattern)
        logger.debug(f"Invalidated {count} cache entries for resource: {resource}")


# Health check function
async def check_cache_health() -> Dict[str, Any]:
    """Check cache system health"""
    try:
        client = await cache_client._get_client()
        if client and cache_client._connected:
            info = await client.info()
            return {
                "status": "healthy",
                "connected": True,
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
            }
        else:
            return {
                "status": "degraded",
                "connected": False,
                "message": "Running without cache",
            }
    except Exception as e:
        return {"status": "error", "connected": False, "error": str(e)}
