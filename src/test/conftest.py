import asyncio
import os
from typing import Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """
    테스트용 app
    """
    os.environ["API_ENV"] = "test"

    # Set required JWT environment variables for testing
    if "JWT_ACCESS_SECRET_KEY" not in os.environ:
        os.environ["JWT_ACCESS_SECRET_KEY"] = "test-secret-key-for-access-tokens"
    if "JWT_REFRESH_SECRET_KEY" not in os.environ:
        os.environ["JWT_REFRESH_SECRET_KEY"] = "test-secret-key-for-refresh-tokens"

    from main import create_app

    yield create_app()


@pytest.fixture(scope="session")
def client(app: FastAPI):
    """
    테스트용 클라이언트 (synchronous - for existing tests)
    """
    with TestClient(app, base_url="http://127.0.0.1/api/v1") as client:
        yield client


@pytest.fixture
def async_client(app: FastAPI):
    """
    비동기 테스트용 클라이언트 (for E2E tests)

    Note: TestClient를 사용하지만 비동기 테스트에서도 작동합니다.
    TestClient는 내부적으로 ASGI를 동기 방식으로 래핑하여 DI가 정상 작동합니다.
    """
    with TestClient(app, base_url="http://127.0.0.1/api/v1") as client:
        yield client


@pytest.fixture
def engine(app: FastAPI) -> AsyncEngine:
    """
    데이터베이스 엔진
    """
    return app.container.db().engine


@pytest_asyncio.fixture
async def redis(app: FastAPI) -> Redis:
    """
    Redis 클라이언트
    """
    redis_client = app.container.redis()
    # redis_client이 실제 Redis 객체인지 확인
    if hasattr(redis_client, "__await__"):
        redis_client = await redis_client
    yield redis_client
    # cleanup - close if it has close method
    if hasattr(redis_client, "close") and callable(redis_client.close):
        await redis_client.close()


# Import fixtures from current test directory
import sys
from pathlib import Path

# Add test and src directory to path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent

if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fixtures.auth_fixtures import (  # noqa: E402
    clean_db,
    registered_user_data,
    authenticated_user,
    multiple_authenticated_users,
)
from fixtures.data_fixtures import (  # noqa: E402
    valid_user_data,
    invalid_email_data,
    short_password_data,
    sql_injection_data,
    max_length_data,
    unicode_data,
    special_chars_data,
)

__all__ = [
    "clean_db",
    "registered_user_data",
    "authenticated_user",
    "multiple_authenticated_users",
    "valid_user_data",
    "invalid_email_data",
    "short_password_data",
    "sql_injection_data",
    "max_length_data",
    "unicode_data",
    "special_chars_data",
]
