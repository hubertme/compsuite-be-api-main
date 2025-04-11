from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class SessionBase(BaseModel):
    company_uuid: UUID 
    openai_thread_id: str


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    id: int

    class Config:
        from_attributes = True
