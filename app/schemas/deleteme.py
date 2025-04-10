from pydantic import BaseModel
from app.schemas.base import ResponseModel

class SumNumberRequest(BaseModel):
    a: int
    b: int

class SubtractNumberRequest(BaseModel):
    a: int
    b: int

class SubtractNumberResponse(BaseModel):
    result: int
    operation: str

class HashDataRequest(BaseModel):
    plain_text: str
    encoding: str