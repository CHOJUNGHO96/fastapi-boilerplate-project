# coding=utf-8
from dependency_injector.wiring import inject
from fastapi import Depends
from passlib.context import CryptContext

from app.auth.domain.user_entity import UserEntity
from app.auth.usecase import UserUseCase
from errors import BadPassword, NotFoundUserEx


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
    ) -> UserEntity:
        user_entity: UserEntity | None = await self.user_usecase.get_one(login_id=user_id)
        if not user_entity:
            raise NotFoundUserEx()
        assert user_entity.password, "password is invalid"
        if not await self.__verify_password(user_passwd, user_entity.password):
            assert user_entity.login_id, "login_id is None"
            raise NotFoundUserEx()
        user_entity.password = None
        assert user_entity.login_id is not None, "login_id is None"

        return user_entity
