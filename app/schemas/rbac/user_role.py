from typing import List
from uuid import UUID
from sqlmodel import SQLModel

from .role import RoleRead

class UserRoleAssign(SQLModel):
    role_ids: List[UUID]  
    
class UserRolesRead(SQLModel):
    user_id: UUID
    roles: List[RoleRead]