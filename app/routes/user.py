from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..database import get_session
from ..schemas.user import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse, 
    UpdateUserRequest, UpdateUserResponse
)
from ..models import User
from ..auth.jwt import create_access_token
from ..auth.password import hash_password, verify_password
from ..auth.dependencies import get_current_active_user
from ..crud.user import get_user_by_email

router = APIRouter(prefix="/users")


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest, 
    db: AsyncSession = Depends(get_session)
) -> RegisterResponse:
    if request.password != request.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Passwords do not match"
        )
    
    existing_user = await get_user_by_email(request.email, db)
    if existing_user:
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


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_session)
) -> LoginResponse:
    user = await get_user_by_email(request.email, db)
    
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
    )


@router.patch("/me")
async def update_user(
    request: UpdateUserRequest, 
    current_user: User | None = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    
    update_data = request.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    
    return update_data

