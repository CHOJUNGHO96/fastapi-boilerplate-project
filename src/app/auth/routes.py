# coding=utf-8
from fastapi import APIRouter

from app.auth.endpoint import login, logout, refresh_token, register

auth_api_router = APIRouter()
auth_api_router.include_router(login.router, tags=["Authentication"])
auth_api_router.include_router(logout.router, tags=["Authentication"])
auth_api_router.include_router(refresh_token.router, tags=["Authentication"])
auth_api_router.include_router(register.router, tags=["Authentication"])
