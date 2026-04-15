from fastapi import Depends, HTTPException, status, APIRouter, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import settings
from ..database import get_session
from ..schemas.user import (
    RegisterRequest, RegisterResponse,
    LoginRequest, AccessTokenResponse, 
    UpdateUserRequest, ChangePasswordRequest
)
from ..services import UserService, RefreshTokenService
from ..models import User
from ..security import (
    create_access_token, 
    generate_refresh_token,
    blacklist_token,
    hash_password, 
    verify_password,
    get_current_active_user, 
    oauth2_scheme
)


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
    
    existing_user = await UserService.get_user_by_email(request.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    new_user = await UserService.create_user_with_roles(
        User(
            first_name=request.first_name,
            last_name=request.last_name,
            patronymic=request.patronymic,
            email=request.email,
            password=hash_password(request.password)
        ), 
        db
    )
    
    return RegisterResponse.model_validate(new_user) 


@router.post("/login", response_model=AccessTokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_session),
    response: Response = None,
) -> AccessTokenResponse:
    user = await UserService.get_user_by_email(request.email, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user with this email address was not found"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(str(user.id))
    plain_refresh = generate_refresh_token()
    
    await RefreshTokenService.delete_refresh_token(user_id=user.id, db=db)
    await RefreshTokenService.add_refresh_token(
        token=plain_refresh, 
        user_id=user.id, 
        db=db
    )
    
    response.set_cookie(
        key="refresh_token",
        value=plain_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/"
    )
    
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=200)
async def logout(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
    response: Response = None
):
    await RefreshTokenService.delete_refresh_token(user_id=current_user.id, db=db)
    await blacklist_token(
        token=token, 
        user_id=current_user.id, 
        db=db
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return { "detail": "Successfully logged out" }


@router.patch("/me")
async def update_user(
    request: UpdateUserRequest, 
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
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


@router.patch("/me/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    if not verify_password(request.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
        
    if request.new_password == request.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current password"
        )
    
    if request.new_password != request.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    current_user.password = hash_password(request.new_password)
    
    db.add(current_user)
    await db.commit()
    
    return {"detail": "Password updated successfully"}


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
):
    await logout(current_user=current_user, token=token, db=db)

    current_user.is_active = False
    db.add(current_user)
    await db.commit()
    
    return {"detail": "Account deleted successfully"}


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
    refresh_token: str = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(get_session),
    response: Response = None
) -> AccessTokenResponse:
    if not refresh_token:
        raise HTTPException(
            status_code=401, 
            detail="Refresh token missing"
        )

    token_record = await RefreshTokenService.get_refresh_token(
        token=refresh_token, db=db
    )
    if not token_record:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired refresh token"
        )

    access_token = create_access_token(str(token_record.user_id))
    plain_refresh = generate_refresh_token()
    
    await RefreshTokenService.delete_refresh_token(
        user_id=token_record.user_id, db=db
    )
    await RefreshTokenService.add_refresh_token(
        token=plain_refresh, 
        user_id=token_record.user_id, 
        db=db
    )
    
    response.set_cookie(
        key="refresh_token",
        value=plain_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/"
    )

    return AccessTokenResponse(access_token=access_token)
