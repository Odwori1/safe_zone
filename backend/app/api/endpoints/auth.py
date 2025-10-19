from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from typing import Optional
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import Token
from app.crud.user import user_crud
from app.core.security import create_access_token, verify_password, get_password_hash
from app.utils.timezone import timezone_handler
from datetime import timedelta
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, request: Request):
    """
    Register new user - BLUEPRINT: User authentication system
    """
    # Check if user already exists
    existing_user = await user_crud.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await user_crud.get_by_username(user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Auto-detect timezone from request
    detected_timezone = timezone_handler.detect_timezone_from_request(request)
    user_in.timezone = detected_timezone
    
    # Create user
    user = await user_crud.create(user_in)
    return UserResponse(**dict(user))

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, request: Request):
    """
    User login - BLUEPRINT: User authentication system + JWT tokens
    """
    # Authenticate user
    user = await user_crud.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    await user_crud.update_last_login(user['id'])
    
    # Create access token - BLUEPRINT: JWT token management
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user['id']), "email": user['email']},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )

@router.get("/me", response_model=UserResponse)
async def read_users_me(token: str = Depends(security)):
    """
    Get current user - BLUEPRINT: Protected routes
    """
    from app.core.security import verify_token
    
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = await user_crud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**dict(user))
