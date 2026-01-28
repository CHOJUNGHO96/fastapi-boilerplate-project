# coding=utf-8
from contextlib import AbstractAsyncContextManager
from typing import Callable, Optional

from sqlalchemy import exists as sql_exists
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.user_entity import UserEntity
from errors import InternalQuerryEx
from infrastructure.db.schema.user import UserInfo


class Repository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ) -> None:
        self.session_factory = session_factory

    # ==================== New Specific Query Methods ====================

    async def find_by_login_id(self, login_id: str) -> Optional[UserEntity]:
        """
        Find user by login_id.

        Args:
            login_id: User's login ID

        Returns:
            UserEntity if found, None otherwise
        """
        async with self.session_factory() as session:
            result = await session.scalars(select(UserInfo).where(UserInfo.login_id == login_id))
            user_info = result.first()
            return self._to_entity(user_info) if user_info else None

    async def find_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Find user by email.

        Args:
            email: User's email address

        Returns:
            UserEntity if found, None otherwise
        """
        async with self.session_factory() as session:
            result = await session.scalars(select(UserInfo).where(UserInfo.email == email))
            user_info = result.first()
            return self._to_entity(user_info) if user_info else None

    async def exists_by_login_id(self, login_id: str) -> bool:
        """
        Check if user exists by login_id.

        Args:
            login_id: User's login ID

        Returns:
            True if user exists, False otherwise
        """
        async with self.session_factory() as session:
            stmt = select(sql_exists().where(UserInfo.login_id == login_id))
            result = await session.scalar(stmt)
            return result

    async def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.

        Args:
            email: User's email address

        Returns:
            True if user exists, False otherwise
        """
        async with self.session_factory() as session:
            stmt = select(sql_exists().where(UserInfo.email == email))
            result = await session.scalar(stmt)
            return result

    async def save(self, user_data: dict) -> int:
        """
        Save new user to database.

        Args:
            user_data: Dictionary containing user information
                      (login_id, user_name, password, email, user_type)

        Returns:
            user_id of the newly created user

        Raises:
            InternalQuerryEx: If database operation fails
        """
        try:
            async with self.session_factory() as session:
                result = await session.execute(insert(UserInfo).values(**user_data))
                await session.flush()
                # Get the inserted user_id
                user_id = result.inserted_primary_key[0]
                return user_id
        except Exception as e:
            raise InternalQuerryEx(ex=e)

    def _to_entity(self, user_info: UserInfo) -> UserEntity:
        """
        Convert UserInfo schema model to UserEntity domain model.

        Args:
            user_info: SQLAlchemy UserInfo model

        Returns:
            UserEntity domain model
        """
        return UserEntity(
            user_id=user_info.user_id,
            login_id=user_info.login_id,
            password=user_info.password,
            user_name=user_info.user_name,
            email=user_info.email,
            user_type=user_info.user_type,
        )

    # ==================== DEPRECATED Methods (will be removed) ====================

    async def one(self, *where) -> UserEntity | None:
        """
        DEPRECATED: Use find_by_login_id() or find_by_email() instead.

        This method will be removed in future versions.
        """
        async with self.session_factory() as session:
            user_info = await session.scalars(select(UserInfo).where(*where))
            user_info = user_info.first()
            if not user_info:
                return None
            else:
                return self._to_entity(user_info)

    async def insert_user(self, insert_user_entity: dict) -> bool:
        """
        DEPRECATED: Use save() instead.

        This method will be removed in future versions.
        """
        try:
            async with self.session_factory() as session:
                await session.execute(insert(UserInfo).values(**insert_user_entity))
                return True
        except InternalQuerryEx as e:
            raise InternalQuerryEx(ex=e)
