"""
RegisterUserUseCase - Orchestrates the user registration business scenario.

This UseCase handles new user registration including duplicate validation,
password hashing, and user creation.
"""
from fastapi import Depends
from passlib.context import CryptContext

from app.auth.repository.user_repository import Repository as UserRepository
from app.auth.usecases.dto import RegisterUserCommand, RegisterUserResult
from errors import DuplicateUserEx


class RegisterUserUseCase:
    """
    User registration business scenario orchestrator.

    Responsibilities:
    1. Validate no duplicate login_id or email exists
    2. Hash the user's password
    3. Save new user to database
    4. Return registration result with user_id
    """

    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        """
        Execute the user registration business scenario.

        Args:
            command: RegisterUserCommand with user information

        Returns:
            RegisterUserResult with user_id and login_id

        Raises:
            DuplicateUserEx: If login_id or email already exists
        """
        # Step 1: Validate no duplicate login_id
        if await self.user_repository.exists_by_login_id(command.login_id):
            raise DuplicateUserEx(user_id=command.login_id)

        # Step 2: Validate no duplicate email
        if await self.user_repository.exists_by_email(command.email):
            raise DuplicateUserEx(user_id=command.email)

        # Step 3: Hash password
        hashed_password = self.pwd_context.hash(command.password)

        # Step 4: Save user to database
        user_id = await self.user_repository.save(
            {
                "login_id": command.login_id,
                "user_name": command.user_name,
                "password": hashed_password,
                "email": command.email,
                "user_type": command.user_type,
            }
        )

        # Step 5: Return result
        return RegisterUserResult(user_id=user_id, login_id=command.login_id)
