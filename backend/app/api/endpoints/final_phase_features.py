"""
Final Phase Features Endpoints for Phase 5 & 6
Following EXACT same patterns as enhanced_ux_community.py endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.schemas.final_phase_features import (
    LanguagePreferencesResponse, LanguagePreferencesUpdate,
    RegionalResourceResponse,
    AccessibilityPreferencesResponse, AccessibilityPreferencesUpdate,
    OrganizationResponse, OrganizationMemberResponse,
    WellnessChallengeResponse, WellnessChallengeCreate,
    AIChatSessionResponse, AIChatSessionCreate,
    AIChatMessageResponse, AIChatMessageCreate,
    VoiceMoodAnalysisResponse, VoiceMoodAnalysisCreate,
    UserIntegrationResponse, UserIntegrationCreate,
    EmergencyContactResponse, EmergencyContactCreate,
    PeerSupportMatchResponse,
    GroupSessionResponse, GroupSessionCreate,
    UserFeedbackResponse, UserFeedbackCreate,
    HealthResponse
)
from app.crud.final_phase_features import final_phase_features_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

# ===== MULTI-LANGUAGE SUPPORT ENDPOINTS (Phase 5) =====

@router.get("/language-preferences", response_model=LanguagePreferencesResponse)
async def get_my_language_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's language preferences
    SECURITY: Users can only see their own preferences
    """
    try:
        preferences = await final_phase_features_crud.get_language_preferences(
            current_user.id, current_user.id
        )

        if not preferences:
            # Return default preferences if none set
            return {
                "user_id": current_user.id,
                "preferred_language": "en",
                "interface_language": "en",
                "content_language": "en",
                "auto_translate": True
            }

        return preferences

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch language preferences"
        )

@router.put("/language-preferences", response_model=LanguagePreferencesResponse)
async def update_my_language_preferences(
    preferences_data: LanguagePreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's language preferences
    SECURITY: Users can only update their own preferences
    """
    try:
        preferences = await final_phase_features_crud.update_language_preferences(
            current_user.id, preferences_data.dict(exclude_unset=True)
        )

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update language preferences"
            )

        return preferences

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update language preferences"
        )

@router.get("/regional-resources", response_model=List[RegionalResourceResponse])
async def get_regional_resources(
    country_code: Optional[str] = None,
    language_code: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get regional resources (crisis lines, support services)
    SECURITY: Public read access to active resources
    """
    try:
        resources = await final_phase_features_crud.get_regional_resources(
            country_code, language_code, resource_type, limit, offset
        )

        return resources

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch regional resources"
        )

# ===== ACCESSIBILITY ENHANCEMENTS ENDPOINTS (Phase 5) =====

@router.get("/accessibility-preferences", response_model=AccessibilityPreferencesResponse)
async def get_my_accessibility_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's accessibility preferences
    SECURITY: Users can only see their own preferences
    """
    try:
        preferences = await final_phase_features_crud.get_accessibility_preferences(
            current_user.id, current_user.id
        )

        if not preferences:
            # Return default preferences if none set
            return {
                "user_id": current_user.id,
                "high_contrast_mode": False,
                "font_size_multiplier": 1.0,
                "color_blind_mode": "none",
                "reduce_animations": False,
                "seizure_safe_mode": False,
                "screen_reader_optimized": False,
                "audio_descriptions": True,
                "mono_audio": False,
                "keyboard_only_navigation": False,
                "voice_control_enabled": False,
                "simplified_ui": False,
                "cognitive_load_reduction": False,
                "alt_text_required": True,
                "transcript_required": True
            }

        return preferences

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch accessibility preferences"
        )

@router.put("/accessibility-preferences", response_model=AccessibilityPreferencesResponse)
async def update_my_accessibility_preferences(
    preferences_data: AccessibilityPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's accessibility preferences
    SECURITY: Users can only update their own preferences
    """
    try:
        preferences = await final_phase_features_crud.update_accessibility_preferences(
            current_user.id, preferences_data.dict(exclude_unset=True)
        )

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update accessibility preferences"
            )

        return preferences

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update accessibility preferences"
        )

# ===== ENTERPRISE FEATURES ENDPOINTS (Phase 5) =====

@router.get("/organizations", response_model=List[OrganizationResponse])
async def get_my_organizations(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's organizations
    SECURITY: Users can only see organizations they belong to
    """
    try:
        organizations = await final_phase_features_crud.get_user_organizations(
            current_user.id, current_user.id
        )

        return organizations

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch organizations"
        )

@router.get("/organizations/{organization_id}/wellness-challenges", response_model=List[WellnessChallengeResponse])
async def get_organization_wellness_challenges(
    organization_id: UUID,
    active_only: bool = True,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get wellness challenges for an organization
    SECURITY: Users can only see challenges from their organizations
    """
    try:
        challenges = await final_phase_features_crud.get_organization_wellness_challenges(
            organization_id, current_user.id, active_only, limit, offset
        )

        return challenges

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wellness challenges"
        )

@router.post("/wellness-challenges/{challenge_id}/join")
async def join_wellness_challenge(
    challenge_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Join a wellness challenge
    SECURITY: Users can only join challenges they have access to
    """
    try:
        participant = await final_phase_features_crud.join_wellness_challenge(
            challenge_id, current_user.id
        )

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot join this challenge or challenge not found"
            )

        return {
            "message": "Successfully joined wellness challenge",
            "challenge_id": str(challenge_id),
            "participant_id": str(participant["id"])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join wellness challenge"
        )

# ===== ADVANCED AI FEATURES ENDPOINTS (Phase 6) =====

@router.post("/ai-chat/sessions", response_model=AIChatSessionResponse)
async def create_ai_chat_session(
    session_data: AIChatSessionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new AI chat session
    SECURITY: Users can only create their own sessions
    """
    try:
        session = await final_phase_features_crud.create_ai_chat_session(
            current_user.id, session_data.dict()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create AI chat session"
            )

        return session

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create AI chat session"
        )

