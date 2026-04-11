from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt import decode_token
from .blacklist import is_token_blacklisted
from ..models import User
from ..database import get_session
from ..crud.user import get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_active_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    if await is_token_blacklisted(payload.get("jti"), db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = await get_user_by_id(user_id, db)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive or not found"
        )
    
    return user