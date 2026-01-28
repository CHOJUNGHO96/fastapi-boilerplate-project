"""
TokenHelper - JWT token manipulation utilities for testing.

Enhancement #3: Time manipulation utility for expired token testing
만료된 토큰 테스트를 위한 시간 조작 유틸리티
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional


class TokenHelper:
    """
    JWT 토큰 생성 및 조작 헬퍼 클래스.

    테스트 환경에서 다양한 토큰 시나리오를 생성하여
    만료, 무효화, 곧 만료될 토큰 등을 테스트할 수 있습니다.
    """

    @staticmethod
    def _get_jwt_config():
        """
        JWT 설정 가져오기.

        Returns:
            JWT 비밀키, 알고리즘, 만료 시간 등의 설정
        """
        from config import conf

        config = conf()
        return {
            "secret_key": config.get("JWT_SECRET", "test-secret-key"),
            "refresh_secret_key": config.get("JWT_REFRESH_SECRET", "test-refresh-secret-key"),
            "algorithm": config.get("JWT_ALGORITHM", "HS256"),
            "access_token_expire": config.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 15),
            "refresh_token_expire": config.get("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 3000),
        }

    @staticmethod
    def create_expired_access_token(user_id: int, login_id: str) -> str:
        """
        만료된 access token 생성 (테스트용).

        현재 시간보다 2시간 전에 만료된 토큰을 생성합니다.

        Args:
            user_id: 사용자 ID
            login_id: 사용자 로그인 ID

        Returns:
            만료된 JWT 액세스 토큰

        Example:
            ```python
            expired_token = TokenHelper.create_expired_access_token(1, "testuser")
            # 이 토큰으로 요청 시 ExpireJwtToken 에러 발생
            ```
        """
        config = TokenHelper._get_jwt_config()

        # 과거 시간으로 설정 (2시간 전 만료)
        expired_time = datetime.utcnow() - timedelta(hours=2)

        payload = {
            "user_id": user_id,
            "login_id": login_id,
            "exp": expired_time,
            "iat": expired_time - timedelta(minutes=15),  # 발급 시간
        }

        return jwt.encode(
            payload,
            config["secret_key"],
            algorithm=config["algorithm"],
        )

    @staticmethod
    def create_expired_refresh_token(user_id: int, login_id: str) -> str:
        """
        만료된 refresh token 생성 (테스트용).

        현재 시간보다 8일 전에 만료된 토큰을 생성합니다.

        Args:
            user_id: 사용자 ID
            login_id: 사용자 로그인 ID

        Returns:
            만료된 JWT 리프레시 토큰

        Example:
            ```python
            expired_refresh = TokenHelper.create_expired_refresh_token(1, "testuser")
            # 이 토큰으로 갱신 시 ExpireJwtToken 에러 발생
            ```
        """
        config = TokenHelper._get_jwt_config()

        # 과거 시간으로 설정 (8일 전 만료, refresh token은 7일 유효)
        expired_time = datetime.utcnow() - timedelta(days=8)

        payload = {
            "user_id": user_id,
            "login_id": login_id,
            "exp": expired_time,
            "iat": expired_time - timedelta(days=7),  # 발급 시간
        }

        return jwt.encode(
            payload,
            config["refresh_secret_key"],
            algorithm=config["algorithm"],
        )

    @staticmethod
    def create_token_expiring_soon(
        user_id: int,
        login_id: str,
        seconds: int = 5,
        token_type: str = "access",
    ) -> str:
        """
        곧 만료될 토큰 생성 (테스트용).

        지정된 시간(초) 후에 만료될 토큰을 생성합니다.

        Args:
            user_id: 사용자 ID
            login_id: 사용자 로그인 ID
            seconds: 만료까지 남은 시간(초)
            token_type: 토큰 타입 ("access" 또는 "refresh")

        Returns:
            곧 만료될 JWT 토큰

        Example:
            ```python
            # 5초 후 만료될 토큰
            token = TokenHelper.create_token_expiring_soon(1, "testuser", seconds=5)

            # 테스트: 5초 기다린 후 요청하면 만료 에러 발생
            import asyncio
            await asyncio.sleep(6)
            # 이제 토큰은 만료됨
            ```
        """
        config = TokenHelper._get_jwt_config()

        expiring_time = datetime.utcnow() + timedelta(seconds=seconds)
        issued_time = datetime.utcnow()

        payload = {
            "user_id": user_id,
            "login_id": login_id,
            "exp": expiring_time,
            "iat": issued_time,
        }

        secret_key = config["refresh_secret_key"] if token_type == "refresh" else config["secret_key"]

        return jwt.encode(
            payload,
            secret_key,
            algorithm=config["algorithm"],
        )

    @staticmethod
    def create_valid_access_token(
        user_id: int,
        login_id: str,
        expire_minutes: Optional[int] = None,
    ) -> str:
        """
        유효한 access token 생성 (테스트용).

        Args:
            user_id: 사용자 ID
            login_id: 사용자 로그인 ID
            expire_minutes: 만료 시간(분), None이면 기본값 사용

        Returns:
            유효한 JWT 액세스 토큰

        Example:
            ```python
            # 기본 15분 유효 토큰
            token = TokenHelper.create_valid_access_token(1, "testuser")

            # 커스텀 만료 시간 (30분)
            token = TokenHelper.create_valid_access_token(1, "testuser", expire_minutes=30)
            ```
        """
        config = TokenHelper._get_jwt_config()

        if expire_minutes is None:
            expire_minutes = config["access_token_expire"]

        expire_time = datetime.utcnow() + timedelta(minutes=expire_minutes)
        issued_time = datetime.utcnow()

        payload = {
            "user_id": user_id,
            "login_id": login_id,
            "exp": expire_time,
            "iat": issued_time,
        }

        return jwt.encode(
            payload,
            config["secret_key"],
            algorithm=config["algorithm"],
        )

    @staticmethod
    def create_valid_refresh_token(
        user_id: int,
        login_id: str,
        expire_minutes: Optional[int] = None,
    ) -> str:
        """
        유효한 refresh token 생성 (테스트용).

        Args:
            user_id: 사용자 ID
            login_id: 사용자 로그인 ID
            expire_minutes: 만료 시간(분), None이면 기본값 사용

        Returns:
            유효한 JWT 리프레시 토큰

        Example:
            ```python
            # 기본 3000분 유효 토큰
            token = TokenHelper.create_valid_refresh_token(1, "testuser")
            ```
        """
        config = TokenHelper._get_jwt_config()

        if expire_minutes is None:
            expire_minutes = config["refresh_token_expire"]

        expire_time = datetime.utcnow() + timedelta(minutes=expire_minutes)
        issued_time = datetime.utcnow()

        payload = {
            "user_id": user_id,
            "login_id": login_id,
            "exp": expire_time,
            "iat": issued_time,
        }

        return jwt.encode(
            payload,
            config["refresh_secret_key"],
            algorithm=config["algorithm"],
        )

    @staticmethod
    def create_invalid_token(user_id: int, login_id: str) -> str:
        """
        잘못된 서명을 가진 토큰 생성 (테스트용).

        올바른 JWT 형식이지만 잘못된 비밀키로 서명된 토큰을 생성합니다.

        Args:
            user_id: 사용자 ID
            login_id: 사용자 로그인 ID

        Returns:
            잘못된 서명을 가진 JWT 토큰

        Example:
            ```python
            invalid_token = TokenHelper.create_invalid_token(1, "testuser")
            # 이 토큰으로 요청 시 InvalidJwtToken 에러 발생
            ```
        """
        config = TokenHelper._get_jwt_config()

        expire_time = datetime.utcnow() + timedelta(hours=1)
        issued_time = datetime.utcnow()

        payload = {
            "user_id": user_id,
            "login_id": login_id,
            "exp": expire_time,
            "iat": issued_time,
        }

        # 잘못된 비밀키로 서명
        wrong_secret = "wrong-secret-key-for-testing"

        return jwt.encode(
            payload,
            wrong_secret,
            algorithm=config["algorithm"],
        )

    @staticmethod
    def decode_token(token: str, token_type: str = "access") -> dict:
        """
        토큰 디코딩 (검증 없이).

        Args:
            token: JWT 토큰
            token_type: 토큰 타입 ("access" 또는 "refresh")

        Returns:
            디코딩된 페이로드

        Example:
            ```python
            payload = TokenHelper.decode_token(token)
            print(payload["user_id"])
            print(payload["exp"])  # 만료 시간
            ```
        """
        config = TokenHelper._get_jwt_config()

        secret_key = config["refresh_secret_key"] if token_type == "refresh" else config["secret_key"]

        try:
            return jwt.decode(
                token,
                secret_key,
                algorithms=[config["algorithm"]],
                options={"verify_exp": False},  # 만료 검증 안 함
            )
        except jwt.InvalidTokenError:
            # 잘못된 토큰이라도 디코딩 시도 (검증 없이)
            return jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False},
            )

    @staticmethod
    def is_token_expired(token: str, token_type: str = "access") -> bool:
        """
        토큰이 만료되었는지 확인.

        Args:
            token: JWT 토큰
            token_type: 토큰 타입 ("access" 또는 "refresh")

        Returns:
            만료되었으면 True, 아니면 False

        Example:
            ```python
            is_expired = TokenHelper.is_token_expired(token)
            if is_expired:
                print("Token is expired")
            ```
        """
        try:
            payload = TokenHelper.decode_token(token, token_type)
            exp_timestamp = payload.get("exp")

            if exp_timestamp is None:
                return False

            # UTC 현재 시간과 비교
            current_timestamp = datetime.utcnow().timestamp()
            return current_timestamp > exp_timestamp

        except Exception:
            return True  # 디코딩 실패 시 만료된 것으로 간주
