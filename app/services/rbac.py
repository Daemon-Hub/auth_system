from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlmodel import select
from typing import List
from uuid import UUID

from ..schemas.rbac.permission import PermissionCreate
from ..schemas.rbac.role import RoleCreate
from ..models.rbac import Permission, Role, UserRole, RolePermission


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
   
    @staticmethod
    async def get_user_permissions(
        db: AsyncSession, 
        user_id: UUID
    ) -> List[Permission]:
        permissions = await db.execute(
            select(Permission)
            .join(RolePermission)
            .join(Role)
            .join(UserRole)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        return permissions.scalars().all()
    
    @staticmethod
    async def get_user_permission_names(
        db: AsyncSession, 
        user_id: UUID
    ) -> List[str]:
        permissions = await RBACService.get_user_permissions(db, user_id)
        return [perm.name for perm in permissions]
       
    @staticmethod
    async def get_guest_permission_names(db: AsyncSession) -> List[str]:
        permissions = await db.execute(
            select(Permission)
            .join(RolePermission)
            .join(Role)
            .where(Role.name == "guest")
            .distinct()
        )
        return [perm.name for perm in permissions.scalars().all()]
    
    # ==================== UserRole методы ====================
     
    @staticmethod
    async def add_roles_to_user(
        db: AsyncSession,
        user_id: UUID,
        role_ids: List[UUID],
        assigned_by: Optional[UUID] = None
    ) -> None:
        for role_id in role_ids:
            user_role = await db.execute(
                select(UserRole).where(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )   
            )
            if not user_role.first():
                ur = UserRole(
                    user_id=user_id, 
                    role_id=role_id, 
                    assigned_by=assigned_by
                )
                db.add(ur)
        
        await db.commit()
    
    # ==================== Проверка прав ====================
    
    @staticmethod
    async def check_user_permission(
        db: AsyncSession,
        user_id: UUID,
        resource: str,
        action: str
    ) -> bool:
        permission_name = f"{resource}.{action}"
        if user_id is None:
            user_permissions = await RBACService.get_guest_permission_names(db)
        else:
            user_permissions = await RBACService.get_user_permission_names(db, user_id)
        return permission_name in user_permissions