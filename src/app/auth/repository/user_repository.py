# coding=utf-8
from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.schema.user import UserInfo


class Repository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ) -> None:
        self.session_factory = session_factory

    async def one(self, *where) -> UserInfo | None:
        async with self.session_factory() as session:
            user_info = await session.scalars(select(UserInfo).where(*where))
            user_info = user_info.first()
            if not user_info:
                return None
            else:
                return user_info
