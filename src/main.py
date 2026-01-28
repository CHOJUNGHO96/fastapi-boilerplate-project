# coding=utf-8

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware

from config import conf
from container import Container
from middleware import dispatch_middlewares
from presentation import router

container = Container()
config = conf()


def create_app() -> FastAPI:
    _app: FastAPI = FastAPI()

    _app.container = container

    _config = container.config()

    _app.title = _config["PROJECT_NAME"]

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=_config["BACKEND_CORS_ORIGINS"] if _config["BACKEND_CORS_ORIGINS"] else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Accept", "Authorization", "Content-Type", "X-Requested-With"],
    )

    _app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=dispatch_middlewares)

    _app.include_router(router, prefix="/api/v1")

    def game_credit_openapi():
        if _app.openapi_schema:
            return _app.openapi_schema
        openapi_schema = get_openapi(
            title="Fastapi-Boilerplate-Project",
            version=_config["VERSION"],
            routes=_app.routes,
        )
        _app.openapi_schema = openapi_schema
        return _app.openapi_schema

    _app.openapi = game_credit_openapi

    return _app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, access_log=False)
