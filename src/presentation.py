from fastapi import APIRouter

from app.auth.routes import auth_api_router
from app.health.endpoint import router as health_router

router = APIRouter()

router.include_router(auth_api_router, prefix="/auth", tags=["Authentication"])
router.include_router(health_router, tags=["Health"])
