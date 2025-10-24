"""
Enhanced UX & Community Management Endpoints for Phase 4, Items 3 & 4
Following EXACT same patterns as advanced_safety_systems.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.schemas.enhanced_ux_community import (
    UserUIPreferencesResponse, UserUIPreferencesUpdate,
    OfflineContentResponse, OfflineContentCreate,
    DataExportJobResponse, DataExportJobCreate,
    CommunityAnalyticsResponse,
    UserReputationResponse,
    ConflictResolutionCaseResponse, ConflictResolutionCaseCreate,
    CommunityEventResponse,
    TrainingModuleResponse, TrainingProgressResponse, TrainingProgressUpdate,
    HealthResponse
)
from app.crud.enhanced_ux_community import enhanced_ux_community_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

# ===== USER UI PREFERENCES ENDPOINTS (Item 3) =====

@router.get("/ui-preferences", response_model=UserUIPreferencesResponse)
async def get_my_ui_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's UI preferences
    SECURITY: Users can only see their own preferences
    """
    try:
        preferences = await enhanced_ux_community_crud.get_user_ui_preferences(
            current_user.id, current_user.id
        )

        if not preferences:
            # Return default preferences if none set
            return {
                "user_id": current_user.id,
                "theme_preference": "system",
                "font_size": "medium",
                "high_contrast_mode": False,
                "reduced_motion": False,
                "screen_reader_optimized": False,
                "keyboard_navigation": True,
                "focus_indicators": True,
                "content_density": "comfortable",
                "image_descriptions": True,
                "auto_play_media": False,
                "language_preference": "en",
                "timezone": "UTC",
                "date_format": "YYYY-MM-DD",
                "email_notifications": True,
                "push_notifications": True,
                "show_online_status": True
            }

        return preferences

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch UI preferences"
        )

@router.put("/ui-preferences", response_model=UserUIPreferencesResponse)
async def update_my_ui_preferences(
    preferences_data: UserUIPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's UI preferences
    SECURITY: Users can only update their own preferences
    """
    try:
        preferences = await enhanced_ux_community_crud.update_user_ui_preferences(
            current_user.id, preferences_data.dict(exclude_unset=True)
        )

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update UI preferences"
            )

        return preferences

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update UI preferences"
        )

# ===== OFFLINE CONTENT ENDPOINTS (Item 3) =====

@router.get("/offline-content", response_model=List[OfflineContentResponse])
async def get_my_offline_content(
    content_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's offline content
    SECURITY: Users can only see their own offline content
    """
    try:
        content = await enhanced_ux_community_crud.get_offline_content(
            current_user.id, current_user.id, content_type, limit, offset
        )

        return content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch offline content"
        )

@router.post("/offline-content", response_model=OfflineContentResponse)
async def save_offline_content(
    content_data: OfflineContentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Save content for offline access
    SECURITY: Users can only save their own offline content
    """
    try:
        content = await enhanced_ux_community_crud.save_offline_content(
            current_user.id, content_data.dict()
        )

        if not content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save offline content"
            )

        return content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save offline content"
        )

@router.delete("/offline-content/{content_id}")
async def delete_offline_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Delete offline content
    SECURITY: Users can only delete their own offline content
    """
    try:
        success = await enhanced_ux_community_crud.delete_offline_content(
            content_id, current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offline content not found or access denied"
            )

        return {"message": "Offline content deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete offline content"
        )

# ===== DATA EXPORT ENDPOINTS (Item 3) =====

@router.post("/data-export", response_model=DataExportJobResponse)
async def create_data_export(
    export_data: DataExportJobCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create data export job
    SECURITY: Users can only create their own export jobs
    """
    try:
        job = await enhanced_ux_community_crud.create_data_export_job(
            current_user.id, export_data.dict()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create data export job"
            )

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create data export job"
        )

@router.get("/data-export/jobs", response_model=List[DataExportJobResponse])
async def get_my_export_jobs(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's data export jobs
    SECURITY: Users can only see their own export jobs
    """
    try:
        jobs = await enhanced_ux_community_crud.get_user_export_jobs(
            current_user.id, current_user.id, status, limit, offset
        )

        return jobs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch export jobs"
        )

# ===== COMMUNITY ANALYTICS ENDPOINTS (Item 4) =====

@router.get("/community-analytics", response_model=List[CommunityAnalyticsResponse])
async def get_community_analytics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get community analytics
    SECURITY: Only moderators/admins can access analytics
    """
    try:
        # Check if user has moderator/admin role
        if current_user.role not in ['moderator', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access community analytics"
            )

        analytics = await enhanced_ux_community_crud.get_community_analytics(
            current_user.id, start_date, end_date, limit, offset
        )

        return analytics

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch community analytics"
        )

# ===== USER REPUTATION ENDPOINTS (Item 4) =====

@router.get("/reputation", response_model=UserReputationResponse)
async def get_my_reputation(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's reputation score
    SECURITY: Users can see their own, moderators can see all
    """
    try:
        reputation = await enhanced_ux_community_crud.get_user_reputation(
            current_user.id, current_user.id
        )

        if not reputation:
            # Return default reputation if none exists
            return {
                "user_id": current_user.id,
                "helpfulness_score": 0,
                "support_score": 0,
                "engagement_score": 0,
                "consistency_score": 0,
                "verified_contributor": False,
                "trusted_member": False,
                "warning_count": 0,
                "account_age_days": 0
            }

        return reputation

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reputation data"
        )

