from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone
from sqlmodel import select
from uuid import UUID

from .jwt import decode_token
from ..models import BlacklistedToken

__all__ = ("blacklist_token", "is_token_blacklisted")

async def blacklist_token(token: str, user_id: UUID, db: AsyncSession):
    payload = decode_token(token)
    
    jti = payload.get("jti")
    exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
    
    token = BlacklistedToken(
        jti=jti,
        user_id=user_id,
        expires_at=exp
    )
    
    db.add(token)
    await db.commit()


async def is_token_blacklisted(jti: str, db: AsyncSession) -> bool:
    result = await db.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    return result.first() is not None