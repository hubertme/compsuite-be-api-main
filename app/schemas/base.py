from pydantic import BaseModel, Field
from typing import Any, Optional
from fastapi import HTTPException, status

# Constants
OK = "OK"
DEV_REPORT_ERROR = "err/dev-report"
BAD_REQUEST_FORMAT = "err/bad-request-format"
AUTH_ERROR = "err/auth-error"
EMPTY_REQUIRED_FIELD_REQUEST = "EMPTY_REQUIRED_FIELD_REQUEST"
GENERAL_ERROR = "GENERAL_ERROR"

class ResponseModel(BaseModel):
    code: str = Field(..., description="Response code")
    message: str = Field("", description="Response message")
    data: Optional[Any] = Field(None, description="Response data")


def resp_success(message: str = "Success", data: Any = None) -> ResponseModel:
    return ResponseModel(code=OK, message=message, data=data)

def resp_error(status_code: int, error_code: str, message: str, data: Any = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ResponseModel(
            code=error_code,
            message=message,
            data=data,
        ).model_dump()
    )

def resp_dev_error() -> HTTPException:
    return HTTPException(
        status_code=500,
        detail=ResponseModel(
            code=DEV_REPORT_ERROR,
            message="Please contact developer to report this error",
            data=None,
        ).model_dump()
    )

def resp_format_error(data: Any = None) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=ResponseModel(
            code=BAD_REQUEST_FORMAT,
            message="Bad request format",
            data=data,
        ).model_dump()
    )

def resp_empty_field_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ResponseModel(
            code=EMPTY_REQUIRED_FIELD_REQUEST,
            message="Empty required field detected, please check your payload",
            data=None,
        ).model_dump()
    )

def resp_general_error(data: Any = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=ResponseModel(
            code=GENERAL_ERROR,
            message="An error occurred",
            data=data,
        ).model_dump()
    )