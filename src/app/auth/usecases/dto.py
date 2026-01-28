"""
Command and Result DTOs for Auth UseCases.

Commands represent input data for business operations.
Results represent output data from business operations.
"""
from dataclasses import dataclass

from app.auth.domain.user_entity import UserEntity


@dataclass
class LoginCommand:
    """Command for user login operation."""

    login_id: str
    password: str


@dataclass
class LoginResult:
    """Result of successful login operation."""

    user: UserEntity
    access_token: str
    refresh_token: str
    token_type: str


@dataclass
class RegisterUserCommand:
    """Command for user registration operation."""

    login_id: str
    user_name: str
    password: str
    email: str
    user_type: int


@dataclass
class RegisterUserResult:
    """Result of successful user registration."""

    user_id: int
    login_id: str


@dataclass
class RefreshTokenCommand:
    """Command for token refresh operation."""

    refresh_token: str


@dataclass
class RefreshTokenResult:
    """Result of successful token refresh."""

    user: UserEntity
    access_token: str
    refresh_token: str
    token_type: str


@dataclass
class LogoutCommand:
    """Command for user logout operation."""

    login_id: str


@dataclass
class LogoutResult:
    """Result of successful logout."""

    success: bool
    message: str
