from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from typing import List, Optional
from app.schemas.user import UserResponse, UserProfileUpdate, HelperApplication, PublicUserProfile
from app.crud.user import user_crud
from app.core.security import verify_token
from app.utils.timezone import timezone_handler

router = APIRouter()
security = HTTPBearer()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(token: str = Depends(security)):
    """
    Get current user's full profile - BLUEPRINT: User profiles
    """
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    user = await user_crud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**dict(user))

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    token: str = Depends(security)
):
    """
    Update current user's profile - BLUEPRINT: User profiles
    """
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    user = await user_crud.update(user_id, profile_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**dict(user))

@router.post("/me/apply-helper", response_model=UserResponse)
async def apply_as_helper(
    application: HelperApplication,
    token: str = Depends(security)
):
    """
    Apply to become a helper - BLUEPRINT: Seeker/Helper modes
    """
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    
    # Update user with helper application
    update_data = {
        "is_helper": True,
        "helper_credentials": application.credentials,
        "helper_specialties": application.specialties,
        "helper_verification_status": "pending",
        "bio": application.bio
    }
    
    user = await user_crud.update(user_id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**dict(user))

@router.get("/{user_id}", response_model=PublicUserProfile)
async def get_public_user_profile(user_id: str):
    """
    Get public user profile - BLUEPRINT: User profiles
    """
    user = await user_crud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return PublicUserProfile(**dict(user))

@router.get("/helpers/list", response_model=List[PublicUserProfile])
async def list_verified_helpers():
    """
    List verified helpers - BLUEPRINT: Helper mode
    """
    async with user_crud.database.pool.acquire() as conn:
        helpers = await conn.fetch("""
            SELECT id, username, full_name, bio, profile_picture, 
                   is_helper, helper_specialties, created_at
            FROM users 
            WHERE is_active = true 
            AND is_helper = true 
            AND helper_verification_status = 'verified'
            ORDER BY created_at DESC
        """)
    
    return [PublicUserProfile(**dict(helper)) for helper in helpers]
