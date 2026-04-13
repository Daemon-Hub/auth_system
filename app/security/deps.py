from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .jwt import decode_token
from .blacklist import is_token_blacklisted
from ..models import User
from ..database import get_session
from ..crud.user import get_user_by_id
from ..services.rbac import RBACService 



__all__ = ("oauth2_scheme", "get_current_active_user")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login", auto_error=False
)


async def check_user(token: str, db: AsyncSession) -> User: 
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


async def get_current_active_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
) -> User:
        return await check_user(token, db)


async def get_optional_user(
    token: Optional[str] = Depends(optional_oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
) -> Optional[User]:
    if not token:
        return None
    return await check_user(token, db)


def require_permission(resource: str, action: str):
    async def permission_checker(
        current_user: Optional[User] = Depends(get_optional_user),
        db: AsyncSession = Depends(get_session)
    ) -> Optional[User]:
        user_id = current_user.id if current_user else None
        
        has_permission = await RBACService.check_user_permission(
            db=db,
            user_id=user_id,
            resource=resource,
            action=action
        )

        if not has_permission:
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: '{resource}.{action}'"
                )
        
        return current_user
    
    return permission_checker