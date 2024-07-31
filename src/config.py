# coding=utf-8
from os import environ
from typing import Any, List
from urllib.parse import quote

from pydantic import AnyHttpUrl, FieldValidationInfo, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    JWT_ALGORITHM: str = ""
    JWT_ACCESS_SECRET_KEY: str = ""
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_SECRET_KEY: str = ""
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 3000
    TEST: bool = False
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    DEBUG: bool = False
    SQL_PRINT: bool = False

    @classmethod
    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Fastapi-Boilerplate-Project"
    VERSION: str = "1.0.0"

    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_SCHEMA: str = ""

    REDIS_SERVER: str = "localhost"
    REDIS_PASSWORD: str = ""
    REDIS_PORT: int = 6379
    REDIS_EXPIRE_TIME: int = 86400

    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    SQLALCHEMY_TEST_DATABASE_URI: PostgresDsn | None = None

    # noinspection PyMethodParameters
    @field_validator("SQLALCHEMY_DATABASE_URI")
    def assemble_db_connection(cls, v: str | None, values: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=quote(values.data.get("POSTGRES_PASSWORD")),
            host=values.data.get("POSTGRES_SERVER"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


class LocalConfig(Config):
    DEBUG: bool = True
    SQL_PRINT: bool = True

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_SCHEMA: str = "public"

    REDIS_SERVER: str = "localhost"


class TestConfig(Config):
    TEST: bool = True

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_SCHEMA: str = "test"

    REDIS_SERVER: str = "localhost"


class ProdConfig(Config):
    pass


def conf():
    c = dict(prod=ProdConfig, test=TestConfig, local=LocalConfig)
    return c[environ.get("API_ENV", "prod")]()
