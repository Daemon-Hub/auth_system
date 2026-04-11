from sqlmodel import SQLModel
from uuid import UUID

class RegisterRequest(SQLModel):
    first_name: str
    last_name: str
    patronymic: str
    email: str
    password: str
    password_confirm: str
    
class RegisterResponse(SQLModel):
    id: UUID
    first_name: str
    last_name: str
    patronymic: str
    email: str