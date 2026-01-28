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
        max_connections=20,
        retry_on_timeout=True,
        health_check_interval=30,
    )
    yield session
    await session.close()


@inject
async def get_user_cache(login_id: str, conf: get_config, redis=Provide["redis"]) -> str | None:
    """
    유저정보 캐시로 관리
    """
    if redis is None:
        raise ValueError("Redis 인스턴스가 초기화되지 않았습니다.")
    cache_user = await redis.get(f"cache_user_info_{login_id}")
    if cache_user is None:
        await redis.set(
            name=f"cache_user_info_{login_id}",
            value=cache_user,
            ex=conf["redis_expire_time"],
        )
        cache_user = await redis.get(f"cache_user_info_{login_id}")
    if isinstance(cache_user, bytes):
        cache_user = cache_user.decode()
        return cache_user
    elif isinstance(cache_user, str):
        return cache_user
