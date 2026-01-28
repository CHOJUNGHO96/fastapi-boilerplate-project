"""
RefreshTokenUseCase - Orchestrates the token refresh business scenario.

This UseCase handles access token regeneration using a valid refresh token.
"""
from fastapi import Depends, Request

from app.auth.domain.user_entity import UserEntity
from app.auth.services.cache_service import CacheService
from app.auth.services.token_service import TokenService
from app.auth.usecases.dto import RefreshTokenCommand, RefreshTokenResult


class RefreshTokenUseCase:
    """
    Token refresh business scenario orchestrator.

    Responsibilities:
    1. Regenerate access and refresh tokens from existing user session
    2. Update user cache with new tokens
    3. Return new tokens
    """

    def __init__(
        self,
        token_service: TokenService = Depends(),
        cache_service: CacheService = Depends(),
    ):
        self.token_service = token_service
        self.cache_service = cache_service

    async def execute(self, request: Request, command: RefreshTokenCommand) -> RefreshTokenResult:
        """
        Execute the token refresh business scenario.

        Args:
            request: FastAPI Request object with user state from middleware
            command: RefreshTokenCommand with refresh_token

        Returns:
            RefreshTokenResult with new tokens

        Note:
            The middleware should have already validated the refresh_token
            and populated request.state.user with user information.
        """
        # Step 1: Get user from request state (set by middleware after token validation)
        user_entity = UserEntity.from_dict(request.state.user)

        # Step 2: Generate new tokens
        user_with_tokens = await self.token_service.get_token(request, user_entity)

        # Step 3: Update cache with new tokens
        await self.cache_service.update_user_cache(user_with_tokens)

        # Step 4: Return result with new tokens
        return RefreshTokenResult(
            user=user_with_tokens,
            access_token=user_with_tokens.access_token,
            refresh_token=user_with_tokens.refresh_token,
            token_type=user_with_tokens.token_type,
        )
