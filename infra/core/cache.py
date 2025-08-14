"""Shared Cache Manager
Centralized cache management for all apps.
"""

import pickle
from abc import ABC, abstractmethod
from typing import Any


try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import get_shared_config
from .logging import get_logger


class CacheBackend(ABC):
    """Abstract cache backend."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache."""


class MemoryCache(CacheBackend):
    """In-memory cache backend."""

    def __init__(self) -> None:
        self._cache = {}
        self.logger = get_logger("yaz.cache.memory")

    async def get(self, key: str) -> Any | None:
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        self._cache[key] = value
        # Note: TTL not implemented for memory cache
        return True

    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def clear(self) -> bool:
        self._cache.clear()
        return True


class RedisCache(CacheBackend):
    """Redis cache backend."""

    def __init__(self, redis_url: str) -> None:
        if not REDIS_AVAILABLE:
            msg = "redis package is required for RedisCache"
            raise ImportError(msg)

        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.logger = get_logger("yaz.cache.redis")

    async def get(self, key: str) -> Any | None:
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            self.logger.exception(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        try:
            serialized = pickle.dumps(value)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized)
            return self.redis_client.set(key, serialized)
        except Exception as e:
            self.logger.exception(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            self.logger.exception(f"Redis delete error: {e}")
            return False

    async def clear(self) -> bool:
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            self.logger.exception(f"Redis clear error: {e}")
            return False


class CacheManager:
    """Cache manager with automatic backend selection."""

    def __init__(self, app_name: str = "yaz") -> None:
        self.app_name = app_name
        self.config = get_shared_config()
        self.logger = get_logger(f"{app_name}.cache")

        # Initialize backend
        self.backend = self._create_backend()

    def _create_backend(self) -> CacheBackend:
        """Create appropriate cache backend."""
        if REDIS_AVAILABLE and self.config.redis_url:
            try:
                return RedisCache(self.config.redis_url)
            except Exception as e:
                self.logger.warning(
                    f"Failed to connect to Redis: {e}, falling back to memory cache"
                )

        return MemoryCache()

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        return f"{self.app_name}:{key}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        return await self.backend.get(self._make_key(key))

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache."""
        ttl = ttl or self.config.cache_ttl
        return await self.backend.set(self._make_key(key), value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        return await self.backend.delete(self._make_key(key))

    async def clear(self) -> bool:
        """Clear all cache for this app."""
        # For now, this clears all cache - could be improved to only clear app-specific keys
        return await self.backend.clear()

    async def get_or_set(self, key: str, factory, ttl: int | None = None) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)
        if value is None:
            value = factory() if callable(factory) else factory
            await self.set(key, value, ttl)
        return value


# Global cache instance
_cache_manager: CacheManager | None = None


def get_cache_manager(app_name: str = "yaz") -> CacheManager:
    """Get cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(app_name)
    return _cache_manager
