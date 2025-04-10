from fastapi import APIRouter
from app.api.v1.endpoints import deleteme, auth, health

v1_api_router = APIRouter()
v1_api_router.include_router(deleteme.router, prefix="/deleteme", tags=["test"])
v1_api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_api_router.include_router(health.router, prefix="/health", tags=["health"])
