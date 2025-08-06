"""
Unit tests for cache module
Tests Redis caching functionality and fallback behavior
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from surgify.core.cache import (CacheClient, CacheConfig, cache_response,
                                generate_cache_key, invalidate_cache)


class TestCacheClient:
    """Test Redis cache client functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.cache_client = CacheClient()

    @pytest.mark.asyncio
    async def test_cache_client_connection_success(self):
        """Test successful Redis connection"""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_redis.return_value = mock_instance
            mock_instance.ping.return_value = True

            client = await self.cache_client._get_client()

            assert client is not None
            mock_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_client_connection_failure(self):
        """Test Redis connection failure and fallback"""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_redis.side_effect = Exception("Redis connection failed")

            client = await self.cache_client._get_client()

            # Should return None on connection failure
            assert client is None

    @pytest.mark.asyncio
    async def test_cache_get_success(self):
        """Test successful cache retrieval"""
        with patch.object(self.cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.get.return_value = json.dumps({"test": "data"})

            result = await self.cache_client.get("test_key")

            assert result == {"test": "data"}
            mock_client.get.assert_called_once_with("surgify:test_key")

    @pytest.mark.asyncio
    async def test_cache_get_miss(self):
        """Test cache miss scenario"""
        with patch.object(self.cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.get.return_value = None

            result = await self.cache_client.get("test_key")

            assert result is None

    @pytest.mark.asyncio
    async def test_cache_set_success(self):
        """Test successful cache storage"""
        with patch.object(self.cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.setex.return_value = True

            result = await self.cache_client.set("test_key", {"test": "data"}, ttl=300)

            assert result is True
            mock_client.setex.assert_called_once_with(
                "surgify:test_key", 300, json.dumps({"test": "data"}, default=str)
            )

    @pytest.mark.asyncio
    async def test_cache_set_failure(self):
        """Test cache storage failure"""
        with patch.object(self.cache_client, "_get_client") as mock_get_client:
            mock_get_client.return_value = None  # Simulate no Redis connection

            result = await self.cache_client.set("test_key", {"test": "data"})

            assert result is False

    @pytest.mark.asyncio
    async def test_cache_invalidate_pattern(self):
        """Test cache invalidation by pattern"""
        with patch.object(self.cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.keys.return_value = ["surgify:user:123", "surgify:user:456"]
            mock_client.delete.return_value = 2

            result = await self.cache_client.invalidate_pattern("user:*")

            assert result == 2
            mock_client.keys.assert_called_once_with("surgify:user:*")
            mock_client.delete.assert_called_once_with(
                "surgify:user:123", "surgify:user:456"
            )


class TestCacheDecorators:
    """Test cache decorators and utilities"""

    def test_cache_key_generation(self):
        """Test cache key generation"""
        key = generate_cache_key("users", user_id=123, active=True)

        assert key.startswith("users:")
        assert "123" in key
        assert "True" in key

    def test_cache_key_with_request(self):
        """Test cache key generation with request data"""
        mock_request = Mock()
        mock_request.url.path = "/api/v1/cases"
        mock_request.query_params = {"page": "1", "limit": "10"}

        key = generate_cache_key("cases", request=mock_request)

        assert "cases:" in key
        assert "page" in key
        assert "limit" in key

    @pytest.mark.asyncio
    async def test_cache_response_decorator_hit(self):
        """Test cache response decorator with cache hit"""
        mock_cache_client = AsyncMock()
        mock_cache_client.get.return_value = {"cached": "data"}

        @cache_response(ttl=300, cache_client=mock_cache_client)
        async def test_endpoint():
            return {"fresh": "data"}

        result = await test_endpoint()

        assert result == {"cached": "data"}
        mock_cache_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_response_decorator_miss(self):
        """Test cache response decorator with cache miss"""
        mock_cache_client = AsyncMock()
        mock_cache_client.get.return_value = None
        mock_cache_client.set.return_value = True

        @cache_response(ttl=300, cache_client=mock_cache_client)
        async def test_endpoint():
            return {"fresh": "data"}

        result = await test_endpoint()

        assert result == {"fresh": "data"}
        mock_cache_client.get.assert_called_once()
        mock_cache_client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_response_decorator_error_fallback(self):
        """Test cache decorator fallback on Redis error"""
        mock_cache_client = AsyncMock()
        mock_cache_client.get.side_effect = Exception("Redis error")

        @cache_response(ttl=300, cache_client=mock_cache_client)
        async def test_endpoint():
            return {"fresh": "data"}

        result = await test_endpoint()

        # Should return fresh data when cache fails
        assert result == {"fresh": "data"}


class TestCacheIntegration:
    """Integration tests for cache functionality"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cache_with_api_endpoint(self):
        """Test cache integration with actual API endpoint"""
        # This would test actual Redis integration
        # Skip if Redis is not available in test environment
        pass

    def test_cache_performance_impact(self):
        """Test cache performance impact on endpoint response times"""
        # Performance testing for cache hit/miss scenarios
        pass

    def test_cache_memory_usage(self):
        """Test cache memory usage patterns"""
        # Memory usage testing for different cache sizes
        pass


class TestCacheConfiguration:
    """Test cache configuration and settings"""

    def test_cache_config_defaults(self):
        """Test default cache configuration values"""
        assert CacheConfig.DEFAULT_TTL == 300
        assert CacheConfig.LIST_TTL == 60
        assert CacheConfig.DETAIL_TTL == 600
        assert CacheConfig.KEY_PREFIX == "surgify"

    def test_cache_config_customization(self):
        """Test custom cache configuration"""
        with patch("src.surgify.core.cache.get_settings") as mock_settings:
            mock_settings.return_value.cache_ttl = 600

            # Test that custom settings are respected
            # This would require modifying the cache implementation
            # to support dynamic configuration
            pass


@pytest.mark.asyncio
class TestCacheEdgeCases:
    """Test cache edge cases and error scenarios"""

    async def test_cache_large_data_serialization(self):
        """Test caching of large data structures"""
        cache_client = CacheClient()
        large_data = {"data": "x" * 10000}  # Large data structure

        with patch.object(cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.setex.return_value = True

            result = await cache_client.set("large_key", large_data)

            assert result is True
            # Verify that large data was properly serialized
            call_args = mock_client.setex.call_args
            assert len(call_args[0][2]) > 10000  # Serialized data should be large

    async def test_cache_complex_object_serialization(self):
        """Test caching of complex Python objects"""
        cache_client = CacheClient()

        # Test with datetime objects and other complex types
        from datetime import datetime

        complex_data = {
            "timestamp": datetime.now(),
            "nested": {"list": [1, 2, 3], "dict": {"key": "value"}},
        }

        with patch.object(cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.setex.return_value = True

            result = await cache_client.set("complex_key", complex_data)

            assert result is True

    async def test_cache_concurrent_access(self):
        """Test cache behavior under concurrent access"""
        cache_client = CacheClient()

        async def concurrent_cache_operation(key: str, data: dict):
            return await cache_client.set(key, data)

        # Simulate concurrent cache operations
        tasks = [concurrent_cache_operation(f"key_{i}", {"data": i}) for i in range(10)]

        with patch.object(cache_client, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_client.setex.return_value = True

            results = await asyncio.gather(*tasks)

            # All operations should succeed
            assert all(results)
            assert mock_client.setex.call_count == 10
