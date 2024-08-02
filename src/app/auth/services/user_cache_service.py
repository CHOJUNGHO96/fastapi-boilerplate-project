# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import Depends

from app.auth.domain.user_entity import UserEntity
from app.auth.usecase import UserUseCase


class UserCacheService:
    def __init__(self, user_usecase: UserUseCase = Depends()):
        self.user_usecase = user_usecase

    @inject
    async def save_user_in_redis(
        self,
        user_entity: UserEntity,
    ) -> None:
        await self.user_usecase.set_user_in_redis(user_entity=user_entity)
