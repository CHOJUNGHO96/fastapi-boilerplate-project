# coding=utf-8
from typing import Annotated

from pydantic import BaseModel, Field


class RequestRegisterModel(BaseModel):
    user_id: Annotated[int, Field(example="유저번호")]
    login_id: Annotated[int, Field(example="로그인 아이디")]
    user_name: Annotated[str, Field(example="이름")]
    email: Annotated[str, Field(example="이메일")]
    user_type: Annotated[str, Field(example="유저타입")]
