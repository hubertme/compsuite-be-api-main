from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class CreateCompanyRequest(BaseModel):
    company_name: str
    display_name: Optional[str] = None
    
class CompanyResponse(BaseModel):
    company_uuid: UUID4
    company_name: str
    display_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
