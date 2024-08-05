# coding=utf-8
from dependency_injector.wiring import Provide, inject

import errors
from app.auth.domain.user_entity import UserEntity
from app.auth.repository.user_repository import Repository as UserRepository
from infrastructure.db.schema.user import UserInfo


class UserUseCase:
    @inject
    async def get_one(
        self,
        user_repository: UserRepository = Provide["auth.user_repository"],
        **kwargs,
    ) -> UserEntity | None:
        where = []
        if kwargs.get("user_id"):
            where.append(UserInfo.user_id == kwargs["user_id"])
        if kwargs.get("login_id"):
            where.append(UserInfo.login_id == kwargs["login_id"])
        if kwargs.get("user_name"):
            where.append(UserInfo.user_name == kwargs["user_name"])
        user_entity: UserEntity = await user_repository.one(*where)

        if not user_entity:
            raise errors.NotFoundUserEx()

        return user_entity

    @inject
    async def user_insert(
        self,
        insert_user_entity: dict,
        user_repository: UserRepository = Provide["auth.user_repository"],
    ) -> bool:
        return await user_repository.insert_user(insert_user_entity)

    @inject
    async def set_user_in_redis(
        self,
        user_entity: UserEntity,
        redis=Provide["redis"],
        config=Provide["config"],
    ) -> None:
        await redis.set(
            name=f"cahce_user_info_{user_entity.login_id}",
            value=str(
                {
                    "user_id": user_entity.user_id,
                    "login_id": user_entity.login_id,
                    "user_name": user_entity.user_name,
                    "user_type": user_entity.user_type,
                    "email": user_entity.email,
                    "access_token": user_entity.access_token,
                    "refresh_token": user_entity.refresh_token,
                }
            ),
            ex=config["REDIS_EXPIRE_TIME"],
        )
