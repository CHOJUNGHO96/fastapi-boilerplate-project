# coding=utf-8
from fastapi import Depends, Request
from fastapi.responses import JSONResponse

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

    async def login(self, reqest: Request, username: str, password: str):
        user_info = await self.auth_service.authenticate(user_id=username, user_passwd=password)
        token_data = await self.token_service.get_token(reqest, user_info=user_info)
        await self.user_cache_service.save_user_in_redis(user_info, token_data)
        response = JSONResponse(content=token_data.dict())
        response.set_cookie("token_type", token_data.token_type)
        response.set_cookie("access_token", token_data.access_token)
        response.set_cookie("refresh_token", token_data.refresh_token)

        return response

    async def logout(self):
        response = JSONResponse(content={"status": 200, "msg": "Suceess Logout."})
        response.delete_cookie(key="token_type")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response
