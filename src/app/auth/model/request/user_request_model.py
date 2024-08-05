# coding=utf-8
from pydantic import BaseModel, EmailStr, Field, constr


class RequestRegisterModel(BaseModel):
    login_id: str = Field(..., example="user123", description="로그인 아이디")
    user_name: str = Field(..., example="Cho Jung Ho", description="유저이름")
    password: constr(min_length=8) = Field(example="password123", description="패스워드")
    email: EmailStr = Field(..., example="user@example.com", description="유효한 이메일 주소")
    user_type: int = Field(..., le=2, example=1, description="유저 타입 (예: 1 = 관리자, 2 = 일반사용자)")

    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "user123",
                "user_name": "Cho Jung Ho",
                "password": "password123",
                "email": "user@example.com",
                "user_type": 1,
            }
        }
