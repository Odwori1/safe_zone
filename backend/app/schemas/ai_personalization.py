"""
AI Personalization Schemas for Phase 4, Item 1
Following EXACT same patterns as professional_directory.py schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import time, datetime

# ===== CONTENT ANALYSIS SCHEMAS =====

class ContentAnalysisBase(BaseModel):
    content_type: str
    content_id: UUID
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    sentiment_label: Optional[str] = Field(None, max_length=20)
    emotion_tags: Optional[List[str]] = None
    content_categories: Optional[List[str]] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    toxicity_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class ContentAnalysisResponse(ContentAnalysisBase):
    id: UUID
    analysis_model: Optional[str]
    confidence_score: Optional[float]
    analysis_timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== USER BEHAVIOR PATTERNS SCHEMAS =====

class UserBehaviorPatternsBase(BaseModel):
    avg_mood_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    mood_volatility: Optional[float] = Field(None, ge=0.0, le=1.0)
    common_mood_patterns: Optional[List[str]] = None
    weekly_rhythm: Optional[Dict[str, Any]] = None
    posting_frequency_daily: Optional[float] = Field(None, ge=0.0)
    active_hours: Optional[List[str]] = None
    engagement_level: Optional[str] = Field(None, max_length=20)
    preferred_content_types: Optional[List[str]] = None
    interested_topics: Optional[List[str]] = None

class UserBehaviorPatternsResponse(UserBehaviorPatternsBase):
    id: UUID
    user_id: UUID
    pattern_confidence: Optional[float]
    last_analysis_date: Optional[datetime]
    analysis_period_days: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== PERSONALIZED RECOMMENDATIONS SCHEMAS =====

class PersonalizedRecommendationBase(BaseModel):
    recommendation_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    reasoning: Optional[str] = None
    content_type: Optional[str] = Field(None, max_length=50)
    content_id: Optional[UUID] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    priority_level: Optional[str] = Field("medium", max_length=20)

class PersonalizedRecommendationCreate(PersonalizedRecommendationBase):
    expires_at: Optional[datetime] = None
    optimal_viewing_time: Optional[time] = None

class PersonalizedRecommendationResponse(PersonalizedRecommendationBase):
    id: UUID
    user_id: UUID
    is_dismissed: bool
    is_completed: bool
    user_feedback: Optional[str]
    feedback_notes: Optional[str]
    recommended_at: datetime
    expires_at: Optional[datetime]
    optimal_viewing_time: Optional[time]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== COPING STRATEGIES SCHEMAS =====

class CopingStrategyBase(BaseModel):
    strategy_name: str = Field(..., max_length=200)
    strategy_type: str = Field(..., max_length=50)
    description: str
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=240)
    target_emotions: Optional[List[str]] = None
    target_intensity: Optional[str] = Field(None, max_length=20)
    effectiveness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    difficulty_level: Optional[str] = Field("beginner", max_length=20)

class CopingStrategyResponse(CopingStrategyBase):
    id: UUID
    requires_resources: Optional[bool]
    resources_description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCopingPreferenceUpdate(BaseModel):
    preference_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    last_used_at: Optional[datetime] = None
    usage_count: Optional[int] = Field(None, ge=0)
    context_tags: Optional[List[str]] = None
    ai_recommendation_score: Optional[float] = Field(None, ge=0.0, le=1.0)

# ===== NOTIFICATION PREFERENCES SCHEMAS =====

class NotificationPreferencesBase(BaseModel):
    optimal_morning_time: Optional[time] = None
    optimal_afternoon_time: Optional[time] = None
    optimal_evening_time: Optional[time] = None
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    timezone: Optional[str] = Field(None, max_length=50)
    receive_mood_insights: Optional[bool] = None
    receive_wellness_tips: Optional[bool] = None
    receive_community_updates: Optional[bool] = None
    receive_professional_suggestions: Optional[bool] = None
    preferred_notification_types: Optional[List[str]] = None
    max_daily_notifications: Optional[int] = Field(None, ge=0, le=50)
    mood_based_timing: Optional[bool] = None
    engagement_based_frequency: Optional[bool] = None

class NotificationPreferencesUpdate(NotificationPreferencesBase):
    pass

class NotificationPreferencesResponse(NotificationPreferencesBase):
    id: UUID
    user_id: UUID
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
