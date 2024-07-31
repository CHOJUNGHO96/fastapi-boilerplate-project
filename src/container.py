# coding=utf-8
from dependency_injector import containers, providers
from fastapi.requests import Request

from app.auth.container import Container as AuthContainer
from config import conf
from infrastructure.db.redis import init_redis_pool
from infrastructure.db.sqlalchemy import AsyncEngine
from logs.log import LogAdapter


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            # redis
            "infrastructure.db.redis",
            # auth
            "app.auth.endpoint",
            "app.auth.usecase",
            "app.auth.services",
        ],
    )

    _config = conf()
    config = providers.Configuration()
    config.from_dict(_config.dict())

    # logging 의존성 주입
    logging = providers.Singleton(LogAdapter, request=Request, response=None, error=None)

    db = providers.Singleton(AsyncEngine, config=config)

    redis = providers.Resource(
        init_redis_pool,
        host=_config.REDIS_SERVER,
        password=_config.REDIS_PASSWORD,
        port=_config.REDIS_PORT,
    )

    auth = providers.Container(AuthContainer, db=db)
