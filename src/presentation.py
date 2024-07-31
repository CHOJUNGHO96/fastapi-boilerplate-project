from fastapi import APIRouter

from app.auth.routes import auth_api_router

router = APIRouter()

router.include_router(auth_api_router, prefix="/auth", tags=["Authentication"])
