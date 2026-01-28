"""Tests module."""

import pytest
from dependency_injector import containers
from fastapi.testclient import TestClient

from infrastructure.db.schema.base import Base


async def delete_data(container: containers):
    """
    테스트전 스키마에있는 테이블 생성및 모든 테이블 데이터 삭제
    """
    db = container.db()

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with db.session() as session:
        for table in Base.metadata.sorted_tables:
            await session.execute(table.delete())


@pytest.mark.asyncio
async def test_registration(client: TestClient):
    """Test user registration with new UseCase-based architecture."""
    await delete_data(client.app.container)
    response = client.post(
        url="auth/register",
        json={
            "email": "test@test.com",  # Fixed: was "user_email"
            "login_id": "test",
            "password": "test123!",  # Fixed: was "user_password"
            "user_name": "테스트유저",
            "user_type": 1,  # Added: required field
        },
    )
    response_body = response.json()
    assert response.status_code == 200
    assert response_body["msg"] == "Success Register."
    assert "user_id" in response_body  # New: UseCase returns user_id
    assert "login_id" in response_body  # New: UseCase returns login_id


@pytest.mark.asyncio
async def test_login(client: TestClient):
    response = client.post(
        url="auth/login",
        data={
            "username": "test",
            "password": "test123!",
        },
    )
    response_body = response.json()
    assert response.status_code == 200
    assert "access_token" in response_body["list"]
    client.app_state.update(
        {"user_id": response_body["list"]["user_id"], "login_id": response_body["list"]["login_id"]}
    )
    client.headers.update({"authorization": f"{response_body['list']['access_token']}"})
