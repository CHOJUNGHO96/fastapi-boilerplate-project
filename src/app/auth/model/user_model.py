# coding=utf-8
from typing import Annotated

from pydantic import BaseModel, Field


class ResponseLoginModel(BaseModel):
    user_id: Annotated[int, Field(example="유저번호")]
    login_id: Annotated[int, Field(example="로그인 아이디")]
    user_name: Annotated[str, Field(example="이름")]
    email: Annotated[str, Field(example="이메일")]
    user_type: Annotated[str, Field(example="유저타입")]
    token_type: Annotated[str, Field(example="토큰타입")]
    access_token: Annotated[str, Field(example="토큰")]
    refresh_token: Annotated[str, Field(example="리프레시토큰")]
