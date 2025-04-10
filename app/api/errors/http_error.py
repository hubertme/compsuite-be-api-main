from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import structlog

from app.core.exceptions import AppException
from app.utils.log_util import get_correlation_id

logger = structlog.get_logger()

def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Any = None,
    correlation_id: str = None,
) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "error": {
            "status_code": status_code,
            "message": message,
            "correlation_id": correlation_id or get_correlation_id(),
        }
    }
    
    if error_code:
        response["error"]["code"] = error_code
    
    if details:
        response["error"]["details"] = details
    
    return response

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors from request data."""
    correlation_id = get_correlation_id()
    logger.error(
        "validation_error",
        correlation_id=correlation_id,
        path=request.url.path,
        errors=exc.errors(),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={
                "errors": exc.errors(),
                "body": exc.body,
            },
            correlation_id=correlation_id,
        ),
    )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    correlation_id = get_correlation_id()
    logger.error(
        "app_error",
        correlation_id=correlation_id,
        path=request.url.path,
        status_code=exc.status_code,
        error_code=exc.error_code,
        detail=exc.detail,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code=exc.error_code,
            correlation_id=correlation_id,
        ),
        headers=exc.headers,
    )

async def python_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    correlation_id = get_correlation_id()
    logger.exception(
        "internal_server_error",
        correlation_id=correlation_id,
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            correlation_id=correlation_id,
        ),
    )

def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, python_exception_handler)
    return None
