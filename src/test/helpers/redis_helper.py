"""Redis cache helper utilities for E2E testing."""

from typing import Optional
from redis.asyncio import Redis
import json


class RedisHelper:
    """Helper class for Redis cache operations in tests."""

    @staticmethod
    def _get_cache_key(login_id: str) -> str:
        """
        Generate cache key for user.

        Args:
            login_id: User login_id

        Returns:
            Redis cache key
        """
        return f"cache_user_info_{login_id}"

    @staticmethod
    async def clear_user_cache(redis: Redis, login_id: str):
        """
        Clear cache for specific user.

        Args:
            redis: Redis client instance
            login_id: User login_id
        """
        cache_key = RedisHelper._get_cache_key(login_id)
        await redis.delete(cache_key)

    @staticmethod
    async def get_user_cache(redis: Redis, login_id: str) -> Optional[dict]:
        """
        Get cached user data.

        Args:
            redis: Redis client instance
            login_id: User login_id

        Returns:
            Cached user data or None
        """
        cache_key = RedisHelper._get_cache_key(login_id)
        cached_data = await redis.get(cache_key)

        if cached_data:
            # Handle both string and bytes
            if isinstance(cached_data, bytes):
                cached_data = cached_data.decode("utf-8")
            return json.loads(cached_data)
        return None

    @staticmethod
    async def set_user_cache(redis: Redis, login_id: str, user_data: dict):
        """
        Set cache for user.

        Args:
            redis: Redis client instance
            login_id: User login_id
            user_data: User data to cache
        """
        cache_key = RedisHelper._get_cache_key(login_id)
        await redis.set(cache_key, json.dumps(user_data))

    @staticmethod
    async def verify_cache_exists(redis: Redis, login_id: str) -> bool:
        """
        Verify that cache exists for user.

        Args:
            redis: Redis client instance
            login_id: User login_id

        Returns:
            True if cache exists, False otherwise
        """
        cache_key = RedisHelper._get_cache_key(login_id)
        return await redis.exists(cache_key) > 0

    @staticmethod
    async def verify_cache_deleted(redis: Redis, login_id: str) -> bool:
        """
        Verify that cache is deleted for user.

        Args:
            redis: Redis client instance
            login_id: User login_id

        Returns:
            True if cache does not exist, False otherwise
        """
        return not await RedisHelper.verify_cache_exists(redis, login_id)

    @staticmethod
    async def clear_all_test_caches(redis: Redis):
        """
        Clear all test-related caches (keys starting with cache_user_info_testuser).

        Args:
            redis: Redis client instance
        """
        # Get all cache keys for test users
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match="cache_user_info_testuser*", count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break

    @staticmethod
    async def workaround_cache_bug(redis: Redis, login_id: str) -> Optional[dict]:
        """
        Workaround for Redis cache bug where None is stored.
        Uses CacheService to properly retrieve user cache.

        NOTE: This is a temporary workaround for the bug in src/infrastructure/db/redis.py:33-36
        where cache_user=None gets stored to Redis.

        Args:
            redis: Redis client instance
            login_id: User login_id

        Returns:
            Cached user data or None
        """
        from app.auth.services.cache_service import CacheService

        cache_service = CacheService()
        return await cache_service.get_user_cache(login_id, redis)
