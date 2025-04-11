from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.base import resp_success, resp_format_error, resp_general_error, ResponseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_util import get_db

from app.services.company import CompanyService
from app.schemas.company import CreateCompanyRequest, CompanyResponse

router = APIRouter()

@router.post("/", response_model=ResponseModel)
async def create_company(req: CreateCompanyRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await CompanyService.create_company(db, req)
        # The create_company method already returns a dictionary with the API key
        # so we don't need to convert it to a Pydantic model
        return resp_success(
            message="Company created successfully", 
            data=result,
        )
    except ValueError as e:
        raise resp_format_error(str(e))
    except Exception as e:
        raise resp_general_error(e)
    
@router.get("/info", response_model=ResponseModel)
async def get_current_company_info(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        company_uuid = getattr(request.state, "company_uuid", None)
        company = await CompanyService.get_company_by_uuid(db, company_uuid)
        company_response = CompanyResponse.model_validate(company)
        return resp_success(data=company_response)
    except ValueError as e:
        raise resp_format_error(str(e))
    except Exception as e:
        raise resp_general_error(e)
