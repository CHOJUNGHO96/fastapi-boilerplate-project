# coding=utf-8
from dependency_injector.wiring import Provide, inject

import errors
from app.auth.domain.user_entity import ModelTokenData
from app.auth.repository.user_repository import Repository as UserRepository
from infrastructure.db.schema.user import UserInfo


class UserUseCase:
    @inject
    async def get_one(
        self,
        user_repository: UserRepository = Provide["auth.user_repository"],
        **kwargs,
    ) -> UserInfo | None:
        where = []
        if kwargs.get("user_id"):
            where.append(UserInfo.user_id == kwargs["user_id"])
        if kwargs.get("login_id"):
            where.append(UserInfo.login_id == kwargs["login_id"])
        if kwargs.get("user_name"):
            where.append(UserInfo.user_name == kwargs["user_name"])
        user_info: UserInfo = await user_repository.one(*where)

        if not user_info:
            raise errors.NotFoundUserEx()

        return user_info

    @inject
    async def set_user_in_redis(
        self,
        user_info: UserInfo | dict[str, str],
        token_data: ModelTokenData,
        redis=Provide["redis"],
        config=Provide["config"],
    ) -> None:
        await redis.set(
            name=f"cahce_user_info_{user_info['login_id']}",
            value=str(
                {
                    "user_id": user_info["user_id"],
                    "login_id": user_info["login_id"],
                    "user_name": user_info["user_name"],
                    "email": user_info["email"],
                    "access_token": token_data.access_token,
                    "refresh_token": token_data.refresh_token,
                }
            ),
            ex=config["REDIS_EXPIRE_TIME"],
        )
