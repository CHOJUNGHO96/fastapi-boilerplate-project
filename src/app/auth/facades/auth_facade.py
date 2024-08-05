# coding=utf-8
from fastapi import Depends, Request
from fastapi.responses import JSONResponse

from app.auth.domain.user_entity import UserEntity
from app.auth.model import ResponseLoginModel, ResponseTokenModel
from app.auth.model.request import RequestRegisterModel
from app.auth.responses import ResponsJson
from app.auth.services import AuthService, TokenService, UserCacheService, UserService


class AuthFacade:
    def __init__(
        self,
        auth_service: AuthService = Depends(),
        user_cache_service: UserCacheService = Depends(),
        token_service: TokenService = Depends(),
        user_service: UserService = Depends(),
    ):
        self.auth_service = auth_service
        self.user_cache_service = user_cache_service
        self.token_service = token_service
        self.user_service = user_service

    async def login(self, request: Request, username: str, password: str):
        authenticated_user: UserEntity = await self.auth_service.authenticate(user_id=username, user_passwd=password)
        user_with_token: UserEntity = await self.token_service.get_token(request, user_entity=authenticated_user)
        await self.user_cache_service.save_user_in_redis(user_entity=user_with_token)
        response: JSONResponse = ResponsJson.extract_response_fields(
            response_model=ResponseLoginModel, entity=user_with_token
        )
        response.set_cookie("token_type", user_with_token.token_type)
        response.set_cookie("access_token", user_with_token.access_token)
        response.set_cookie("refresh_token", user_with_token.refresh_token)

        return response

    async def logout(self):
        response = JSONResponse(content={"status": 200, "msg": "Suceess Logout."})
        response.delete_cookie(key="token_type")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response

    async def refresh_token(self, request: Request):
        if "refresh_token" in request.cookies:
            user_entity_from_state = UserEntity.from_dict(request.state.user)
            user_with_token: UserEntity = await self.token_service.get_token(
                request, user_entity=user_entity_from_state
            )
            await self.user_cache_service.save_user_in_redis(user_entity=user_with_token)
            response: JSONResponse = ResponsJson.extract_response_fields(
                response_model=ResponseTokenModel, entity=user_with_token
            )
            response.set_cookie("token_type", user_with_token.token_type)
            response.set_cookie("access_token", user_with_token.access_token)
            response.set_cookie("refresh_token", user_with_token.refresh_token)
            return response
        else:
            return JSONResponse(status_code=422, content={"status": 422, "msg": "Token not in cookie"})

    async def register(self, request: RequestRegisterModel):
        if await self.user_service.register(request):
            return JSONResponse(content={"status": 200, "msg": "Success Register."})
