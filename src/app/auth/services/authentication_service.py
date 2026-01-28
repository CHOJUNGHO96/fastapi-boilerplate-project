# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import Depends
from passlib.context import CryptContext

from app.auth.domain.user_entity import UserEntity
from app.auth.repository.user_repository import Repository as UserRepository
from errors import BadPassword, NotFoundUserEx, ValidationError


class AuthService:
    """
    Authentication service for user credential verification.

    This service handles:
    - Password verification
    - User authentication against stored credentials
    """

    def __init__(self, user_repository: UserRepository = Depends()):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_repository = user_repository

    async def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify plain password against hashed password.

        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password

        Returns:
            True if password matches, False otherwise

        Raises:
            BadPassword: If password verification fails
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            raise BadPassword()

    @inject
    async def authenticate(
        self,
        user_id: str,
        user_passwd: str,
    ) -> UserEntity:
        """
        Authenticate user with credentials.

        Args:
            user_id: User's login ID
            user_passwd: User's plain text password

        Returns:
            UserEntity with password field cleared

        Raises:
            NotFoundUserEx: If user not found or password incorrect
            BadPassword: If password verification fails
        """
        # Step 1: Find user by login_id (using Repository directly)
        user_entity: UserEntity | None = await self.user_repository.find_by_login_id(user_id)

        if not user_entity:
            raise NotFoundUserEx()

        # Step 2: Verify password
        if not user_entity.password:
            raise ValidationError("Password is required")

        if not await self.__verify_password(user_passwd, user_entity.password):
            raise NotFoundUserEx()

        # Step 3: Clear password from entity (security)
        user_entity.password = None

        if user_entity.login_id is None:
            raise ValidationError("Login ID is required")

        return user_entity
