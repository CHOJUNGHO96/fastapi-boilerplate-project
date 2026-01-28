"""Authentication-related test fixtures."""

import pytest
from typing import Dict, Any
from httpx import AsyncClient

from test.helpers.test_data_generator import generate_user_data
from test.helpers.auth_helper import AuthHelper
from test.helpers.db_helper import ensure_clean_database
from test.helpers.redis_helper import RedisHelper


@pytest.fixture
async def clean_db(engine, redis):
    """
    Ensure clean database and Redis cache before each test.

    Args:
        engine: Database engine from conftest
        redis: Redis client from conftest

    Yields:
        None (setup fixture)
    """
    # Clean database
    await ensure_clean_database(engine)

    # Clean Redis test caches
    await RedisHelper.clear_all_test_caches(redis)

    yield

    # Cleanup after test
    await RedisHelper.clear_all_test_caches(redis)


@pytest.fixture
def registered_user_data() -> Dict[str, Any]:
    """
    Generate test user data for registration.

    Returns:
        Dictionary with valid user registration data
    """
    return generate_user_data()


@pytest.fixture
async def authenticated_user(async_client: AsyncClient, clean_db, registered_user_data) -> Dict[str, Any]:
    """
    Create and authenticate a test user, returning user data and tokens.

    Args:
        async_client: AsyncClient from conftest
        clean_db: Clean database fixture
        registered_user_data: User registration data

    Returns:
        Dictionary with user_data and tokens (token_type, access_token, refresh_token)
    """
    # Register user
    register_response = await AuthHelper.register_user(async_client, registered_user_data)
    assert register_response.status_code == 200

    # Login user
    login_response = await AuthHelper.login_user(
        async_client,
        registered_user_data["login_id"],
        registered_user_data["password"],
    )
    assert login_response.status_code == 200

    # Extract tokens
    tokens = AuthHelper.extract_tokens_from_cookies(login_response)

    return {
        "user_data": registered_user_data,
        "tokens": tokens,
        "login_response": login_response,
    }


@pytest.fixture
async def multiple_authenticated_users(
    async_client: AsyncClient,
    clean_db,
) -> list[Dict[str, Any]]:
    """
    Create multiple authenticated test users for concurrent testing.

    Args:
        async_client: AsyncClient from conftest
        clean_db: Clean database fixture

    Returns:
        List of dictionaries with user_data and tokens for each user
    """
    users = []

    for i in range(3):
        user_data = generate_user_data()

        # Register
        register_response = await AuthHelper.register_user(async_client, user_data)
        assert register_response.status_code == 200

        # Login
        login_response = await AuthHelper.login_user(
            async_client,
            user_data["login_id"],
            user_data["password"],
        )
        assert login_response.status_code == 200

        # Extract tokens
        tokens = AuthHelper.extract_tokens_from_cookies(login_response)

        users.append(
            {
                "user_data": user_data,
                "tokens": tokens,
                "login_response": login_response,
            }
        )

    return users
