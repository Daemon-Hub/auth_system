from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ..models import User
from ..security.deps import require_permission, get_session
from ..services.rbac import RBACService
from ..services.user import UserService

from ..schemas.rbac.permission import PermissionRead
from ..schemas.rbac.role import RoleRead
from ..schemas.rbac.role_permission import RolePermissionAssign, RolePermissionsRead
from ..schemas.rbac.user_role import UserRoleAssign, UserRolesRead

router = APIRouter(prefix="/admin")

ADMIN_CHECK = Depends(require_permission("roles", "manage"))


@router.get("/permissions", response_model=List[PermissionRead])
async def list_all_permissions(
    _: User = ADMIN_CHECK,
    db: AsyncSession = Depends(get_session)
) -> List[PermissionRead]:
    return await RBACService.get_all_permissions(db)


@router.get("/roles", response_model=List[RoleRead])
async def list_all_roles(
    _: User = ADMIN_CHECK,
    db: AsyncSession = Depends(get_session)
) -> List[RoleRead]:
    return await RBACService.get_all_roles(db)


@router.get("/roles/{role_id}/permissions", response_model=RolePermissionsRead)
async def get_role_permissions(
    role_id: UUID,
    _: User = ADMIN_CHECK,
    db: AsyncSession = Depends(get_session)
) -> RolePermissionsRead:
    data = await RBACService.get_role_permissions(db, role_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role not found"
        )
    return data


@router.put("/roles/{role_id}/permissions", response_model=RolePermissionsRead)
async def update_role_permissions(
    role_id: UUID,
    payload: RolePermissionAssign,
    _: User = ADMIN_CHECK,
    db: AsyncSession = Depends(get_session)
) -> RolePermissionsRead:
    if not await RBACService.get_role_by_id(db, role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role not found"
        )
    await RBACService.sync_role_permissions(db, role_id, payload.permission_ids)
    return await RBACService.get_role_permissions(db, role_id)


@router.get("/users/{user_id}/roles", response_model=UserRolesRead)
async def get_user_roles(
    user_id: UUID,
    _: User = ADMIN_CHECK,
    db: AsyncSession = Depends(get_session)
) -> UserRolesRead:
    if not await UserService.get_user_by_id(user_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return await RBACService.get_user_roles(db, user_id)


@router.put("/users/{user_id}/roles", response_model=UserRolesRead)
async def update_user_roles(
    user_id: UUID,
    payload: UserRoleAssign,
    admin: User = ADMIN_CHECK,
    db: AsyncSession = Depends(get_session)
) -> UserRolesRead:
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You cannot modify your own roles"
        )
        
    if not await UserService.get_user_by_id(user_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    await RBACService.sync_user_roles(
        db, 
        user_id, 
        payload.role_ids, 
        assigned_by=admin.id
    )
    
    return await RBACService.get_user_roles(db, user_id)