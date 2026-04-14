from datetime import datetime, timedelta, timezone
from sqlmodel import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RefreshToken
from ..settings import settings


class RefreshTokenService:   
    @staticmethod
    async def add_refresh_token(
        token: str,
        user_id: str,
        db: AsyncSession
    ) -> None:
        db.add(RefreshToken(
            user_id=user_id,
            refresh_token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        ))
        await db.commit()

    @staticmethod
    async def get_refresh_token(
        token: str,
        db: AsyncSession
    ) -> RefreshToken:
        result = await db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.refresh_token == token,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_refresh_token(
        user_id: str, 
        db: AsyncSession
    ) -> None:
        await db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        await db.commit()