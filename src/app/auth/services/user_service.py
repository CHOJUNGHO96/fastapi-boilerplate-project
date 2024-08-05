from dependency_injector.wiring import inject
from fastapi import Depends

from app.auth.domain.user_entity import UserEntity
from app.auth.model.request import RequestRegisterModel
from app.auth.usecase.user_usecase import UserUseCase


class UserService:
    def __init__(self, user_usecase: UserUseCase = Depends()):
        self.user_usecase = user_usecase

    async def register(self, request_user_info: RequestRegisterModel) -> bool:
        request_entity = UserEntity.from_dict(request_user_info.dict())
        deleted_none_data_entity = UserEntity.delete_to_dict_none_data(request_entity)
        return await self.user_usecase.user_insert(deleted_none_data_entity)

    @inject
    async def save_user_in_redis(
        self,
        user_entity: UserEntity,
    ) -> None:
        await self.user_usecase.set_user_in_redis(user_entity=user_entity)
