"""
LogoutUseCase - Orchestrates the logout business scenario.

This UseCase handles user logout by clearing the user's cache session.
"""
from fastapi import Depends

from app.auth.services.cache_service import CacheService
from app.auth.usecases.dto import LogoutCommand, LogoutResult


class LogoutUseCase:
    """
    Logout business scenario orchestrator.

    Responsibilities:
    1. Delete user session from cache
    2. Return logout success result

    Note:
        Cookie deletion is handled by the endpoint (HTTP concern),
        not by this UseCase (business logic concern).
    """

    def __init__(self, cache_service: CacheService = Depends()):
        self.cache_service = cache_service

    async def execute(self, command: LogoutCommand) -> LogoutResult:
        """
        Execute the logout business scenario.

        Args:
            command: LogoutCommand with login_id

        Returns:
            LogoutResult indicating success
        """
        # Step 1: Delete user cache
        deleted = await self.cache_service.delete_user_cache(command.login_id)

        # Step 2: Return result
        return LogoutResult(success=True, message="Successfully logged out" if deleted else "User was not cached")
