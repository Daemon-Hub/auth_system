from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel


class PermissionBase(SQLModel):
    name: str = Field(max_length=100)
    resource: str = Field(max_length=50)
    action: str = Field(max_length=50)
    description: Optional[str] = Field(default="", max_length=500)
    
class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: UUID
    created_at: datetime
    
    