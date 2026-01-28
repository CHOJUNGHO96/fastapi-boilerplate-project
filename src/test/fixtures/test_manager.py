"""
TestManager - Integrated test fixture management.

Enhancement #1: Test fixture integration and optimization
통합 픽스처 관리 클래스로 테스트 코드 간결화 및 재사용성 향상
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from httpx import AsyncClient


@dataclass
class TestUser:
    """
    테스트 사용자 데이터 및 토큰을 관리하는 클래스.

    사용자 생성부터 로그인, 로그아웃까지 전체 라이프사이클을 관리하여
    테스트 코드를 간결하게 만들고 재사용성을 높입니다.

    Attributes:
        login_id: 사용자 로그인 ID
        email: 사용자 이메일
        password: 사용자 비밀번호
        user_name: 사용자 이름
        user_type: 사용자 타입 (CUSTOMER, ADMIN 등)
        user_id: 데이터베이스 사용자 ID (등록 후 할당)
        access_token: JWT 액세스 토큰 (로그인 후 할당)
        refresh_token: JWT 리프레시 토큰 (로그인 후 할당)
        token_type: 토큰 타입 (기본: Bearer)
    """

    login_id: str
    email: str
    password: str
    user_name: str
    user_type: str
    user_id: Optional[int] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"

    @classmethod
    async def create_and_login(cls, client: AsyncClient) -> "TestUser":
        """
        사용자 생성 및 로그인을 한 번에 처리.

        Args:
            client: AsyncClient 인스턴스

        Returns:
            로그인된 TestUser 인스턴스

        Example:
            ```python
            user = await TestUser.create_and_login(async_client)
            print(user.access_token)  # JWT 토큰 사용 가능
            ```
        """
        from test.helpers.test_data_generator import generate_user_data
        from test.helpers.auth_helper import AuthHelper

        user_data = generate_user_data()

        # Register
        register_response = await AuthHelper.register_user(client, user_data)
        assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
        user_id = register_response.json()["user_id"]

        # Login
        login_response = await AuthHelper.login_user(
            client,
            user_data["login_id"],
            user_data["password"],
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"

        # Extract tokens
        tokens = AuthHelper.extract_tokens_from_cookies(login_response)

        return cls(
            login_id=user_data["login_id"],
            email=user_data["email"],
            password=user_data["password"],
            user_name=user_data["user_name"],
            user_type=user_data["user_type"],
            user_id=user_id,
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            token_type=tokens.get("token_type", "Bearer"),
        )

    @classmethod
    async def create_only(cls, client: AsyncClient) -> "TestUser":
        """
        사용자 등록만 수행 (로그인 없음).

        Args:
            client: AsyncClient 인스턴스

        Returns:
            등록된 TestUser 인스턴스 (토큰 없음)

        Example:
            ```python
            user = await TestUser.create_only(async_client)
            # 나중에 수동으로 로그인 가능
            await user.login(async_client)
            ```
        """
        from test.helpers.test_data_generator import generate_user_data
        from test.helpers.auth_helper import AuthHelper

        user_data = generate_user_data()

        # Register only
        register_response = await AuthHelper.register_user(client, user_data)
        assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
        user_id = register_response.json()["user_id"]

        return cls(
            login_id=user_data["login_id"],
            email=user_data["email"],
            password=user_data["password"],
            user_name=user_data["user_name"],
            user_type=user_data["user_type"],
            user_id=user_id,
        )

    def get_cookies(self) -> Dict[str, str]:
        """
        인증 쿠키 딕셔너리 반환.

        Returns:
            token_type, access_token, refresh_token을 포함한 딕셔너리

        Example:
            ```python
            user = await TestUser.create_and_login(async_client)
            response = await async_client.get(
                "/api/v1/protected",
                cookies=user.get_cookies()
            )
            ```
        """
        if not self.access_token or not self.refresh_token:
            raise ValueError("User is not logged in. Call login() first.")

        return {
            "token_type": self.token_type,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }

    async def login(self, client: AsyncClient) -> None:
        """
        사용자 로그인 및 토큰 업데이트.

        Args:
            client: AsyncClient 인스턴스

        Example:
            ```python
            user = await TestUser.create_only(async_client)
            await user.login(async_client)  # 이제 토큰 사용 가능
            ```
        """
        from test.helpers.auth_helper import AuthHelper

        login_response = await AuthHelper.login_user(
            client,
            self.login_id,
            self.password,
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"

        # Update tokens
        tokens = AuthHelper.extract_tokens_from_cookies(login_response)
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")
        self.token_type = tokens.get("token_type", "Bearer")

    async def logout(self, client: AsyncClient) -> None:
        """
        사용자 로그아웃 및 토큰 제거.

        Args:
            client: AsyncClient 인스턴스

        Example:
            ```python
            user = await TestUser.create_and_login(async_client)
            await user.logout(async_client)  # 토큰 무효화
            ```
        """
        from test.helpers.auth_helper import AuthHelper

        response = await AuthHelper.logout_user(client, cookies=self.get_cookies())
        assert response.status_code == 200, f"Logout failed: {response.text}"

        # Clear tokens
        self.access_token = None
        self.refresh_token = None

    async def refresh_tokens(self, client: AsyncClient) -> None:
        """
        토큰 갱신 및 업데이트.

        Args:
            client: AsyncClient 인스턴스

        Example:
            ```python
            user = await TestUser.create_and_login(async_client)
            await user.refresh_tokens(async_client)  # 새 토큰 발급
            ```
        """
        from test.helpers.auth_helper import AuthHelper

        if not self.refresh_token:
            raise ValueError("No refresh_token available. User must be logged in.")

        response = await AuthHelper.refresh_token(client, self.refresh_token)
        assert response.status_code == 200, f"Token refresh failed: {response.text}"

        # Update tokens
        tokens = AuthHelper.extract_tokens_from_cookies(response)
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")

    def is_logged_in(self) -> bool:
        """
        로그인 상태 확인.

        Returns:
            로그인되어 있으면 True, 아니면 False
        """
        return bool(self.access_token and self.refresh_token)

    def to_dict(self) -> Dict[str, Any]:
        """
        사용자 정보를 딕셔너리로 변환.

        Returns:
            사용자 정보를 담은 딕셔너리
        """
        return {
            "login_id": self.login_id,
            "email": self.email,
            "password": self.password,
            "user_name": self.user_name,
            "user_type": self.user_type,
            "user_id": self.user_id,
        }


class TestManager:
    """
    여러 테스트 사용자와 리소스를 관리하는 매니저 클래스.

    복잡한 테스트 시나리오에서 여러 사용자를 생성하고 관리할 때 유용합니다.

    Example:
        ```python
        async def test_multiple_users(async_client):
            manager = TestManager()

            # 3명의 사용자 생성
            users = await manager.create_multiple_users(async_client, count=3)

            # 모든 사용자로 동시 작업 수행
            # ...

            # 모든 사용자 로그아웃
            await manager.logout_all(async_client)
        ```
    """

    def __init__(self):
        self.users: list[TestUser] = []

    async def create_multiple_users(
        self,
        client: AsyncClient,
        count: int = 3,
        login: bool = True,
    ) -> list[TestUser]:
        """
        여러 사용자를 동시에 생성.

        Args:
            client: AsyncClient 인스턴스
            count: 생성할 사용자 수
            login: 로그인까지 수행할지 여부

        Returns:
            생성된 TestUser 리스트
        """
        import asyncio

        if login:
            tasks = [TestUser.create_and_login(client) for _ in range(count)]
        else:
            tasks = [TestUser.create_only(client) for _ in range(count)]

        self.users = await asyncio.gather(*tasks)
        return self.users

    async def logout_all(self, client: AsyncClient) -> None:
        """
        관리 중인 모든 사용자 로그아웃.

        Args:
            client: AsyncClient 인스턴스
        """
        import asyncio

        tasks = [user.logout(client) for user in self.users if user.is_logged_in()]
        await asyncio.gather(*tasks)

    def get_user(self, index: int = 0) -> TestUser:
        """
        인덱스로 사용자 가져오기.

        Args:
            index: 사용자 인덱스 (기본: 0)

        Returns:
            TestUser 인스턴스
        """
        if not self.users or index >= len(self.users):
            raise IndexError(f"No user at index {index}")
        return self.users[index]

    def clear(self) -> None:
        """관리 중인 사용자 목록 초기화."""
        self.users.clear()
