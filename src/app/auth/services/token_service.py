# coding=utf-8
from dependency_injector.wiring import Provide, inject
from fastapi import Request

from app.auth.domain.user_entity import UserEntity
from app.auth.util.jwt import create_access_token


class TokenService:
    @inject
    async def get_token(
        self,
        request: Request,
        user_entity: UserEntity | dict,
        config=Provide["config"],
    ) -> UserEntity:
        request.state.user = user_entity.to_dict() if isinstance(user_entity, UserEntity) else user_entity
        token_type = "bearer"
        access_token = create_access_token(
            jwt_secret_key=config["JWT_ACCESS_SECRET_KEY"],
            jwt_algorithm=config["JWT_ALGORITHM"],
            user_id=int(request.state.user["user_id"]),
            login_id=request.state.user["login_id"],
            user_name=request.state.user["user_name"],
            user_type=int(request.state.user["user_type"]) if "user_type" in request.state.user else None,
            expire=config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"],
        )
        refresh_token = create_access_token(
            jwt_secret_key=config["JWT_REFRESH_SECRET_KEY"],
            jwt_algorithm=config["JWT_ALGORITHM"],
            user_id=int(request.state.user["user_id"]),
            login_id=request.state.user["login_id"],
            user_name=request.state.user["user_name"],
            user_type=int(request.state.user["user_type"]) if "user_type" in request.state.user else None,
            expire=config["JWT_REFRESH_TOKEN_EXPIRE_MINUTES"],
        )
        user_entity.access_token = access_token
        user_entity.refresh_token = refresh_token
        user_entity.token_type = token_type
        user_entity.user_id = int(request.state.user["user_id"])
        return user_entity
