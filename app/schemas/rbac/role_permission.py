from typing import List
from uuid import UUID
from sqlmodel import SQLModel

from .permission import PermissionRead

class RolePermissionAssign(SQLModel):
    permission_ids: List[UUID]
    
class RolePermissionsRead(SQLModel):
    role_id: UUID
    permissions: List[PermissionRead]
    