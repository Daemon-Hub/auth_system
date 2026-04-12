from sqlmodel import SQLModel, Field, Column, DateTime
from datetime import datetime, timezone
from uuid import UUID, uuid7

__all__ = ("BlacklistedToken",)

class BlacklistedToken(SQLModel, table=True):
    __tablename__ = "blacklisted_token"
    
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

