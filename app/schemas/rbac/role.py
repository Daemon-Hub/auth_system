from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel


class RoleBase(SQLModel):
    name: str = Field(max_length=50)
    description: Optional[str] = Field(default="", max_length=500)
    
class RoleCreate(RoleBase):
    pass

class RoleUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    
class RoleRead(RoleBase):
    id: UUID
    created_at: datetime
    permissions_count: int = 0

