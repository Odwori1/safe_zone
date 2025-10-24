"""
Phase 6 Missing Features Schemas
Following EXACT same patterns as final_phase_features.py schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# ===== TELEHEALTH SESSIONS SCHEMAS =====

class TelehealthSessionBase(BaseModel):
    professional_id: UUID
    scheduled_time: datetime
    duration_minutes: Optional[int] = Field(60, ge=15, le=240)
    session_status: Optional[str] = Field("scheduled", max_length=50)
    meeting_url: Optional[str] = None
    notes: Optional[str] = None

class TelehealthSessionCreate(TelehealthSessionBase):
    pass

class TelehealthSessionResponse(TelehealthSessionBase):
    id: UUID
    user_id: UUID
    patient_username: Optional[str] = None
    professional_username: Optional[str] = None
    recording_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== EMR CONNECTIONS SCHEMAS =====

class EMRConnectionBase(BaseModel):
    emr_system: str = Field(..., max_length=100)
    connection_status: Optional[str] = Field("pending", max_length=50)
    consent_given_at: datetime
    consent_expires_at: datetime
    access_token_encrypted: Optional[str] = None
    refresh_token_encrypted: Optional[str] = None

class EMRConnectionCreate(EMRConnectionBase):
    pass

class EMRConnectionResponse(EMRConnectionBase):
    id: UUID
    user_id: UUID
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== COMMUNITY MILESTONES SCHEMAS =====

class CommunityMilestoneBase(BaseModel):
    milestone_type: str = Field(..., max_length=100)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    achieved_at: datetime
    community_impact_metric: Optional[Dict[str, Any]] = None

class CommunityMilestoneResponse(CommunityMilestoneBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ===== SUCCESS STORIES SCHEMAS =====

class SuccessStoryBase(BaseModel):
    title: str = Field(..., max_length=200)
    story_content: str
    consent_given: Optional[bool] = False
    consent_given_at: Optional[datetime] = None
    anonymized: Optional[bool] = True
    featured: Optional[bool] = False

class SuccessStoryCreate(SuccessStoryBase):
    pass

class SuccessStoryResponse(SuccessStoryBase):
    id: UUID
    user_id: UUID
    username: Optional[str] = None
    featured_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== USER SESSIONS SCHEMAS =====

class UserSessionBase(BaseModel):
    device_id: str = Field(..., max_length=100)
    expires_at: datetime

class UserSessionCreate(UserSessionBase):
    pass

class UserSessionResponse(UserSessionBase):
    id: UUID
    user_id: UUID
    last_activity: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ===== DEVICE SYNC SCHEMAS =====

class DeviceSyncBase(BaseModel):
    device_type: str = Field(..., max_length=50)
    device_id: str = Field(..., max_length=100)
    sync_token: Optional[str] = Field(None, max_length=200)

class DeviceSyncCreate(DeviceSyncBase):
    pass

class DeviceSyncResponse(DeviceSyncBase):
    id: UUID
    user_id: UUID
    last_sync: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ===== TUTORIAL PROGRESS SCHEMAS =====

class TutorialProgressBase(BaseModel):
    tutorial_module: str = Field(..., max_length=100)
    progress_percentage: Optional[int] = Field(0, ge=0, le=100)
    completed: Optional[bool] = False
    completed_at: Optional[datetime] = None

class TutorialProgressCreate(TutorialProgressBase):
    pass

class TutorialProgressResponse(TutorialProgressBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== CONTENT SUMMARIZATION SCHEMAS =====

class ContentSummaryUpdate(BaseModel):
    content_summary: Optional[str] = None
    summary_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

class ContentSummaryResponse(BaseModel):
    id: UUID
    content_summary: Optional[str] = None
    summary_confidence: Optional[float] = None
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== HEALTH SCHEMA =====

class Phase6HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
