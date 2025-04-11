from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_util import get_db
from app.services.session import SessionService
from app.schemas.base import ResponseModel, GENERAL_ERROR, resp_success
from app.schemas.session import SessionResponse

router = APIRouter()

@router.get("/", response_model=ResponseModel)
async def get_sessions(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all sessions.
    """
    try:
        company_uuid = getattr(request.state, "company_uuid", None)
        
        sessions = await SessionService.get_all_sessions(db, company_uuid)
        session_responses = [SessionResponse.model_validate(session) for session in sessions]
        return resp_success(data=session_responses)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel(
                code=GENERAL_ERROR,
                data=str(e),
            ).model_dump()
        )
    
@router.post("/", response_model=ResponseModel)
async def create_session(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new session.
    """
    try:
        company_uuid = getattr(request.state, "company_uuid", None)
        
        session = await SessionService.create_new_session(db, company_uuid)
        return resp_success(data=SessionResponse.model_validate(session))
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel(
                code=GENERAL_ERROR,
                data=str(e),
            ).model_dump()
        )
