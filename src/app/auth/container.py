# coding=utf-8
from dependency_injector import containers, providers

from app.auth.repository.user_repository import Repository as UserRepository
from app.auth.services.authentication_service import AuthService
from app.auth.services.cache_service import CacheService
from app.auth.services.token_service import TokenService
from app.auth.usecases.login_usecase import LoginUseCase
from app.auth.usecases.logout_usecase import LogoutUseCase
from app.auth.usecases.refresh_token_usecase import RefreshTokenUseCase
from app.auth.usecases.register_user_usecase import RegisterUserUseCase


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection container for Auth module.

    Provides:
    - Repositories: Data access layer
    - Services: Business logic and infrastructure abstractions
    - UseCases: Business scenario orchestrators
    """

    db = providers.Singleton()

    # ==================== Repository ====================
    user_repository = providers.Singleton(UserRepository, session_factory=db.provided.session)

    # ==================== Services ====================
    auth_service = providers.Factory(AuthService, user_repository=user_repository)

    token_service = providers.Factory(TokenService)

    cache_service = providers.Factory(CacheService)

    # ==================== UseCases ====================
    login_usecase = providers.Factory(
        LoginUseCase,
        auth_service=auth_service,
        token_service=token_service,
        cache_service=cache_service,
    )

    register_user_usecase = providers.Factory(RegisterUserUseCase, user_repository=user_repository)

    refresh_token_usecase = providers.Factory(
        RefreshTokenUseCase,
        token_service=token_service,
        cache_service=cache_service,
    )

    logout_usecase = providers.Factory(LogoutUseCase, cache_service=cache_service)
