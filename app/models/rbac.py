from sqlmodel import Field, Relationship, SQLModel, Column, DateTime
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

__all__ = ("Role", "Permission", "RolePermission", "UserRole")


class Role(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)
    description: Optional[str] = Field(default="", max_length=500)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    
    role_permissions: List["RolePermission"] = Relationship(back_populates="role")
    user_roles: List["UserRole"] = Relationship(back_populates="role")


class Permission(SQLModel, table=True):  
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=100)
    resource: str = Field(index=True, max_length=50)
    action: str = Field(index=True, max_length=50)
    description: Optional[str] = Field(default="", max_length=500)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    
    role_permissions: List["RolePermission"] = Relationship(back_populates="permission")


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permission"
    
    role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permission.id", primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    
    role: Role = Relationship(back_populates="role_permissions")
    permission: Permission = Relationship(back_populates="role_permissions")


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    assigned_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    assigned_by: Optional[UUID] = Field(default=None)
    
    user: "User" = Relationship(back_populates="user_roles")
    role: Role = Relationship(back_populates="user_roles")