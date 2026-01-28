"""Test data generation utilities for E2E testing."""

import random
import string
from typing import Dict, Any


def generate_user_data(
    login_id: str = None,
    email: str = None,
    password: str = None,
    user_name: str = None,
    user_type: str = "CUSTOMER",
) -> Dict[str, Any]:
    """
    Generate valid user data for registration.

    Args:
        login_id: User login ID (default: random)
        email: User email (default: random)
        password: User password (default: "ValidPass123!")
        user_name: User name (default: random)
        user_type: User type (default: "CUSTOMER")

    Returns:
        Dictionary with valid user data
    """
    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    return {
        "login_id": login_id or f"testuser_{random_suffix}",
        "email": email or f"test_{random_suffix}@example.com",
        "password": password or "ValidPass123!",
        "user_name": user_name or f"Test User {random_suffix}",
        "user_type": user_type,
    }


def generate_invalid_email() -> str:
    """Generate invalid email format for testing."""
    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        "user@.com",
        "user..name@example.com",
        "user@example",
    ]
    return random.choice(invalid_emails)


def generate_short_password() -> str:
    """Generate password that's too short (< 8 characters)."""
    return "Short1!"


def generate_sql_injection_payload() -> str:
    """Generate SQL injection test payload."""
    payloads = [
        "'; DROP TABLE users; --",
        "admin' OR '1'='1",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "1' OR '1' = '1",
    ]
    return random.choice(payloads)


def generate_max_length_string(length: int = 255) -> str:
    """
    Generate string of specified length for boundary testing.

    Args:
        length: String length (default: 255)

    Returns:
        String of specified length
    """
    return "a" * length


def generate_unicode_string() -> str:
    """Generate string with Unicode characters for testing."""
    unicode_strings = [
        "사용자이름",  # Korean
        "ユーザー名",  # Japanese
        "用户名",  # Chinese
        "Имя_пользователя",  # Russian
        "مستخدم",  # Arabic
        "👤User🔐Name",  # Emojis
    ]
    return random.choice(unicode_strings)


def generate_special_characters_string() -> str:
    """Generate string with special characters."""
    return "!@#$%^&*()_+-=[]{}|;':\"<>?,./"


def generate_empty_or_whitespace() -> str:
    """Generate empty or whitespace-only string."""
    whitespace_strings = [
        "",
        " ",
        "   ",
        "\t",
        "\n",
        "  \t\n  ",
    ]
    return random.choice(whitespace_strings)
