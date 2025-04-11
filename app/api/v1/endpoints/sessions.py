from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db_util import get_db
from app.services.session import SessionService
from app.schemas.base import ResponseModel, GENERAL_ERROR, resp_success
from app.schemas.session import SessionResponse, SendNewMessageRequest

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

@router.delete("/{session_id}", response_model=ResponseModel)
async def close_session(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Close a session.
    """
    try:
        company_uuid = getattr(request.state, "company_uuid", None)
        
        session = await SessionService.close_session(db, company_uuid, session_id)
        return resp_success(data=None)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel(
                code=GENERAL_ERROR,
                data=str(e),
            ).model_dump()
        )
    
@router.get("/{session_id}/messages", response_model=ResponseModel)
async def get_session_messages(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get messages for a session.
    """
    try:
        company_uuid = getattr(request.state, "company_uuid", None)
        
        messages = await SessionService.get_session_messages(db, company_uuid, session_id)
        return resp_success(data=messages)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel(
                code=GENERAL_ERROR,
                data=str(e),
            ).model_dump()
        )
    
@router.post("/{session_id}/messages", response_model=ResponseModel)
async def send_new_message_to_session(
    request: Request,
    session_id: str,
    req: SendNewMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a new message to a session.
    """
    try:
        company_uuid = getattr(request.state, "company_uuid", None)
        
        messages = await SessionService.send_new_message_to_thread(db, company_uuid, session_id, req.message)
        return resp_success(data=messages)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel(
                code=GENERAL_ERROR,
                data=str(e),
            ).model_dump()
)