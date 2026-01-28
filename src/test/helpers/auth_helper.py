"""Authentication helper utilities for E2E testing."""

from typing import Dict, Any, Optional, Union
from httpx import AsyncClient, Response
from fastapi.testclient import TestClient

# Import ErrorCode for better test assertions
from errors import ErrorCode


class AuthHelper:
    """Helper class for authentication-related test operations."""

    @staticmethod
    def register_user(
        client: Union[AsyncClient, TestClient],
        user_data: Dict[str, Any],
    ) -> Response:
        """
        Register a new user.

        Args:
            client: AsyncClient or TestClient instance
            user_data: User registration data

        Returns:
            Response from registration endpoint
        """
        return client.post("auth/register", json=user_data)

    @staticmethod
    def login_user(
        client: Union[AsyncClient, TestClient],
        username: str,
        password: str,
    ) -> Response:
        """
        Login user using OAuth2 form format.

        Args:
            client: AsyncClient or TestClient instance
            username: User login_id
            password: User password

        Returns:
            Response from login endpoint with cookies
        """
        return client.post(
            "auth/login",
            data={
                "username": username,
                "password": password,
            },
        )

    @staticmethod
    def logout_user(
        client: Union[AsyncClient, TestClient],
        cookies: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Logout user.

        Args:
            client: AsyncClient or TestClient instance
            cookies: Optional cookies to include in request

        Returns:
            Response from logout endpoint
        """
        if cookies:
            return client.post("auth/logout", cookies=cookies)
        return client.post("auth/logout")

    @staticmethod
    def refresh_token(
        client: Union[AsyncClient, TestClient],
        refresh_token: str,
    ) -> Response:
        """
        Refresh access token using refresh token.

        Args:
            client: AsyncClient or TestClient instance
            refresh_token: Refresh token from login

        Returns:
            Response from refresh_token endpoint
        """
        return client.get(
            "auth/refresh_token",
            cookies={"refresh_token": refresh_token},
        )

    @staticmethod
    def extract_tokens_from_cookies(response: Response) -> Dict[str, str]:
        """
        Extract authentication tokens from response cookies.

        Args:
            response: Response object with Set-Cookie headers

        Returns:
            Dictionary with token_type, access_token, refresh_token
        """
        cookies = {}
        for cookie in response.cookies.jar:
            cookies[cookie.name] = cookie.value
        return cookies

    @staticmethod
    def assert_token_in_cookies(
        response: Response,
        expected_tokens: list = None,
    ):
        """
        Assert that expected tokens are present in response cookies.

        Args:
            response: Response object to check
            expected_tokens: List of expected token names (default: all three tokens)
        """
        if expected_tokens is None:
            expected_tokens = ["token_type", "access_token", "refresh_token"]

        cookie_names = [cookie.name for cookie in response.cookies.jar]
        for token in expected_tokens:
            assert token in cookie_names, f"Expected '{token}' in cookies, but got: {cookie_names}"

    @staticmethod
    def assert_cookies_deleted(response: Response):
        """
        Assert that authentication cookies are deleted (Max-Age=0).

        Args:
            response: Response object to check
        """
        for cookie in response.cookies.jar:
            if cookie.name in ["token_type", "access_token", "refresh_token"]:
                # Check if cookie is marked for deletion (empty value or Max-Age=0)
                assert (
                    cookie.value == "" or cookie.get("max-age") == "0"
                ), f"Cookie '{cookie.name}' should be deleted but has value: {cookie.value}"

    @staticmethod
    def assert_error_response(
        response: Response,
        expected_status: int,
        expected_error_code: Optional[int] = None,
        expected_message_contains: Optional[str] = None,
    ):
        """
        Assert error response structure and content.

        Args:
            response: Response object to check
            expected_status: Expected HTTP status code
            expected_error_code: Expected application error code (optional)
            expected_message_contains: Substring expected in error message (optional)
        """
        assert (
            response.status_code == expected_status
        ), f"Expected status {expected_status}, got {response.status_code}: {response.text}"

        if expected_error_code is not None:
            data = response.json()
            assert "error_code" in data, f"Expected 'error_code' in response, got: {data}"
            assert (
                data["error_code"] == expected_error_code
            ), f"Expected error_code {expected_error_code}, got {data['error_code']}"

        if expected_message_contains is not None:
            data = response.json()
            message = data.get("message", "") or data.get("detail", "")
            assert (
                expected_message_contains.lower() in message.lower()
            ), f"Expected '{expected_message_contains}' in message, got: {message}"

    @staticmethod
    def register_and_login(
        client: Union[AsyncClient, TestClient],
        user_data: Dict[str, Any],
    ) -> tuple[Response, Response, Dict[str, str]]:
        """
        Register a user and immediately login.

        Args:
            client: AsyncClient or TestClient instance
            user_data: User registration data

        Returns:
            Tuple of (register_response, login_response, tokens_dict)
        """
        register_response = AuthHelper.register_user(client, user_data)
        login_response = AuthHelper.login_user(
            client,
            user_data["login_id"],
            user_data["password"],
        )
        tokens = AuthHelper.extract_tokens_from_cookies(login_response)
        return register_response, login_response, tokens
