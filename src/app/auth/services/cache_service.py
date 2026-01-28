"""
CacheService - Redis abstraction for user cache management.

This service provides an abstraction layer over Redis operations,
isolating infrastructure concerns from business logic.
"""
from typing import Optional

from dependency_injector.wiring import Provide, inject

from app.auth.domain.user_entity import UserEntity


class CacheService:
    """Service for managing user cache in Redis."""

    @inject
    async def save_user_cache(
        self,
        user: UserEntity,
        redis=Provide["redis"],
        config=Provide["config"],
    ) -> None:
        """
        Save user information to Redis cache.

        Args:
            user: UserEntity with user information and tokens
            redis: Redis connection (injected)
            config: Application config (injected)
        """
        cache_key = f"cache_user_info_{user.login_id}"  # Fixed typo: "cahce" -> "cache"
        cache_value = str(
            {
                "user_id": user.user_id,
                "login_id": user.login_id,
                "user_name": user.user_name,
                "user_type": user.user_type,
                "email": user.email,
                "access_token": user.access_token,
                "refresh_token": user.refresh_token,
            }
        )

        await redis.set(
            name=cache_key,
            value=cache_value,
            ex=config["REDIS_EXPIRE_TIME"],
        )

    @inject
    async def get_user_cache(
        self,
        login_id: str,
        redis=Provide["redis"],
    ) -> Optional[str]:
        """
        Retrieve user information from Redis cache.

        Args:
            login_id: User's login ID
            redis: Redis connection (injected)

        Returns:
            Cached user data as string, or None if not found
        """
        cache_key = f"cache_user_info_{login_id}"  # Fixed typo
        cached_user = await redis.get(cache_key)

        if cached_user is None:
            return None

        # Handle bytes or string response
        if isinstance(cached_user, bytes):
            return cached_user.decode()
        return cached_user

    @inject
    async def delete_user_cache(
        self,
        login_id: str,
        redis=Provide["redis"],
    ) -> bool:
        """
        Delete user information from Redis cache.

        Args:
            login_id: User's login ID
            redis: Redis connection (injected)

        Returns:
            True if cache was deleted, False if it didn't exist
        """
        cache_key = f"cache_user_info_{login_id}"  # Fixed typo
        result = await redis.delete(cache_key)
        return result > 0

    @inject
    async def update_user_cache(
        self,
        user: UserEntity,
        redis=Provide["redis"],
        config=Provide["config"],
    ) -> None:
        """
        Update existing user cache with new information.

        This is essentially an alias for save_user_cache since Redis SET
        overwrites existing keys.

        Args:
            user: UserEntity with updated information
            redis: Redis connection (injected)
            config: Application config (injected)
        """
        await self.save_user_cache(user, redis, config)
