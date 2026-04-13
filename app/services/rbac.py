from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlmodel import select

from ..schemas.rbac.permission import PermissionCreate
from ..schemas.rbac.role import RoleCreate
from ..models.rbac import Permission, Role


class RBACService:
    @staticmethod
    async def create_role(db: AsyncSession, role_data: RoleCreate) -> Role:
        role = Role(**role_data.model_dump())
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role
        
    @staticmethod
    async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
        role = await db.execute(
            select(Role).where(Role.name == name)
        )
        return role.scalar_one_or_none()

    # ==================== Permission методы ====================
    
    @staticmethod
    async def create_permission(db: AsyncSession, perm_data: PermissionCreate) -> Permission:
        permission = Permission(**perm_data.model_dump())
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission
    

    @staticmethod
    async def get_permission_by_name(db: AsyncSession, name: str) -> Permission | None:
        permission = await db.execute(
            select(Permission).where(Permission.name == name)
        )
        return permission.scalar_one_or_none()
   