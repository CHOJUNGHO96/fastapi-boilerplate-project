# coding=utf-8
from typing import AsyncIterator

from dependency_injector.wiring import Provide, inject
from redis import asyncio as aioredis

from config import conf as get_config


async def init_redis_pool(host: str, password: str, port: int) -> AsyncIterator[aioredis.Redis]:
    session = await aioredis.from_url(
        f"redis://{host}",
        port=port,
        password=password,
        encoding="utf-8",
        decode_responses=True,
    )
    yield session
    await session.close()


@inject
async def get_user_cahce(login_id: str, conf: get_config, redis=Provide["redis"]) -> str | None:
    """
    유저정보 캐시로 관리
    """
    if redis is None:
        raise ValueError("Redis 인스턴스가 초기화되지 않았습니다.")
    cahce_user = await redis.get(f"cahce_user_info_{login_id}")
    if cahce_user is None:
        await redis.set(
            name=f"cahce_user_info_{login_id}",
            value=cahce_user,
            ex=conf["redis_expire_time"],
        )
        cahce_user = await redis.get(f"cahce_user_info_{login_id}")
    if isinstance(cahce_user, bytes):
        cahce_user = cahce_user.decode()
        return cahce_user
    elif isinstance(cahce_user, str):
        return cahce_user