@router.get("/ai-chat/sessions", response_model=List[AIChatSessionResponse])
async def get_my_ai_chat_sessions(
    session_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's AI chat sessions
    SECURITY: Users can only see their own sessions
    """
    try:
        sessions = await final_phase_features_crud.get_user_ai_chat_sessions(
            current_user.id, current_user.id, session_type, limit, offset
        )

        return sessions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch AI chat sessions"
        )

@router.post("/ai-chat/sessions/{session_id}/messages", response_model=AIChatMessageResponse)
async def add_ai_chat_message(
    session_id: UUID,
    message_data: AIChatMessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to AI chat session
    SECURITY: Users can only add messages to their own sessions
    """
    try:
        message = await final_phase_features_crud.add_ai_chat_message(
            session_id, current_user.id, message_data.dict()
        )

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )

        return message

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add chat message"
        )

@router.post("/voice-mood-analysis", response_model=VoiceMoodAnalysisResponse)
async def save_voice_mood_analysis(
    analysis_data: VoiceMoodAnalysisCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Save voice mood analysis results
    SECURITY: Users can only save their own analysis
    """
    try:
        analysis = await final_phase_features_crud.save_voice_mood_analysis(
            current_user.id, analysis_data.dict()
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save voice mood analysis"
            )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save voice mood analysis"
        )

# ===== INTEGRATION ECOSYSTEM ENDPOINTS (Phase 6) =====

@router.get("/integrations", response_model=List[UserIntegrationResponse])
async def get_my_integrations(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's integrations
    SECURITY: Users can only see their own integrations
    """
    try:
        integrations = await final_phase_features_crud.get_user_integrations(
            current_user.id, current_user.id
        )

        return integrations

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch integrations"
        )

@router.post("/integrations", response_model=UserIntegrationResponse)
async def create_integration(
    integration_data: UserIntegrationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user integration
    SECURITY: Users can only create their own integrations
    """
    try:
        integration = await final_phase_features_crud.create_user_integration(
            current_user.id, integration_data.dict()
        )

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create integration"
            )

        return integration

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create integration"
        )

@router.get("/emergency-contacts", response_model=List[EmergencyContactResponse])
async def get_my_emergency_contacts(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's emergency contacts
    SECURITY: Users can only see their own contacts
    """
    try:
        contacts = await final_phase_features_crud.get_emergency_contacts(
            current_user.id, current_user.id
        )

        return contacts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch emergency contacts"
        )

@router.post("/emergency-contacts", response_model=EmergencyContactResponse)
async def add_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add an emergency contact
    SECURITY: Users can only add their own contacts
    """
    try:
        contact = await final_phase_features_crud.add_emergency_contact(
            current_user.id, contact_data.dict()
        )

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add emergency contact"
            )

        return contact

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add emergency contact"
        )

# ===== COMMUNITY BUILDING ENDPOINTS (Phase 6) =====

@router.get("/peer-support/matches", response_model=List[PeerSupportMatchResponse])
async def get_my_peer_support_matches(
    match_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's peer support matches
    SECURITY: Users can only see their own matches
    """
    try:
        matches = await final_phase_features_crud.get_peer_support_matches(
            current_user.id, current_user.id, match_type, limit, offset
        )

        return matches

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch peer support matches"
        )

@router.get("/group-sessions", response_model=List[GroupSessionResponse])
async def get_group_sessions(
    upcoming_only: bool = True,
    session_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Get group sessions
    SECURITY: Public read access to sessions (no authentication required)
    """
    try:
        # Use default user ID for public access
        sessions = await final_phase_features_crud.get_group_sessions(
            UUID("00000000-0000-0000-0000-000000000000"), upcoming_only, session_type, limit, offset
        )

        return sessions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch group sessions"
        )

@router.post("/group-sessions/{session_id}/join")
async def join_group_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Join a group session
    SECURITY: Users can join public sessions
    """
    try:
        participant = await final_phase_features_crud.join_group_session(
            session_id, current_user.id
        )

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot join this session or session is full"
            )

        return {
            "message": "Successfully joined group session",
            "session_id": str(session_id),
            "participant_id": str(participant["id"])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join group session"
        )

# ===== USER FEEDBACK ENDPOINTS (Phase 6) =====

@router.post("/feedback", response_model=UserFeedbackResponse)
async def submit_feedback(
    feedback_data: UserFeedbackCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Submit user feedback
    SECURITY: Users can only submit their own feedback
    """
    try:
        feedback = await final_phase_features_crud.submit_user_feedback(
            current_user.id, feedback_data.dict()
        )

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit feedback"
            )

        return feedback

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )

@router.get("/feedback", response_model=List[UserFeedbackResponse])
async def get_my_feedback(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's feedback submissions
    SECURITY: Users can see their own feedback
    """
    try:
        feedback = await final_phase_features_crud.get_user_feedback(
            current_user.id, current_user.id, status, limit, offset
        )

        return feedback

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch feedback"
        )

# ===== HEALTH ENDPOINT =====

@router.get("/health")
async def final_phase_features_health(
    current_user: User = Depends(get_current_user)
):
    """
    Health check for final phase features service
    SECURITY: Requires authentication
    """
    try:
        health_ok = await final_phase_features_crud.health_check(current_user.id)

        if health_ok:
            return {"status": "healthy", "service": "final_phase_features"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Final phase features service unavailable"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Final phase features health check failed"
        )
