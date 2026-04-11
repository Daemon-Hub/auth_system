from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.database import get_session
from src.schemas.user import RegisterRequest, RegisterResponse
from src.models import User
from src.auth import hash_password

router = APIRouter(prefix="/users")

@router.post("/register")
async def register(
    request: RegisterRequest, 
    db: AsyncSession = Depends(get_session)
) -> RegisterResponse:
    if request.password != request.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Passwords do not match"
        )
    
    existing_user = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    new_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        patronymic=request.patronymic,
        email=request.email,
        password=hash_password(request.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return RegisterResponse(
        id=new_user.id,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        patronymic=new_user.patronymic,
        email=new_user.email
    )

