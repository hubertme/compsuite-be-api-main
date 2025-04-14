from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.routes import v1_api_router
from app.api.middlewares.middleware import setup_middleware, setup_rate_limiter
from app.api.middlewares.api_key import CompanyContextMiddleware
from app.api.errors.http_error import add_exception_handlers
from app.config.app_config import settings, routes_name
from app.core.monitoring import init_monitoring, track_request_metrics
from app.utils.log_util import setup_logging
from app.utils.openai_util import OpenAIUtil

# Setup structured logging
def setup_services() -> None:
    setup_logging()
    OpenAIUtil.init()

def setup_routes(app: FastAPI) -> None:
    app.include_router(v1_api_router, prefix=routes_name.API_V1)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A production-ready FastAPI boilerplate with best practices",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        debug=settings.DEBUG,
    )

    # Add middlewares
    setup_middleware(app)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(CompanyContextMiddleware)

    # Add exception handlers
    add_exception_handlers(app)
    setup_services()

    # Setup API routes
    setup_routes(app)

    # Setup monitoring with custom metrics
    init_monitoring(app)
    app.middleware("http")(track_request_metrics())

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()

# @app.on_event("startup")
# async def startup_event():
#     await setup_rate_limiter(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1,
    )
