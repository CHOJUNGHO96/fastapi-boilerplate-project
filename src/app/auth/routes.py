# coding=utf-8
from fastapi import APIRouter

import app.auth.endpoint.login as login
import app.auth.endpoint.logout as logout
import app.auth.endpoint.refresh_token as refresh_token

auth_api_router = APIRouter()
auth_api_router.include_router(login.router, tags=["Authentication"])
auth_api_router.include_router(logout.router, tags=["Authentication"])
auth_api_router.include_router(refresh_token.router, tags=["Authentication"])
