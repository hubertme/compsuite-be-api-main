from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config.app_config import settings
from app.utils.db_util import get_db
import redis.asyncio as redis

router = APIRouter()

async def check_db_connection(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print("DB connection error:", e)
        return False

async def check_redis_connection() -> bool:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        return True
    except Exception:
        return False

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict:
    """
    Health check endpoint that verifies:
    - API is responsive
    - Database connection is working
    - Redis connection is working
    - Current environment and version
    """
    db_status = await check_db_connection(db)
    redis_status = await check_redis_connection()
    
    return {
        "status": "healthy" if db_status and redis_status else "unhealthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_status else "disconnected",
        "redis": "connected" if redis_status else "disconnected",
    }
