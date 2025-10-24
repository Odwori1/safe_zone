"""
Final Phase Features Schemas for Phase 5 & 6
Following EXACT same patterns as enhanced_ux_community.py schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime, time

# ===== MULTI-LANGUAGE SUPPORT SCHEMAS (Phase 5) =====

class LanguagePreferencesBase(BaseModel):
    preferred_language: Optional[str] = Field("en", max_length=10)
    interface_language: Optional[str] = Field("en", max_length=10)
    content_language: Optional[str] = Field("en", max_length=10)
    auto_translate: Optional[bool] = True

class LanguagePreferencesUpdate(LanguagePreferencesBase):
    pass

class LanguagePreferencesResponse(LanguagePreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RegionalResourceBase(BaseModel):
    country_code: str = Field(..., max_length=5)
    language_code: str = Field(..., max_length=10)
    resource_type: str = Field(..., max_length=50)
    resource_name: str = Field(..., max_length=200)
    contact_info: str
    operating_hours: Optional[str] = None
    services_offered: Optional[List[str]] = None

class RegionalResourceResponse(RegionalResourceBase):
    id: UUID
    is_active: bool
    verification_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== ACCESSIBILITY ENHANCEMENTS SCHEMAS (Phase 5) =====

class AccessibilityPreferencesBase(BaseModel):
    # Visual
    high_contrast_mode: Optional[bool] = False
    font_size_multiplier: Optional[float] = Field(1.0, ge=0.5, le=3.0)
    color_blind_mode: Optional[str] = Field("none", max_length=20)
    reduce_animations: Optional[bool] = False
    seizure_safe_mode: Optional[bool] = False
    
    # Audio
    screen_reader_optimized: Optional[bool] = False
    audio_descriptions: Optional[bool] = True
    mono_audio: Optional[bool] = False
    
    # Interaction
    keyboard_only_navigation: Optional[bool] = False
    voice_control_enabled: Optional[bool] = False
    simplified_ui: Optional[bool] = False
    cognitive_load_reduction: Optional[bool] = False
    
    # Content
    alt_text_required: Optional[bool] = True
    transcript_required: Optional[bool] = True

class AccessibilityPreferencesUpdate(AccessibilityPreferencesBase):
    pass

class AccessibilityPreferencesResponse(AccessibilityPreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== ENTERPRISE FEATURES SCHEMAS (Phase 5) =====

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    organization_type: str = Field(..., max_length=50)
    size_range: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=200)
    website_url: Optional[str] = Field(None, max_length=500)

class OrganizationResponse(OrganizationBase):
    id: UUID
    is_verified: bool
    subscription_tier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrganizationMemberResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class WellnessChallengeBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    challenge_type: str = Field(..., max_length=50)
    start_date: date
    end_date: date
    participation_goal: Optional[int] = Field(None, ge=1)
    is_public: Optional[bool] = False

class WellnessChallengeCreate(WellnessChallengeBase):
    organization_id: Optional[UUID] = None

class WellnessChallengeResponse(WellnessChallengeBase):
    id: UUID
    organization_id: Optional[UUID]
    participant_count: int
    is_participating: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== ADVANCED AI FEATURES SCHEMAS (Phase 6) =====

class AIChatSessionBase(BaseModel):
    session_type: str = Field(..., max_length=50)
    context_data: Optional[Dict[str, Any]] = None

class AIChatSessionCreate(AIChatSessionBase):
    pass

class AIChatSessionResponse(AIChatSessionBase):
    id: UUID
    user_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    session_duration_seconds: Optional[int] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    created_at: datetime

    class Config:
        from_attributes = True

class AIChatMessageBase(BaseModel):
    message_type: str = Field(..., max_length=20)
    content: str
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    urgency_level: Optional[str] = Field(None, max_length=20)

class AIChatMessageCreate(AIChatMessageBase):
    pass

class AIChatMessageResponse(AIChatMessageBase):
    id: UUID
    session_id: UUID
    response_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class VoiceMoodAnalysisBase(BaseModel):
    audio_file_url: Optional[str] = None
    analysis_result: Dict[str, Any]
    mood_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    detected_emotions: Optional[List[str]] = None

class VoiceMoodAnalysisCreate(VoiceMoodAnalysisBase):
    pass

class VoiceMoodAnalysisResponse(VoiceMoodAnalysisBase):
    id: UUID
    user_id: UUID
    analysis_timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ===== INTEGRATION ECOSYSTEM SCHEMAS (Phase 6) =====

class UserIntegrationBase(BaseModel):
    integration_type: str = Field(..., max_length=50)
    service_name: str = Field(..., max_length=100)
    sync_frequency: Optional[str] = Field("daily", max_length=20)
    config_data: Optional[Dict[str, Any]] = None

class UserIntegrationCreate(UserIntegrationBase):
    pass

class UserIntegrationResponse(UserIntegrationBase):
    id: UUID
    user_id: UUID
    connection_status: str
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmergencyContactBase(BaseModel):
    contact_name: str = Field(..., max_length=200)
    contact_relationship: Optional[str] = Field(None, max_length=100)
    contact_methods: Dict[str, Any]
    notification_preferences: Optional[Dict[str, Any]] = None
    is_primary: Optional[bool] = False

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactResponse(EmergencyContactBase):
    id: UUID
    user_id: UUID
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== COMMUNITY BUILDING SCHEMAS (Phase 6) =====

class PeerSupportMatchBase(BaseModel):
    matched_user_id: UUID
    match_reason: Optional[str] = None
    match_type: Optional[str] = Field("wellness", max_length=50)

class PeerSupportMatchResponse(PeerSupportMatchBase):
    id: UUID
    user_id: UUID
    compatibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: str
    matched_at: datetime
    last_interaction: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class GroupSessionBase(BaseModel):
    session_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    max_participants: Optional[int] = Field(None, ge=1)
    scheduled_time: datetime
    duration_minutes: Optional[int] = Field(60, ge=1, le=480)
    platform: Optional[str] = Field(None, max_length=50)
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[str] = Field(None, max_length=100)

class GroupSessionCreate(GroupSessionBase):
    pass

class GroupSessionResponse(GroupSessionBase):
    id: UUID
    facilitator_id: Optional[UUID]
    facilitator_username: Optional[str]
    participant_count: int
    is_participating: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== USER FEEDBACK SCHEMAS (Phase 6) =====

class UserFeedbackBase(BaseModel):
    feedback_type: str = Field(..., max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    description: str
    urgency: Optional[str] = Field("medium", max_length=20)

class UserFeedbackCreate(UserFeedbackBase):
    pass

class UserFeedbackResponse(UserFeedbackBase):
    id: UUID
    user_id: UUID
    status: str
    assigned_to: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== HEALTH SCHEMA =====

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
