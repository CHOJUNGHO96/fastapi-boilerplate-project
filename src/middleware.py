import ast
import re
import time

import sqlalchemy.exc
from dependency_injector import containers
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import conf as get_config
from errors import (
    APIException,
    ExpireJwtToken,
    InternalSqlEx,
    NotAuthorization,
    NotFoundUserEx,
)
from infrastructure.db.redis import get_user_cache
from logs.log import LogAdapter


async def dispatch_middlewares(request: Request, call_next):
    container: containers = request.app.container
    config: get_config = container.config()
    logger: LogAdapter = container.logging()

    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None

    headers = request.headers
    cookies = request.cookies

    # 프록시를 사용하여 x-forwarded-for 헤더가 있으면 그 값을, 없으면 클라이언트의 IP 주소를 사용합니다.
    if "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"]
    elif request.client is not None and request.client.host is not None:
        ip = request.client.host
    else:
        ip = "unknown"
    request.state.ip = ip.split(",")[0] if "," in ip else ip

    # 토큰검증없이 접속가능한 url 처리 작업
    url = request.url.path

    try:
        if url == "/api/v1/auth/refresh_token":
            pass
        elif await url_pattern_check(url, "^(/docs|/redoc|/api/v1/auth|/api/v1/health)") or url in [
            "/",
            "/openapi.json",
        ]:
            response = await call_next(request)
            if url != "/":
                await logger.process(request=request, response=response)
            return response

        # 토큰검증후 HTTP 요청처리
        token = {
            "access_token": (
                str(headers.get("authorization"))
                if "authorization" in headers.keys()
                else (str(cookies.get("access_token")) if "access_token" in cookies.keys() else None)
            ),
            "refresh_token": str(cookies.get("refresh_token") if "refresh_token" in cookies.keys() else None),
        }

        try:
            if token.get("access_token"):
                payload = jwt.decode(
                    token["access_token"],
                    config["JWT_ACCESS_SECRET_KEY"],
                    algorithms=config["JWT_ALGORITHM"],
                )
                login_id: str | None = payload.get("login_id")
                if login_id is None:
                    raise NotAuthorization()
                user_info = await get_user_cache(login_id=login_id, conf=config)
                request.state.user = ast.literal_eval(user_info)
                if not user_info:
                    raise NotFoundUserEx()
            else:
                raise NotAuthorization()
        except ExpiredSignatureError as e:
            raise ExpireJwtToken(ex=e)
        return await call_next(request)
    except Exception as e:
        error = await exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, code=error.code, list=[])
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await logger.process(request=request, error=error)
        return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def exception_handler(error: Exception):
    print(error)
    if isinstance(error, sqlalchemy.exc.OperationalError):
        error = InternalSqlEx(ex=error)
    if not isinstance(error, APIException):
        error = APIException(ex=error)
    return error
