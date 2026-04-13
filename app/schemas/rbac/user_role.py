from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import SQLModel

from .role import RoleRead

class UserRoleAssign(SQLModel):
    role_ids: List[UUID]
    
class UserRoleRead(SQLModel):
    user_id: UUID
    role_id: UUID
    assigned_at: datetime
    assigned_by: Optional[UUID] = None
    role: RoleRead
    
class UserRolesRead(SQLModel):
    user_id: UUID
    roles: List[RoleRead]