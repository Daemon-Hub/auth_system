from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel
from pydantic import ConfigDict


class RoleBase(SQLModel):
    name: str = Field(max_length=50)
    description: Optional[str] = Field(default="", max_length=500)
    
class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
