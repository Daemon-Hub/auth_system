from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..database import get_session
from .jwt import verify_token
from ..crud.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_active_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
) -> User | None:
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = await get_user_by_id(user_id, db)
    if not user or not user.is_active:
        return None
    
    return user