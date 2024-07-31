# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import Depends

from app.auth.domain.user_entity import ModelTokenData
from app.auth.usecase import UserUseCase
from infrastructure.db.schema.user import UserInfo


class UserCacheService:
    def __init__(self, user_usecase: UserUseCase = Depends()):
        self.user_usecase = user_usecase

    @inject
    async def save_user_in_redis(
        self,
        user_info: UserInfo | dict[str, str],
        token_data: ModelTokenData,
    ) -> None:
        user_info = user_info.to_dict() if isinstance(user_info, UserInfo) else user_info
        await self.user_usecase.set_user_in_redis(user_info=user_info, token_data=token_data)
