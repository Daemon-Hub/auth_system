from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    first_name: str
    last_name: str
    patronymic: str
    email: Field(index=True, unique=True) # pyright: ignore[reportInvalidTypeForm]
    password: str
    
