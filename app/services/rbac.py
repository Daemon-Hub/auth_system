from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlmodel import select, delete
from typing import List
from uuid import UUID

from ..schemas.rbac.permission import PermissionCreate, PermissionRead
from ..schemas.rbac.role import RoleCreate, RoleRead
from ..schemas.rbac.role_permission import RolePermissionsRead
from ..schemas.rbac.user_role import UserRolesRead
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
    
    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: str) -> Role | None:
        role = await db.execute(
            select(Role).where(Role.id == role_id)
        )
        return role.scalar_one_or_none()

    @staticmethod
    async def get_all_roles(db: AsyncSession) -> List[RoleRead]:
        result = await db.execute(select(Role))
        return [RoleRead.model_validate(role) 
                for role in result.scalars().all()]
    
    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: UUID) -> UserRolesRead:
        result = await db.execute(
            select(Role)
            # .options(selectinload(UserRole.role))
            .join(UserRole)
            .where(UserRole.user_id == user_id)
        )
        user_roles = [
            RoleRead.model_validate(role) 
                for role in result.scalars().all()]
        return UserRolesRead(user_id=user_id, roles=user_roles)
    
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
    async def get_all_permissions(db: AsyncSession) -> List[Permission]:
        result = await db.execute(
            select(Permission)
            .order_by(
                Permission.resource, 
                Permission.action
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_role_permissions(db: AsyncSession, role_id: UUID) -> List[PermissionRead]:
        result = await db.execute(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        permissions = [
            PermissionRead.model_validate(perm) 
                for perm in result.scalars().all()]
        return RolePermissionsRead(role_id=role_id, permissions=permissions)  
   
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
        all_roles_ids = [role.id for role in await RBACService.get_all_roles(db)]
        for role_id in role_ids:
            if role_id not in all_roles_ids: 
                continue
            user_role = await db.execute(
                select(UserRole).where(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )   
            )
            if not user_role.first():
                db.add(UserRole(
                    user_id=user_id, 
                    role_id=role_id, 
                    assigned_by=assigned_by
                ))
        
        await db.commit()
    
    @staticmethod
    async def sync_user_roles(
        db: AsyncSession, 
        user_id: UUID, 
        role_ids: List[UUID], 
        assigned_by: Optional[UUID]
    ) -> None:
        await db.execute(
            delete(UserRole).where(UserRole.user_id == user_id)
        )
        await RBACService.add_roles_to_user(db, user_id, role_ids, assigned_by)
        
    # ================ RolePermission методы ================
    
    @staticmethod
    async def sync_role_permissions(
        db: AsyncSession, 
        role_id: UUID, 
        permission_ids: List[UUID]
    ) -> None:
        await db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        for perm_id in permission_ids:
            db.add(RolePermission(role_id=role_id, permission_id=perm_id))
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