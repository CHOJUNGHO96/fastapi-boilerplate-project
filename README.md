# Fastapi Boilerplate Project
> Fastapi로 프로젝트 시작시 사용할수있는 보일러플레이트 프로젝트입니다.

![Static Badge](https://img.shields.io/badge/Python-%233776AB)
![Static Badge](https://img.shields.io/badge/Fastapi-%23009688)
![Static Badge](https://img.shields.io/badge/PostgreSql-%234169E1)
![Static Badge](https://img.shields.io/badge/Sqlalchemy-%23D71F00)
![Static Badge](https://img.shields.io/badge/Dependency_Injector-blue)
![Static Badge](https://img.shields.io/badge/Poetry-%2360A5FA)
![Static Badge](https://img.shields.io/badge/Gunicorn-%23499848)
![Static Badge](https://img.shields.io/badge/Docker-%232496ED)
![Static Badge](https://img.shields.io/badge/JwtToken-red)

## 해당프로젝트 특징
#### 1. 파이썬 Fastapi프레임워크를 기반으로 Fastapi공식문서에 나온 웹소켓 기능과 Dependency_Injector라이브러리를 활용하여 웹채팅서비스 구축하였습니다.<br>
#### FastApi웹소켓 공식문서 참고 URL : https://fastapi.tiangolo.com/ko/advanced/websockets/#handling-disconnections-and-multiple-clients
#### dependency-injector 공식문서 URL : https://python-dependency-injector.ets-labs.org/
#### 2. 서비스 레이어에 facade를 적용하여 엔드포인트와 서비스간의 인터페이스 제공하여 의존성 감소, 테스트코드 용이함, 가독성과 유지보수성 향상하였습니다.
#### 3. precommit을 사용하여 commit시 자동으로 black, flake8, toml-sort, isort 실행되도록해서 유효성검사 추가하였습니다.
#### 4. docker cpmpose를 이용하여 명령어입력하면 자동으로 빌드되도록 추가하였습니다.
#### 5. 마이그레이션을위한 alembic 추가하였습니다.
#### 6. jwt token을 사용하여 사용자인증 구현 하였습니다.
#### 7. orm을 사용하기위해 sqlalchemy2.x 와 mongodb는 odmantic라이브러리 사용하였습니다.
#### 8. 유저정보 캐시에저장하기위해 redis 사용하였습니다.

----------
## 프로젝트 디렉토리 구조
```shell
  src
    ├─app
    │  └─auth
    │      ├─domain    
    │      ├─endpoint  
    │      ├─facades
    │      ├─model
    │      ├─repository
    │      ├─services
    │      ├─usecase
    │      ├─util
    ├─infrastructure
    │  └─db
    │      ├─schema
    ├─logs
    ├─scripts
   
```
- src : 프로젝트의 모든 소스코드가 위치하는 디렉토리
- app : 프로젝트의 모든 비즈니스 로직이 위치하는 디렉토리
  - auth : 인증 관련 비즈니스 로직이 위치하는 디렉토리
    - domain : 도메인 엔터티 파일이 위치하는 디렉토리
    - endpoint : 엔드포인트 로직이 위치하는 디렉토리
    - facades : 서비스 레이어에 facade패턴을 적용한 파일이 위치하는 디렉토리
    - model : 벨리데이션 검사를위한 모델 로직이 위치하는 디렉토리
    - repository : 레포지토리 로직이 위치하는 디렉토리
    - services : 서비스 로직이 위치하는 디렉토리
    - usecase : 유스케이스 로직이 위치하는 디렉토리
    - util : 유틸 로직이 위치하는 디렉토리
- infrastructure : 프로젝트의 모든 외부 로직이 위치하는 디렉토리
  - db : 데이터베이스 관련 로직이 위치하는 디렉토리
    - schema : 스키마 로직이 위치하는 디렉토리
- logs : 프로젝트의 모든 로그 파일이 위치하는 디렉토리
- scripts : 프로젝트의 모든 스크립트 파일이 위치하는 디렉토리

----------
## 프로젝트 아키텍처 구조

![img.png](img.png)

- endpoint : 클라이언트의 요청을 받아 서비스 레이어로 전달하는 역할만 합니다.
```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.model.user_model import ModelTokenData
from app.auth.services.auth_facade import AuthFacade

router = APIRouter()
@router.post("/login", response_model=ModelTokenData)
@inject
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_facade: AuthFacade = Depends(),
):
    response: JSONResponse = await auth_facade.login(request, username=form_data.username, password=form_data.password)
    return response

```

</br>

- service facade layer : 다양한 비지니스 로직을 Facade패턴을 사용하여 단순화된 하나의 인터페이스로 통합 합니다.
```python
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

    ...

```

</br>

- service business layer : 비지니스 로직을 처리하는 서비스 레이어입니다.
```python
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
```

</br>

- usecase layer : 서비스 레이어에서 비지니스 로직을 처리하기 위한 유스케이스 레이어입니다.
```python
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

```

</br>

- interface layer : 유스케이스 레이어와 데이터베이스 레이어의 인터페이스를 제공하는 레이어입니다. (Dependency_Injector사용, 경로 : app/auth/container.py)
```python
# coding=utf-8
from dependency_injector import containers, providers

from app.auth.repository.user_repository import Repository as UserRepository


class Container(containers.DeclarativeContainer):
    db = providers.Singleton()

    # Repository
    user_repository = providers.Singleton(UserRepository, session_factory=db.provided.session)

```

</br>

- repository layer : 데이터베이스와 직접적으로 통신하는 레이어입니다.
```python
# coding=utf-8
from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.schema.user import UserInfo


class Repository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ) -> None:
        self.session_factory = session_factory

    async def one(self, *where) -> UserInfo | None:
        async with self.session_factory() as session:
            user_info = await session.scalars(select(UserInfo).where(*where))
            user_info = user_info.first()
            if not user_info:
                return None
            else:
                return user_info
```

----------


## 업데이트 내역


## 정보

조정호 – jo4186@naver.com

[https://github.com/CHOJUNGHO96/github-link](https://github.com/CHOJUNGHO96)

## 기여 방법

1. (<https://github.com/CHOJUNGHO96/fastapi-chat-project/fork>)을 포크합니다.
2. (`git checkout -b feature/fooBar`) 명령어로 새 브랜치를 만드세요.
3. (`git commit -am 'Add some fooBar'`) 명령어로 커밋하세요.
4. (`git push origin feature/fooBar`) 명령어로 브랜치에 푸시하세요. 
5. 풀리퀘스트를 보내주세요.

<!-- Markdown link & img dfn's -->
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
