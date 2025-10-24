"""
Enhanced UX & Community Management Schemas for Phase 4, Items 3 & 4
Following EXACT same patterns as advanced_safety_systems.py schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime, time

# ===== USER UI PREFERENCES SCHEMAS (Item 3) =====

class UserUIPreferencesBase(BaseModel):
    theme_preference: Optional[str] = Field("system", max_length=20)
    font_size: Optional[str] = Field("medium", max_length=20)
    high_contrast_mode: Optional[bool] = False
    reduced_motion: Optional[bool] = False
    screen_reader_optimized: Optional[bool] = False
    keyboard_navigation: Optional[bool] = True
    focus_indicators: Optional[bool] = True
    content_density: Optional[str] = Field("comfortable", max_length=20)
    image_descriptions: Optional[bool] = True
    auto_play_media: Optional[bool] = False
    language_preference: Optional[str] = Field("en", max_length=10)
    timezone: Optional[str] = Field("UTC", max_length=50)
    date_format: Optional[str] = Field("YYYY-MM-DD", max_length=20)
    email_notifications: Optional[bool] = True
    push_notifications: Optional[bool] = True
    show_online_status: Optional[bool] = True

class UserUIPreferencesUpdate(UserUIPreferencesBase):
    pass

class UserUIPreferencesResponse(UserUIPreferencesBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== OFFLINE CONTENT SCHEMAS (Item 3) =====

class OfflineContentBase(BaseModel):
    content_type: str = Field(..., max_length=50)
    content_id: UUID
    content_data: Dict[str, Any]
    file_size_bytes: Optional[int] = Field(None, ge=0)
    expires_at: Optional[datetime] = None
    is_pinned: Optional[bool] = False

class OfflineContentCreate(OfflineContentBase):
    pass

class OfflineContentResponse(OfflineContentBase):
    id: UUID
    user_id: UUID
    last_accessed: datetime
    access_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== DATA EXPORT JOBS SCHEMAS (Item 3) =====

class DataExportJobBase(BaseModel):
    export_format: str = Field("json", max_length=20)
    data_categories: Optional[List[str]] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None

class DataExportJobCreate(DataExportJobBase):
    pass

class DataExportJobResponse(DataExportJobBase):
    id: UUID
    user_id: UUID
    status: str
    progress_percent: int
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    download_count: int
    access_token: UUID
    expires_at: datetime
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ===== COMMUNITY ANALYTICS SCHEMAS (Item 4) =====

class CommunityAnalyticsBase(BaseModel):
    date: date
    active_users: Optional[int] = 0
    new_registrations: Optional[int] = 0
    posts_created: Optional[int] = 0
    comments_created: Optional[int] = 0
    support_sessions: Optional[int] = 0
    avg_session_duration_minutes: Optional[float] = Field(None, ge=0)
    bounce_rate: Optional[float] = Field(None, ge=0, le=1)
    crisis_interventions: Optional[int] = 0
    content_reports: Optional[int] = 0
    resolved_reports: Optional[int] = 0
    response_time_ms: Optional[float] = Field(None, ge=0)
    uptime_percent: Optional[float] = Field(None, ge=0, le=100)

class CommunityAnalyticsResponse(CommunityAnalyticsBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ===== USER REPUTATION SCHEMAS (Item 4) =====

class UserReputationBase(BaseModel):
    helpfulness_score: Optional[int] = 0
    support_score: Optional[int] = 0
    engagement_score: Optional[int] = 0
    consistency_score: Optional[int] = 0
    verified_contributor: Optional[bool] = False
    trusted_member: Optional[bool] = False
    warning_count: Optional[int] = 0
    last_warning_date: Optional[date] = None

class UserReputationResponse(UserReputationBase):
    id: UUID
    user_id: UUID
    account_age_days: int
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== CONFLICT RESOLUTION SCHEMAS (Item 4) =====

class ConflictResolutionCaseBase(BaseModel):
    case_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field("medium", max_length=20)
    reported_user_id: Optional[UUID] = None
    content_reference_type: Optional[str] = Field(None, max_length=50)
    content_reference_id: Optional[UUID] = None

class ConflictResolutionCaseCreate(ConflictResolutionCaseBase):
    pass

class ConflictResolutionCaseResponse(ConflictResolutionCaseBase):
    id: UUID
    reporter_id: UUID
    assigned_moderator_id: Optional[UUID] = None
    status: str
    resolution_notes: Optional[str] = None
    resolution_type: Optional[str] = None
    reported_at: datetime
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== COMMUNITY EVENTS SCHEMAS (Item 4) =====

class CommunityEventBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    event_type: str = Field(..., max_length=50)
    start_time: datetime
    end_time: datetime
    timezone: Optional[str] = Field("UTC", max_length=50)
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[str] = Field(None, max_length=100)
    max_participants: Optional[int] = Field(None, ge=1)
    is_public: Optional[bool] = True
    requires_rsvp: Optional[bool] = False
    event_platform: Optional[str] = Field(None, max_length=50)
    platform_link: Optional[str] = None

class CommunityEventCreate(CommunityEventBase):
    pass

class CommunityEventResponse(CommunityEventBase):
    id: UUID
    host_id: Optional[UUID] = None
    co_host_ids: Optional[List[UUID]] = None
    rsvp_count: int
    attendance_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== MODERATOR TRAINING SCHEMAS (Item 4) =====

class TrainingModuleBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    content_type: str = Field(..., max_length=50)
    content_url: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    required_for_role: Optional[str] = Field(None, max_length=50)
    difficulty_level: Optional[str] = Field("beginner", max_length=20)

class TrainingModuleResponse(TrainingModuleBase):
    id: UUID
    is_active: bool
    version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingProgressUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=20)
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    score: Optional[float] = Field(None, ge=0, le=100)
    attempts: Optional[int] = Field(None, ge=0)
    feedback: Optional[str] = None

class TrainingProgressResponse(TrainingProgressUpdate):
    id: UUID
    user_id: UUID
    module_id: UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
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
