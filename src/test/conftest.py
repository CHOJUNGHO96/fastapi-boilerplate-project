import asyncio
import os
from typing import Generator

import pytest
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
    os.environ["API_MODE"] = "test"

    from main import create_app

    yield create_app()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client(app: FastAPI):
    """
    테스트용 클라이언트 (synchronous - for existing tests)
    """
    with TestClient(app, base_url="http://127.0.0.1/api/v1") as client:
        yield client


@pytest.fixture(scope="session")
async def async_client(app: FastAPI) -> AsyncClient:
    """
    비동기 테스트용 클라이언트 (for E2E tests)
    """
    async with AsyncClient(app=app, base_url="http://127.0.0.1") as client:
        yield client


@pytest.fixture(scope="session")
def engine(app: FastAPI) -> AsyncEngine:
    """
    데이터베이스 엔진
    """
    return app.container.db().engine


@pytest.fixture(scope="session")
async def redis(app: FastAPI) -> Redis:
    """
    Redis 클라이언트
    """
    redis_client = app.container.redis()
    yield redis_client
    await redis_client.close()


# Import fixtures from fixtures package
pytest_plugins = [
    "test.fixtures.auth_fixtures",
    "test.fixtures.data_fixtures",
]
