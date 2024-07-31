# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import Depends
from passlib.context import CryptContext

from app.auth.usecase import UserUseCase
from errors import BadPassword, NotFoundUserEx
from infrastructure.db.schema.user import UserInfo


class AuthService:
    def __init__(self, user_usecase: UserUseCase = Depends()):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_usecase = user_usecase

    async def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            raise BadPassword()

    @inject
    async def authenticate(
        self,
        user_id: str,
        user_passwd: str,
    ) -> UserInfo:
        user_info: UserInfo | None = await self.user_usecase.get_one(login_id=user_id)
        if not user_info:
            raise NotFoundUserEx()
        assert user_info.password, "password is invalid"
        if not await self.__verify_password(user_passwd, user_info.password):
            assert user_info.login_id, "login_id is None"
            raise NotFoundUserEx()
        assert user_info.login_id is not None, "login_id is None"
        return user_info