# ===== CONFLICT RESOLUTION ENDPOINTS (Item 4) =====

@router.get("/conflict-cases", response_model=List[ConflictResolutionCaseResponse])
async def get_my_conflict_cases(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get conflict resolution cases involving current user
    SECURITY: Users can only see cases they're involved in
    """
    try:
        cases = await enhanced_ux_community_crud.get_user_conflict_cases(
            current_user.id, current_user.id, status, limit, offset
        )

        return cases

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conflict cases"
        )

@router.post("/conflict-cases", response_model=ConflictResolutionCaseResponse)
async def create_conflict_case(
    case_data: ConflictResolutionCaseCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a conflict resolution case
    SECURITY: Users can create cases, moderators have full access
    """
    try:
        case = await enhanced_ux_community_crud.create_conflict_case(
            case_data.dict(), current_user.id
        )

        if not case:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conflict case"
            )

        return case

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conflict case"
        )

# ===== COMMUNITY EVENTS ENDPOINTS (Item 4) =====

@router.get("/community-events", response_model=List[CommunityEventResponse])
async def get_community_events(
    event_type: Optional[str] = None,
    upcoming_only: bool = True,
    limit: int = 20,
    offset: int = 0
):
    """
    Get community events
    SECURITY: Public read access to events (no authentication required)
    """
    try:
        # Use a default user ID for public access (following same pattern as AI personalization)
        events = await enhanced_ux_community_crud.get_community_events(
            UUID("00000000-0000-0000-0000-000000000000"), event_type, upcoming_only, limit, offset
        )

        return events

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch community events"
        )

# ===== MODERATOR TRAINING ENDPOINTS (Item 4) =====

@router.get("/training/modules", response_model=List[TrainingModuleResponse])
async def get_training_modules(
    required_for_role: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Get training modules
    SECURITY: Public read access to active modules (no authentication required)
    """
    try:
        # Use a default user ID for public access (following same pattern as AI personalization)
        modules = await enhanced_ux_community_crud.get_training_modules(
            UUID("00000000-0000-0000-0000-000000000000"), required_for_role, difficulty_level, limit, offset
        )

        return modules

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch training modules"
        )

@router.get("/training/progress", response_model=List[TrainingProgressResponse])
async def get_my_training_progress(
    module_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's training progress
    SECURITY: Users can only see their own progress
    """
    try:
        progress = await enhanced_ux_community_crud.get_user_training_progress(
            current_user.id, current_user.id, module_id, limit, offset
        )

        return progress

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch training progress"
        )

@router.post("/training/modules/{module_id}/progress")
async def update_training_progress(
    module_id: UUID,
    progress_data: TrainingProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update training progress for a module
    SECURITY: Users can only update their own progress
    """
    try:
        progress = await enhanced_ux_community_crud.update_training_progress(
            current_user.id, module_id, progress_data.dict(exclude_unset=True)
        )

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update training progress"
            )

        return {
            "message": "Training progress updated successfully",
            "module_id": str(module_id),
            "status": progress["status"],
            "progress_percent": progress["progress_percent"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update training progress"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health")
async def enhanced_ux_community_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for enhanced UX & community service
    SECURITY: Requires authentication
    """
    try:
        health_ok = await enhanced_ux_community_crud.health_check(current_user.id)

        if health_ok:
            return {"status": "healthy", "service": "enhanced_ux_community"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Enhanced UX & Community service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Enhanced UX & Community health check failed"
        )
