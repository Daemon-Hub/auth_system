from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..models import User

class UserService:
    @staticmethod
    async def create_user(user: User, db: AsyncSession) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> User:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(user_id: str, db: AsyncSession) -> User:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
