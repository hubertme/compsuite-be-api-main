from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class SessionBase(BaseModel):
    company_uuid: UUID 
    openai_thread_id: str


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    id: str

    class Config:
        from_attributes = True


class SendNewMessageRequest(BaseModel):
    message: str
