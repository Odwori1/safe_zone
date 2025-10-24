"""
Professional Directory Endpoints for Phase 3, Item 7
Following EXACT same patterns as enhanced_moderation.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from app.schemas.professional_directory import (
    ProfessionalProfileCreate, ProfessionalProfileResponse, ProfessionalProfileUpdate,
    ProfessionalVerificationCreate, ProfessionalVerificationResponse,
    AvailabilitySlotCreate, AvailabilitySlotResponse,
    ProfessionalDirectoryResponse, ProfessionalSearchFilters
)
from app.crud.professional_directory import professional_directory_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

# ===== PROFESSIONAL PROFILE ENDPOINTS =====

@router.post("/profiles", response_model=ProfessionalProfileResponse)
async def create_professional_profile(
    profile_data: ProfessionalProfileCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create or update professional profile
    SECURITY: RLS ensures users can only create/update their own profile
    """
    try:
        profile = await professional_directory_crud.create_professional_profile(
            current_user.id, profile_data.dict()
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create professional profile"
            )

        return profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create professional profile"
        )

@router.get("/profiles/me", response_model=ProfessionalProfileResponse)
async def get_my_professional_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's professional profile
    SECURITY: RLS ensures users can only access their own profile
    """
    try:
        profile = await professional_directory_crud.get_professional_profile(
            current_user.id, current_user.id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )

        return profile

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch professional profile"
        )

@router.put("/profiles/me", response_model=ProfessionalProfileResponse)
async def update_professional_profile(
    profile_data: ProfessionalProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update professional profile
    SECURITY: RLS ensures users can only update their own profile
    """
    try:
        profile = await professional_directory_crud.update_professional_profile(
            current_user.id, profile_data.dict(exclude_unset=True)
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )

        return profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update professional profile"
        )

@router.get("/profiles/{user_id}", response_model=ProfessionalProfileResponse)
async def get_professional_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get professional profile by user ID
    SECURITY: RLS ensures users can only access public verified profiles or their own
    """
    try:
        profile = await professional_directory_crud.get_professional_profile(
            user_id, current_user.id
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )

        return profile

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch professional profile"
        )

# ===== PROFESSIONAL DIRECTORY ENDPOINTS =====

@router.get("/directory", response_model=List[ProfessionalDirectoryResponse])
async def get_professional_directory(
    specialties: Optional[List[str]] = None,
    session_types: Optional[List[str]] = None,
    min_rating: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get professional directory listings
    SECURITY: RLS ensures users can only see verified professionals
    """
    try:
        professionals = await professional_directory_crud.get_professional_directory(
            current_user.id, specialties, session_types, min_rating, limit, offset
        )

        return professionals

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch professional directory"
        )

@router.post("/directory/search", response_model=List[ProfessionalDirectoryResponse])
async def search_professionals(
    search_filters: ProfessionalSearchFilters,
    current_user: User = Depends(get_current_user)
):
    """
    Search professionals with advanced filters
    SECURITY: RLS ensures users can only see verified professionals
    """
    try:
        professionals = await professional_directory_crud.get_professional_directory(
            current_user.id,
            search_filters.specialties,
            search_filters.session_types,
            search_filters.min_rating,
            search_filters.limit,
            search_filters.offset
        )

        return professionals

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search professionals"
        )

# ===== PROFESSIONAL VERIFICATION ENDPOINTS =====

@router.post("/verifications", response_model=ProfessionalVerificationResponse)
async def create_professional_verification(
    verification_data: ProfessionalVerificationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Upload professional verification document
    SECURITY: RLS ensures users can only upload their own verifications
    """
    try:
        verification = await professional_directory_crud.create_professional_verification(
            current_user.id, verification_data.dict()
        )

        if not verification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )

        return verification

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload verification document"
        )

@router.get("/verifications/me", response_model=List[ProfessionalVerificationResponse])
async def get_my_verifications(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's verification documents
    SECURITY: RLS ensures users can only see their own verifications
    """
    try:
        verifications = await professional_directory_crud.get_professional_verifications(
            current_user.id, current_user.id
        )

        return verifications

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch verification documents"
        )

# ===== AVAILABILITY ENDPOINTS =====

@router.post("/availability", response_model=AvailabilitySlotResponse)
async def create_availability_slot(
    availability_data: AvailabilitySlotCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create availability slot
    SECURITY: RLS ensures professionals can only manage their own availability
    """
    try:
        availability = await professional_directory_crud.create_availability_slot(
            current_user.id, availability_data.dict()
        )

        if not availability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professional profile not found"
            )

        return availability

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create availability slot"
        )

@router.get("/availability/{professional_id}", response_model=List[AvailabilitySlotResponse])
async def get_professional_availability(
    professional_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get professional availability
    SECURITY: RLS ensures users can only see availability of verified professionals
    """
    try:
        availability = await professional_directory_crud.get_professional_availability(
            professional_id, current_user.id
        )

        return availability

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch professional availability"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health")
async def professional_directory_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for professional directory
    SECURITY: Requires authentication
    """
    try:
        health_ok = await professional_directory_crud.health_check(current_user.id)
        
        if health_ok:
            return {"status": "healthy", "service": "professional_directory"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Professional directory service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Professional directory health check failed"
        )
