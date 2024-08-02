# coding=utf-8
from fastapi import Depends, Request
from fastapi.responses import JSONResponse

from app.auth.domain.user_entity import UserEntity
from app.auth.model.user_model import ResponseLoginModel
from app.auth.responses import ResponsJson
from app.auth.services import AuthService, TokenService, UserCacheService


class AuthFacade:
    def __init__(
        self,
        auth_service: AuthService = Depends(),
        user_cache_service: UserCacheService = Depends(),
        token_service: TokenService = Depends(),
    ):
        self.auth_service = auth_service
        self.user_cache_service = user_cache_service
        self.token_service = token_service

    async def login(self, request: Request, username: str, password: str):
        user_entity: UserEntity = await self.auth_service.authenticate(user_id=username, user_passwd=password)
        user_entity: UserEntity = await self.token_service.get_token(request, user_entity=user_entity)
        await self.user_cache_service.save_user_in_redis(user_entity=user_entity)
        response: JSONResponse = ResponsJson.extract_response_fields(
            response_model=ResponseLoginModel, entity=user_entity
        )
        response.set_cookie("token_type", user_entity.token_type)
        response.set_cookie("access_token", user_entity.access_token)
        response.set_cookie("refresh_token", user_entity.refresh_token)

        return response

    async def logout(self):
        response = JSONResponse(content={"status": 200, "msg": "Suceess Logout."})
        response.delete_cookie(key="token_type")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response
