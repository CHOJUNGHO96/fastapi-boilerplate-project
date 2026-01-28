# coding=utf-8
import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, AsyncIterator

from sqlalchemy import TextClause, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import ORMExecuteState, Session

from config import conf
from infrastructure.db.dialect import LiteralDialect

config = conf()
logger = logging.getLogger("query")


class AsyncEngine:
    def __init__(self, config):
        self._config = config
        self.engine = create_async_engine(
            str(config["SQLALCHEMY_DATABASE_URI"]),
            future=True,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=50,
            pool_recycle=3600,  # Recycle connections after 1 hour
            connect_args={
                "server_settings": {
                    "timezone": "Asia/Seoul",
                    "search_path": self._config["POSTGRES_SCHEMA"],
                },
            },
        )

        self._session_factory = async_sessionmaker(
            self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def session(
        self,
    ) -> AsyncIterator[AbstractAsyncContextManager[AsyncSession]]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()


@event.listens_for(Session, "do_orm_execute")
def print_query(state: ORMExecuteState):
    if not config.DEBUG or not config.SQL_PRINT:
        return

    query = state.statement
    if state.parameters and isinstance(query, TextClause):
        query = query.params(state.parameters)

    print(
        str(
            query.compile(
                dialect=LiteralDialect(),
                compile_kwargs={"literal_binds": True},
            )
        ).replace("\n", " ")
    )


# Query Service
async def exec(session, sql: str, bind_param=None) -> Any:
    if bind_param is None:
        bind_param = dict()

    query = await session.execute(text(sql), bind_param)
    return query.rowcount or 0


async def first(session, sql: str, bind_param: dict | None = None) -> Any:
    if bind_param is None:
        bind_param = dict()

    query = await session.execute(text(sql), bind_param)
    if ret := query.first():
        return ret._asdict()
    else:
        return {}


async def all(session, sql: str, bind_param: dict | None = None) -> Any:
    if bind_param is None:
        bind_param = dict()

    query = await session.execute(text(sql), bind_param)
    if ret := query.all():
        return [r._asdict() for r in ret]
    else:
        return []
