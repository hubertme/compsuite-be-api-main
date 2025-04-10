from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_config import settings, routes_name
from app.core.security import decode_token
from app.utils.db_util import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{routes_name.API_V1}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[dict]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Note: User model and repository will be implemented in next step
    # This is just the dependency setup
    return payload

async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
