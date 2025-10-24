"""
Phase 6 Missing Features Endpoints
Following EXACT same patterns as final_phase_features.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.schemas.phase6_missing_features import (
    TelehealthSessionResponse, TelehealthSessionCreate,
    EMRConnectionResponse, EMRConnectionCreate,
    CommunityMilestoneResponse,
    SuccessStoryResponse, SuccessStoryCreate,
    UserSessionResponse, UserSessionCreate,
    DeviceSyncResponse, DeviceSyncCreate,
    TutorialProgressResponse, TutorialProgressCreate,
    ContentSummaryResponse, ContentSummaryUpdate,
    Phase6HealthResponse
)
from app.crud.phase6_missing_features import phase6_missing_features_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

# ===== TELEHEALTH SESSIONS ENDPOINTS =====

@router.post("/telehealth/sessions", response_model=TelehealthSessionResponse)
async def create_telehealth_session(
    session_data: TelehealthSessionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new telehealth session
    SECURITY: Users can only create their own sessions
    """
    try:
        session = await phase6_missing_features_crud.create_telehealth_session(
            current_user.id, session_data.dict()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create telehealth session"
            )

        return session

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create telehealth session"
        )

@router.get("/telehealth/sessions", response_model=List[TelehealthSessionResponse])
async def get_my_telehealth_sessions(
    status: Optional[str] = None,
    upcoming_only: bool = True,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's telehealth sessions
    SECURITY: Users can only see their own sessions
    """
    try:
        sessions = await phase6_missing_features_crud.get_user_telehealth_sessions(
            current_user.id, current_user.id, status, upcoming_only, limit, offset
        )

        return sessions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch telehealth sessions"
        )

# ===== EMR CONNECTIONS ENDPOINTS =====

@router.post("/emr/connections", response_model=EMRConnectionResponse)
async def create_emr_connection(
    connection_data: EMRConnectionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new EMR connection
    SECURITY: Users can only create their own connections
    """
    try:
        connection = await phase6_missing_features_crud.create_emr_connection(
            current_user.id, connection_data.dict()
        )

        if not connection:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create EMR connection"
            )

        return connection

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create EMR connection"
        )

@router.get("/emr/connections", response_model=List[EMRConnectionResponse])
async def get_my_emr_connections(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's EMR connections
    SECURITY: Users can only see their own connections
    """
    try:
        connections = await phase6_missing_features_crud.get_user_emr_connections(
            current_user.id, current_user.id
        )

        return connections

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch EMR connections"
        )

# ===== COMMUNITY MILESTONES ENDPOINTS =====

@router.get("/community/milestones", response_model=List[CommunityMilestoneResponse])
async def get_community_milestones(
    milestone_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Get community milestones
    SECURITY: Public read access
    """
    try:
        milestones = await phase6_missing_features_crud.get_community_milestones(
            milestone_type, limit, offset
        )

        return milestones

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch community milestones"
        )

# ===== SUCCESS STORIES ENDPOINTS =====

@router.post("/success-stories", response_model=SuccessStoryResponse)
async def create_success_story(
    story_data: SuccessStoryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a success story
    SECURITY: Users can only create their own stories
    """
    try:
        # Set consent given at timestamp if consent is given
        if story_data.consent_given and not story_data.consent_given_at:
            story_data_dict = story_data.dict()
            story_data_dict["consent_given_at"] = datetime.utcnow()
        else:
            story_data_dict = story_data.dict()

        story = await phase6_missing_features_crud.create_success_story(
            current_user.id, story_data_dict
        )

        if not story:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create success story"
            )

        return story

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create success story"
        )

@router.get("/success-stories/featured", response_model=List[SuccessStoryResponse])
async def get_featured_success_stories(
    limit: int = 10,
    offset: int = 0
):
    """
    Get featured success stories
    SECURITY: Public read access to featured stories with consent
    """
    try:
        stories = await phase6_missing_features_crud.get_featured_success_stories(
            limit, offset
        )

        return stories

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch success stories"
        )

# ===== USER SESSIONS ENDPOINTS =====

@router.post("/user-sessions", response_model=UserSessionResponse)
async def create_user_session(
    session_data: UserSessionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a user session for timeout management
    SECURITY: Users can only create their own sessions
    """
    try:
        session = await phase6_missing_features_crud.create_user_session(
            current_user.id, session_data.dict()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user session"
            )

        return session

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user session"
        )

@router.put("/user-sessions/{session_id}/activity")
async def update_session_activity(
    session_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Update user session activity
    SECURITY: Users can only update their own sessions
    """
    try:
        session = await phase6_missing_features_crud.update_user_session_activity(
            session_id, current_user.id
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )

        return {"message": "Session activity updated", "session_id": str(session_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session activity"
        )

# ===== DEVICE SYNC ENDPOINTS =====

@router.post("/devices/register", response_model=DeviceSyncResponse)
async def register_device(
    device_data: DeviceSyncCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Register device for cross-device synchronization
    SECURITY: Users can only register their own devices
    """
    try:
        device = await phase6_missing_features_crud.register_device(
            current_user.id, device_data.dict()
        )

        if not device:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register device"
            )

        return device

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register device"
        )

@router.get("/devices", response_model=List[DeviceSyncResponse])
async def get_my_devices(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's registered devices
    SECURITY: Users can only see their own devices
    """
    try:
        devices = await phase6_missing_features_crud.get_user_devices(
            current_user.id, current_user.id
        )

        return devices

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch devices"
        )

# ===== TUTORIAL PROGRESS ENDPOINTS =====

@router.post("/tutorial/progress", response_model=TutorialProgressResponse)
async def update_tutorial_progress(
    progress_data: TutorialProgressCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Update tutorial progress
    SECURITY: Users can only update their own progress
    """
    try:
        # Set completed_at timestamp if completed
        if progress_data.completed and not progress_data.completed_at:
            progress_data_dict = progress_data.dict()
            progress_data_dict["completed_at"] = datetime.utcnow()
        else:
            progress_data_dict = progress_data.dict()

        progress = await phase6_missing_features_crud.update_tutorial_progress(
            current_user.id, progress_data_dict
        )

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update tutorial progress"
            )

        return progress

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tutorial progress"
        )

@router.get("/tutorial/progress", response_model=List[TutorialProgressResponse])
async def get_my_tutorial_progress(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's tutorial progress
    SECURITY: Users can only see their own progress
    """
    try:
        progress = await phase6_missing_features_crud.get_user_tutorial_progress(
            current_user.id, current_user.id
        )

        return progress

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tutorial progress"
        )

# ===== CONTENT SUMMARIZATION ENDPOINTS =====

@router.put("/ai-content/{analysis_id}/summary", response_model=ContentSummaryResponse)
async def update_content_summary(
    analysis_id: UUID,
    summary_data: ContentSummaryUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update content summary for AI analysis
    SECURITY: Users can only update their own content analysis
    """
    try:
        analysis = await phase6_missing_features_crud.update_content_summary(
            analysis_id, current_user.id, summary_data.dict()
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found or access denied"
            )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content summary"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health", response_model=Phase6HealthResponse)
async def phase6_features_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for phase 6 missing features service
    SECURITY: Requires authentication
    """
    try:
        health_ok = await phase6_missing_features_crud.health_check(current_user.id)

        if health_ok:
            return {
                "status": "healthy", 
                "service": "phase6_missing_features",
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Phase 6 missing features service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Phase 6 missing features health check failed"
        )
