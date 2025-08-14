"""Redis Cache Implementation for Surgify Platform
Provides caching decorators and utilities for high-performance endpoints.
"""

import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel
from redis.asyncio import Redis

from shared.config import get_shared_config


logger = logging.getLogger(__name__)
settings = get_shared_config()


class CacheConfig:
    """Cache configuration constants."""

    DEFAULT_TTL = 300  # 5 minutes
    LIST_TTL = 60  # 1 minute for list endpoints
    DETAIL_TTL = 600  # 10 minutes for detail endpoints
    KEY_PREFIX = "surgify"


class CacheClient:
    """Redis cache client wrapper with fallback support."""

    def __init__(self) -> None:
        self._client: Redis | None = None
        self._connected = False

    async def _get_client(self) -> Redis | None:
        """Get Redis client with connection handling."""
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

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        try:
            client = await self._get_client()
            if client:
                # Add prefix if not already present
                cache_key = (
                    key
                    if key.startswith(f"{CacheConfig.KEY_PREFIX}:")
                    else f"{CacheConfig.KEY_PREFIX}:{key}"
                )
                value = await client.get(cache_key)
                if value:
                    return deserialize_response(value)
                return None
        except Exception as e:
            logger.warning(f"Cache GET error for key {key}: {e}")
            return None
        return None

    async def set(
        self, key: str, value: Any, ttl: int = CacheConfig.DEFAULT_TTL
    ) -> bool:
        """Set value in cache with TTL."""
        try:
            client = await self._get_client()
            if client:
                # Add prefix if not already present
                cache_key = (
                    key
                    if key.startswith(f"{CacheConfig.KEY_PREFIX}:")
                    else f"{CacheConfig.KEY_PREFIX}:{key}"
                )
                # Serialize value to JSON string
                if isinstance(value, str):
                    serialized_value = value
                else:
                    serialized_value = serialize_response(value)
                result = await client.setex(cache_key, ttl, serialized_value)
                return bool(result)
        except Exception as e:
            logger.warning(f"Cache SET error for key {key}: {e}")
        return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            client = await self._get_client()
            if client and self._connected:
                await client.delete(key)
                return True
        except Exception as e:
            logger.warning(f"Cache DELETE error for key {key}: {e}")
        return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        try:
            client = await self._get_client()
            if client:
                keys = await client.keys(pattern)
                if keys:
                    return await client.delete(*keys)
                return 0
        except Exception as e:
            logger.warning(f"Cache DELETE_PATTERN error for pattern {pattern}: {e}")
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern."""
        try:
            client = await self._get_client()
            if client:
                # Add prefix to pattern if not already prefixed
                if not pattern.startswith(f"{CacheConfig.KEY_PREFIX}:"):
                    full_pattern = f"{CacheConfig.KEY_PREFIX}:{pattern}"
                else:
                    full_pattern = pattern

                keys = await client.keys(full_pattern)
                if keys:
                    return await client.delete(*keys)
                return 0
        except Exception as e:
            logger.warning(f"Cache INVALIDATE_PATTERN error for pattern {pattern}: {e}")
            return 0


# Global cache client instance
cache_client = CacheClient()


def generate_cache_key(resource: str, **params) -> str:
    """Generate consistent cache key from resource and parameters."""
    # Start with just the resource (without namespace prefix)
    key_parts = [resource]

    # Handle request object if present
    if "request" in params:
        request = params.pop("request")
        if hasattr(request, "url") and hasattr(request.url, "path"):
            key_parts.append(request.url.path)
        if hasattr(request, "query_params"):
            sorted_params = dict(sorted(request.query_params.items()))
            params_str = json.dumps(sorted_params, sort_keys=True)
            key_parts.append(params_str)

    # Add other parameters
    for key, value in sorted(params.items()):
        key_parts.append(f"{key}={value}")

    return ":".join(key_parts)


def serialize_response(data: Any) -> str:
    """Serialize response data for caching."""
    if isinstance(data, BaseModel):
        return data.model_dump_json()
    if isinstance(data, list) and data and isinstance(data[0], BaseModel):
        return json.dumps([item.model_dump() for item in data])
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        # Fallback to pickle for complex objects that can't be JSON serialized
        import base64
        import pickle

        pickled = pickle.dumps(data)
        return base64.b64encode(pickled).decode("utf-8")


def deserialize_response(data: str | Any, response_model: type | None = None) -> Any:
    """Deserialize cached response data."""
    # If data is already a dict/list/etc (from mocks), return it directly
    if not isinstance(data, str):
        return data

    try:
        # First try JSON deserialization
        parsed_data = json.loads(data)

        if response_model and issubclass(response_model, BaseModel):
            if isinstance(parsed_data, list):
                return [response_model(**item) for item in parsed_data]
            return response_model(**parsed_data)

        return parsed_data
    except (json.JSONDecodeError, TypeError):
        try:
            # Fallback to pickle deserialization for complex objects
            import base64
            import pickle

            pickled_data = base64.b64decode(data.encode("utf-8"))
            return pickle.loads(pickled_data)
        except Exception as e:
            logger.warning(f"Cache deserialization error: {e}")
            return None


def cache_response(
    ttl: int,
    cache_client: CacheClient,
    resource: str | None = None,
    key_params: list | None = None,
    response_model: type | None = None,
):
    """Cache decorator for API endpoints.

    Args:
        ttl: Time to live in seconds
        cache_client: Cache client instance
        resource: Resource name for cache key generation
        key_params: List of parameter names to include in cache key
        response_model: Pydantic model for response serialization
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Use function name as resource if not provided
            resource_name = resource or func.__name__

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
            cache_key = generate_cache_key(resource_name, **cache_params)

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
    """Cache decorator for list endpoints."""
    return cache_response(
        ttl=ttl,
        cache_client=cache_client,
        resource=resource,
        key_params=["page", "limit", "search", "filter"],
    )


def cache_detail_endpoint(resource: str, ttl: int = CacheConfig.DETAIL_TTL):
    """Cache decorator for detail endpoints."""
    return cache_response(
        ttl=ttl, cache_client=cache_client, resource=resource, key_params=["id"]
    )


async def invalidate_cache(resource: str, **params) -> None:
    """Invalidate cache entries for a resource."""
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
async def check_cache_health() -> dict[str, Any]:
    """Check cache system health."""
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
        return {
            "status": "degraded",
            "connected": False,
            "message": "Running without cache",
        }
    except Exception as e:
        return {"status": "error", "connected": False, "error": str(e)}
