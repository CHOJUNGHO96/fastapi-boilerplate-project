# coding=utf-8
from dependency_injector.wiring import Provide, inject
from fastapi import Request

from app.auth.model.user_model import ModelTokenData
from app.auth.util.jwt import create_access_token
from infrastructure.db.schema.user import UserInfo


class TokenService:
    @inject
    async def get_token(
        self,
        request: Request,
        user_info: UserInfo | dict[str, str],
        config=Provide["config"],
    ) -> ModelTokenData:
        request.state.user = user_info.to_dict() if isinstance(user_info, UserInfo) else user_info
        token_type = "bearer"
        access_token = create_access_token(
            jwt_secret_key=config["JWT_ACCESS_SECRET_KEY"],
            jwt_algorithm=config["JWT_ALGORITHM"],
            user_id=int(request.state.user["user_id"]),
            login_id=request.state.user["login_id"],
            user_name=request.state.user["user_name"],
            user_type=int(request.state.user["user_type"]),
            expire=config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"],
        )
        refresh_token = create_access_token(
            jwt_secret_key=config["JWT_REFRESH_SECRET_KEY"],
            jwt_algorithm=config["JWT_ALGORITHM"],
            user_id=int(request.state.user["user_id"]),
            login_id=request.state.user["login_id"],
            user_name=request.state.user["user_name"],
            user_type=int(request.state.user["user_type"]),
            expire=config["JWT_REFRESH_TOKEN_EXPIRE_MINUTES"],
        )
        return ModelTokenData(
            user_id=request.state.user["user_id"],
            token_type=token_type,
            access_token=access_token,
            refresh_token=refresh_token,
        )
