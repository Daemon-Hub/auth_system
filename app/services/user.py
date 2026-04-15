from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from ..models import User
from .rbac import RBACService

class UserService:
    @staticmethod
    async def create_user(user: User, db: AsyncSession) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def create_user_with_roles(
        user: User, 
        db: AsyncSession,
        role_names: List[str] = ["user"],
    ) -> User:
        new_user = await UserService.create_user(user, db)
        await RBACService.add_roles_to_user(
            db, user.id,
            [(await RBACService.get_role_by_name(db, role)).id
             for role in role_names]
        )
        return new_user
    
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
