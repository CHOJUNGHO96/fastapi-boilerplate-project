"""
개선사항 데모 테스트.

이 파일은 구현된 개선사항들이 실제로 어떻게 사용되는지 보여줍니다:
- Enhancement #1: TestUser/TestManager 클래스
- Enhancement #2: ErrorCode 상수
- Enhancement #3: TokenHelper 유틸리티
"""

import pytest
from httpx import AsyncClient

from errors import ErrorCode
from test.fixtures.test_manager import TestUser, TestManager
from test.helpers.token_helper import TokenHelper
from test.helpers.auth_helper import AuthHelper


# ============================================================================
# Enhancement #1 데모: TestUser 클래스 사용
# ============================================================================


@pytest.mark.asyncio
async def test_demo_test_user_simple(async_client: AsyncClient, clean_db):
    """
    TestUser 클래스를 사용한 간단한 테스트.

    기존 방식 대비 코드가 훨씬 간결해집니다.
    """
    # 한 줄로 사용자 생성 및 로그인
    user = await TestUser.create_and_login(async_client)

    # 로그인 상태 확인
    assert user.is_logged_in()
    assert user.access_token is not None

    # 보호된 엔드포인트 접근 (쿠키 자동 생성)
    response = await async_client.post(
        "/api/v1/auth/logout",
        cookies=user.get_cookies(),
    )
    assert response.status_code == 200

    # 로그아웃 후 상태 확인
    assert not user.is_logged_in()


@pytest.mark.asyncio
async def test_demo_test_user_workflow(async_client: AsyncClient, clean_db):
    """
    TestUser로 전체 워크플로우 관리.
    """
    # 등록만 수행
    user = await TestUser.create_only(async_client)
    assert not user.is_logged_in()

    # 수동 로그인
    await user.login(async_client)
    assert user.is_logged_in()

    # 토큰 갱신
    old_access_token = user.access_token
    await user.refresh_tokens(async_client)
    assert user.access_token != old_access_token

    # 로그아웃
    await user.logout(async_client)
    assert not user.is_logged_in()


@pytest.mark.asyncio
async def test_demo_test_manager_multiple_users(async_client: AsyncClient, clean_db):
    """
    TestManager로 여러 사용자 관리.
    """
    manager = TestManager()

    # 3명의 사용자 동시 생성
    users = await manager.create_multiple_users(async_client, count=3, login=True)

    # 모든 사용자가 로그인됨
    for user in users:
        assert user.is_logged_in()

    # 첫 번째 사용자 가져오기
    first_user = manager.get_user(0)
    assert first_user.access_token is not None

    # 모든 사용자 로그아웃
    await manager.logout_all(async_client)

    # 모든 사용자가 로그아웃됨
    for user in users:
        assert not user.is_logged_in()


# ============================================================================
# Enhancement #2 데모: ErrorCode 상수 사용
# ============================================================================


@pytest.mark.asyncio
async def test_demo_error_code_constants(async_client: AsyncClient, clean_db):
    """
    ErrorCode 상수를 사용한 명확한 에러 검증.

    기존: expected_error_code=4010003  (매직 넘버)
    개선: expected_error_code=ErrorCode.NOT_FOUND_USER  (명확한 상수)
    """
    # 존재하지 않는 사용자로 로그인 시도
    response = await AuthHelper.login_user(
        async_client,
        "nonexistent_user",
        "somepassword",
    )

    # 명확한 상수 사용
    AuthHelper.assert_error_response(
        response,
        expected_status=404,
        expected_error_code=ErrorCode.NOT_FOUND_USER,  # ✅ 명확함
    )


@pytest.mark.asyncio
async def test_demo_error_code_duplicate_user(async_client: AsyncClient, clean_db):
    """
    중복 사용자 에러 검증.
    """
    user = await TestUser.create_only(async_client)

    # 같은 login_id로 재등록 시도
    from test.helpers.test_data_generator import generate_user_data

    duplicate_data = generate_user_data(
        login_id=user.login_id,  # 중복
        email="different@email.com",
    )

    response = await AuthHelper.register_user(async_client, duplicate_data)

    # 중복 사용자 에러 확인
    AuthHelper.assert_error_response(
        response,
        expected_status=400,
        expected_error_code=ErrorCode.DUPLICATE_USER,  # ✅ 명확함
    )


