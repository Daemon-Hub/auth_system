from sqlmodel import SQLModel, Field
from uuid import UUID, uuid7

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True) 
    first_name: str
    last_name: str
    patronymic: str
    email: str = Field(index=True, unique=True)
    password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)