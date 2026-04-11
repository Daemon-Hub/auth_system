from sqlmodel import SQLModel
from pydantic import EmailStr
from uuid import UUID
from typing import Optional

class RegisterRequest(SQLModel):
    first_name: str
    last_name: str
    patronymic: str
    email: EmailStr
    password: str
    password_confirm: str
    
class RegisterResponse(SQLModel):
    id: UUID
    first_name: str
    last_name: str
    patronymic: str
    email: str
    
class LoginRequest(SQLModel):
    email: EmailStr
    password: str
    
class LoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    
class UpdateUserRequest(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePasswordRequest(SQLModel):
    current_password: str
    new_password: str
    new_password_confirm: str