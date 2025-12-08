# tenebrinet/core/cache.py
"""
Redis caching layer for TenebriNET.

Provides caching functionality for frequently accessed data to reduce
database load and improve API response times.
"""
import json
import os
from typing import Any, Optional

import redis.asyncio as redis


class CacheManager:
    """Manages Redis caching operations."""

    def __init__(self):
        """Initialize the cache manager with Redis connection."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 60  # Default TTL: 60 seconds

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists, None otherwise
        """
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # Log error but don't fail - cache is optional
            print(f"Cache get error: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds (default: 60)

        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., "stats:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return 0

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis.close()


# Global cache instance
cache = CacheManager()
