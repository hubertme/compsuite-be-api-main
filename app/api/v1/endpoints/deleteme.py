from fastapi import APIRouter, HTTPException
from app.schemas.deleteme import SumNumberRequest, SubtractNumberRequest, SubtractNumberResponse, ResponseModel, HashDataRequest
from app.schemas.base import resp_success, resp_format_error
from app.services.deleteme import ServiceDeleteme

router = APIRouter()

@router.post("/sum", response_model=ResponseModel)
async def sum_two_numbers(op: SumNumberRequest):
    result = ServiceDeleteme.sum_two_numbers(op.a, op.b)
    return resp_success(data=result)

@router.post("/subtract", response_model=ResponseModel)
async def subtract_two_numbers(op: SubtractNumberRequest):
    result = ServiceDeleteme.subtract_two_numbers(op.a, op.b)
    return resp_success(data=SubtractNumberResponse(result=result, operation="subtraction"))

@router.post("/hash", response_model=ResponseModel)
async def hash_data(data: HashDataRequest):
    if str.lower(data.encoding) == "hex":
        result = ServiceDeleteme.hash_data_hex(data.plain_text)
    elif str.lower(data.encoding) == "base64":
        result = ServiceDeleteme.hash_data_base64(data.plain_text)
    else:
        raise resp_format_error("Encoding must be hex or base64")

    return resp_success(data=result)