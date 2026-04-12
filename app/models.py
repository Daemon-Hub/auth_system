from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from datetime import datetime, timezone
from uuid import UUID, uuid7
from typing import List, Optional


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True) 
    first_name: str
    last_name: str
    patronymic: str
    email: str = Field(index=True, unique=True)
    password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    refresh_token: Optional["RefreshToken"] = Relationship(back_populates="user")
    
    
class RefreshToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, unique=True)
    refresh_token: str = Field(unique=True, index=True)
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    
    user: Optional[User] = Relationship(back_populates="refresh_token")


class BlacklistedToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True)
    jti: str = Field(unique=True, index=True)
    user_id: UUID = Field(foreign_key="user.id")
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
