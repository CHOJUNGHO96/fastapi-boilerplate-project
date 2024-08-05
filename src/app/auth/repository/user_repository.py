# coding=utf-8
from contextlib import AbstractAsyncContextManager
from typing import Callable

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

    async def one(self, *where) -> UserEntity | None:
        async with self.session_factory() as session:
            user_info = await session.scalars(select(UserInfo).where(*where))
            user_info = user_info.first()
            if not user_info:
                return None
            else:
                user_entity = UserEntity(
                    user_id=user_info.user_id,
                    login_id=user_info.login_id,
                    password=user_info.password,
                    user_name=user_info.user_name,
                    email=user_info.email,
                    user_type=user_info.user_type,
                )
                return user_entity

    async def insert_user(self, insert_user_entity: dict) -> bool:
        try:
            async with self.session_factory() as session:
                await session.execute(insert(UserInfo).values(**insert_user_entity))
                return True
        except InternalQuerryEx as e:
            raise InternalQuerryEx(ex=e)