# ============================================================================
# Enhancement #3 데모: TokenHelper 사용
# ============================================================================


@pytest.mark.asyncio
async def test_demo_expired_token_with_helper(async_client: AsyncClient, clean_db):
    """
    TokenHelper로 만료된 토큰 테스트.

    기존: pytest.skip("Requires time manipulation")
    개선: TokenHelper로 즉시 테스트 가능
    """
    # 사용자 생성
    user = await TestUser.create_and_login(async_client)

    # 만료된 access token 생성
    expired_token = TokenHelper.create_expired_access_token(
        user.user_id,
        user.login_id,
    )

    # 만료 확인
    assert TokenHelper.is_token_expired(expired_token)

    # 만료된 토큰으로 로그아웃 시도
    response = await async_client.post(
        "/api/v1/auth/logout",
        cookies={
            "token_type": "Bearer",
            "access_token": expired_token,
            "refresh_token": user.refresh_token,
        },
    )

    # 만료 에러 확인
    AuthHelper.assert_error_response(
        response,
        expected_status=401,
        expected_error_code=ErrorCode.EXPIRE_JWT_TOKEN,  # ✅ 명확한 상수 + 만료 토큰
    )


@pytest.mark.asyncio
async def test_demo_invalid_token_with_helper(async_client: AsyncClient, clean_db):
    """
    TokenHelper로 잘못된 토큰 테스트.
    """
    user = await TestUser.create_and_login(async_client)

    # 잘못된 서명의 토큰 생성
    invalid_token = TokenHelper.create_invalid_token(
        user.user_id,
        user.login_id,
    )

    # 잘못된 토큰으로 로그아웃 시도
    response = await async_client.post(
        "/api/v1/auth/logout",
        cookies={
            "token_type": "Bearer",
            "access_token": invalid_token,
            "refresh_token": user.refresh_token,
        },
    )

    # 잘못된 토큰 에러 확인
    AuthHelper.assert_error_response(
        response,
        expected_status=401,
        expected_error_code=ErrorCode.INVALID_JWT_TOKEN,  # ✅ 명확한 상수
    )


@pytest.mark.asyncio
async def test_demo_token_expiring_soon(async_client: AsyncClient, clean_db):
    """
    TokenHelper로 곧 만료될 토큰 테스트.
    """
    import asyncio

    user = await TestUser.create_and_login(async_client)

    # 5초 후 만료될 토큰 생성
    expiring_token = TokenHelper.create_token_expiring_soon(
        user.user_id,
        user.login_id,
        seconds=5,
    )

    # 현재는 유효함
    assert not TokenHelper.is_token_expired(expiring_token)

    # 6초 대기
    await asyncio.sleep(6)

    # 이제 만료됨
    assert TokenHelper.is_token_expired(expiring_token)


# ============================================================================
# 통합 데모: 모든 개선사항 함께 사용
# ============================================================================


@pytest.mark.asyncio
async def test_demo_all_improvements_together(async_client: AsyncClient, clean_db):
    """
    모든 개선사항을 함께 사용한 복합 시나리오.

    시나리오:
    1. TestManager로 여러 사용자 생성
    2. 첫 번째 사용자 토큰 만료
    3. ErrorCode로 명확한 에러 검증
    """
    # Enhancement #1: TestManager로 사용자 관리
    manager = TestManager()
    users = await manager.create_multiple_users(async_client, count=2, login=True)

    first_user = manager.get_user(0)
    second_user = manager.get_user(1)

    # Enhancement #3: TokenHelper로 만료된 토큰 생성
    expired_token = TokenHelper.create_expired_access_token(
        first_user.user_id,
        first_user.login_id,
    )

    # 만료된 토큰으로 요청
    response = await async_client.post(
        "/api/v1/auth/logout",
        cookies={
            "token_type": "Bearer",
            "access_token": expired_token,
            "refresh_token": first_user.refresh_token,
        },
    )

    # Enhancement #2: ErrorCode로 명확한 검증
    AuthHelper.assert_error_response(
        response,
        expected_status=401,
        expected_error_code=ErrorCode.EXPIRE_JWT_TOKEN,
    )

    # 두 번째 사용자는 정상 로그아웃 가능
    await second_user.logout(async_client)
    assert not second_user.is_logged_in()

    # 정리
    await manager.logout_all(async_client)
