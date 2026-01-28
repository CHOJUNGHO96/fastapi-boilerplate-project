"""
LoginUseCase - Orchestrates the login business scenario.

This UseCase coordinates authentication, token generation, and cache management
to complete the user login flow.
"""
from fastapi import Depends, Request

from app.auth.services.authentication_service import AuthService
from app.auth.services.cache_service import CacheService
from app.auth.services.token_service import TokenService
from app.auth.usecases.dto import LoginCommand, LoginResult


class LoginUseCase:
    """
    Login business scenario orchestrator.

    Responsibilities:
    1. Authenticate user credentials
    2. Generate access and refresh tokens
    3. Store user session in cache
    4. Return login result with tokens
    """

    def __init__(
        self,
        auth_service: AuthService = Depends(),
        token_service: TokenService = Depends(),
        cache_service: CacheService = Depends(),
    ):
        self.auth_service = auth_service
        self.token_service = token_service
        self.cache_service = cache_service

    async def execute(self, request: Request, command: LoginCommand) -> LoginResult:
        """
        Execute the login business scenario.

        Args:
            request: FastAPI Request object (needed for token generation)
            command: LoginCommand with login_id and password

        Returns:
            LoginResult with user entity and tokens

        Raises:
            NotFoundUserEx: If user not found or password incorrect
            BadPassword: If password verification fails
        """
        # Step 1: Authenticate user (verify credentials)
        user = await self.auth_service.authenticate(command.login_id, command.password)

        # Step 2: Generate access and refresh tokens
        user_with_tokens = await self.token_service.get_token(request, user)

        # Step 3: Save user session to cache
        await self.cache_service.save_user_cache(user_with_tokens)

        # Step 4: Return result with user data and tokens
        return LoginResult(
            user=user_with_tokens,
            access_token=user_with_tokens.access_token,
            refresh_token=user_with_tokens.refresh_token,
            token_type=user_with_tokens.token_type,
        )
