from typing import Callable
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
import structlog
from app.config.app_config import settings as config, Environment

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = str(uuid.uuid4())
        logger.info(
            "incoming_request",
            correlation_id=correlation_id,
            method=request.method,
            url=str(request.url),
            client=request.client.host if request.client else None,
            headers=dict(request.headers),
            query_params=str(request.query_params),
            path_params=request.path_params,
        )
        
        try:
            response = await call_next(request)
            logger.info(
                "outgoing_response",
                correlation_id=correlation_id,
                status_code=response.status_code,
                method=request.method,
                url=str(request.url),
                headers=dict(response.headers),
            )
            return response
        except Exception as e:
            logger.error(
                "request_failed",
                correlation_id=correlation_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise

def setup_middleware(app: FastAPI) -> None:
    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
    )

    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=config.ALLOWED_HOSTS
    )

    # Session Middleware with enhanced security
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY,
        max_age=config.SESSION_MAX_AGE,
        same_site="lax",  # Prevents CSRF
        https_only=config.ENVIRONMENT == Environment.PROD,
    )

    # Request Logging Middleware
    app.add_middleware(RequestLoggingMiddleware)

async def setup_rate_limiter(app: FastAPI) -> None:
    redis_instance = redis.from_url(
        config.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_instance)

    # Apply rate limiting to all routes by default
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if not request.scope["path"].startswith("/api/"):
            return await call_next(request)
        
        limiter = RateLimiter(times=config.RATE_LIMIT_TIMES, seconds=config.RATE_LIMIT_SECONDS)
        await limiter(request)
        return await call_next(request)
