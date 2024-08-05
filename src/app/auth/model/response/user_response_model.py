# coding=utf-8
from pydantic import BaseModel, Field


class ResponseLoginModel(BaseModel):
    user_id: int = Field(example="유저번호")
    login_id: int = Field(example="로그인아이디")
    user_name: str = Field(example="유저이름")
    email: str = Field(example="이메일")
    user_type: str = Field(example="유저타입")
    token_type: str = Field(example="토큰타입")
    access_token: str = Field(example="토큰")
    refresh_token: str = Field(example="리프레시토큰")


class ResponseTokenModel(BaseModel):
    token_type: str = Field(example="토큰타입")
    access_token: str = Field(example="토큰")
    refresh_token: str = Field(example="리프레시토큰")
