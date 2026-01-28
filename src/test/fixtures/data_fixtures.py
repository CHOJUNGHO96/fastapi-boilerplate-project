"""Test data fixtures for E2E testing."""

import pytest
from typing import Dict, Any

from test.helpers.test_data_generator import (
    generate_user_data,
    generate_invalid_email,
    generate_short_password,
    generate_sql_injection_payload,
    generate_max_length_string,
    generate_unicode_string,
    generate_special_characters_string,
)


@pytest.fixture
def valid_user_data() -> Dict[str, Any]:
    """Generate valid user registration data."""
    return generate_user_data()


@pytest.fixture
def invalid_email_data() -> Dict[str, Any]:
    """Generate user data with invalid email format."""
    return generate_user_data(email=generate_invalid_email())


@pytest.fixture
def short_password_data() -> Dict[str, Any]:
    """Generate user data with short password."""
    return generate_user_data(password=generate_short_password())


@pytest.fixture
def sql_injection_data() -> Dict[str, Any]:
    """Generate user data with SQL injection payload."""
    return generate_user_data(login_id=generate_sql_injection_payload())


@pytest.fixture
def max_length_data() -> Dict[str, Any]:
    """Generate user data with maximum length fields."""
    return generate_user_data(
        login_id=generate_max_length_string(50),
        email=f"{generate_max_length_string(240)}@test.com",
        user_name=generate_max_length_string(100),
    )


@pytest.fixture
def unicode_data() -> Dict[str, Any]:
    """Generate user data with Unicode characters."""
    return generate_user_data(
        user_name=generate_unicode_string(),
    )


@pytest.fixture
def special_chars_data() -> Dict[str, Any]:
    """Generate user data with special characters in name."""
    return generate_user_data(
        user_name=generate_special_characters_string(),
    )
