from typing import Callable

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram
import structlog

logger = structlog.get_logger()

# Custom metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

def init_monitoring(app: FastAPI) -> None:
    """Initialize monitoring with custom metrics."""
    
    # Add default metrics
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
    )

    # Add custom metrics
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    
    instrumentator.add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    
    instrumentator.add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    # Instrument application
    instrumentator.instrument(app)

    # Expose metrics
    instrumentator.expose(app, include_in_schema=True, should_gzip=True)

    logger.info(
        "monitoring_initialized",
        metrics_endpoint="/metrics",
        custom_metrics=[
            "http_requests_total",
            "http_request_duration_seconds",
            "request_size",
            "response_size",
            "latency",
        ],
    )

def track_request_metrics() -> Callable:
    """Middleware factory for tracking request metrics."""
    async def middleware(request, call_next):
        try:
            response = await call_next(request)
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
            ).inc()
            return response
        except Exception as e:
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
            ).inc()
            raise
    return middleware
