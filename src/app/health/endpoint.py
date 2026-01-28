# coding=utf-8
from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from redis import asyncio as aioredis
from sqlalchemy import text

from infrastructure.db.sqlalchemy import AsyncEngine

router = APIRouter()


@router.get("/health")
@inject
async def health_check(
    db: AsyncEngine = Depends(Provide["db"]),
    redis: aioredis.Redis = Depends(Provide["redis"]),
):
    """
    Health check endpoint for monitoring and deployment validation.

    Checks:
    - API service status
    - Database connectivity
    - Redis connectivity

    Returns:
        dict: Health status with component checks and timestamp
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
    }

    # Check database connection
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {"status": "unhealthy", "message": f"Database error: {str(e)}"}

    # Check Redis connection
    try:
        await redis.ping()
        health_status["checks"]["redis"] = {"status": "healthy", "message": "Redis connection successful"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = {"status": "unhealthy", "message": f"Redis error: {str(e)}"}

    return health_status
