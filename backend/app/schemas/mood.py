"""
Enhanced Mood Tracking Schemas with Professional Mental Health Features
"""

from pydantic import BaseModel, validator, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.utils.timezone import timezone_handler
from .base import TimeStampedSchema
from .mood_taxonomy import ProfessionalMood, MoodCategory, get_mood_category, get_mood_insights, validate_professional_mood

class MoodIntensity(int, Enum):
    """Mood intensity levels (1-10 scale)"""
    VERY_LOW = 1
    LOW = 2
    SLIGHTLY_LOW = 3
    NEUTRAL_LOW = 4
    NEUTRAL = 5
    NEUTRAL_HIGH = 6
    SLIGHTLY_HIGH = 7
    HIGH = 8
    VERY_HIGH = 9
    EXTREME = 10

class MoodBase(BaseModel):
    """Base mood entry schema"""
    model_config = ConfigDict(from_attributes=True)

    mood: str = Field(..., min_length=1, max_length=50, description="Professional mood description")
    intensity: Optional[MoodIntensity] = Field(None, description="Mood intensity from 1-10")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes about the mood")

    @validator('mood')
    @classmethod
    def validate_mood(cls, v: str) -> str:
        """Validate mood is not empty and suggest professional alternatives"""
        if not v.strip():
            raise ValueError('Mood cannot be empty')

        # Suggest professional mood if similar exists
        mood_lower = v.lower().strip()
        if not validate_professional_mood(mood_lower):
            # This is where we could suggest alternatives in the future
            pass

        return v.strip()

    @validator('intensity')
    @classmethod
    def validate_intensity(cls, v: Optional[int]) -> Optional[int]:
        """Validate intensity is between 1-10"""
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Intensity must be between 1 and 10')
        return v

class MoodEntryCreate(BaseModel):
    """Schema for creating a mood entry with extended fields"""
    mood: str
    intensity: Optional[int] = None
    notes: Optional[str] = None
    source_type: Optional[str] = 'standalone'
    source_id: Optional[UUID] = None
    triggers: Optional[List[str]] = []
    activities: Optional[List[str]] = []
    physical_symptoms: Optional[List[str]] = []
    social_context: Optional[str] = None
    sleep_quality: Optional[int] = None
    energy_level: Optional[int] = None
    location: Optional[str] = None
    weather: Optional[str] = None
    duration_minutes: Optional[int] = None
    medication_taken: Optional[bool] = False
    medication_notes: Optional[str] = None

    @validator('intensity')
    def validate_intensity(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Intensity must be between 1 and 10')
        return v

    @validator('source_type')
    def validate_source_type(cls, v):
        if v not in ['post', 'journal', 'standalone']:
            raise ValueError('Source type must be post, journal, or standalone')
        return v

    @validator('sleep_quality', 'energy_level')
    def validate_quality_levels(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Quality levels must be between 1 and 10')
        return v

class MoodEntryUpdate(BaseModel):
    """Schema for updating a mood entry"""
    mood: Optional[str] = Field(None, min_length=1, max_length=50, description="Mood description")
    intensity: Optional[int] = Field(None, ge=1, le=10, description="Mood intensity from 1-10")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes about the mood")
    triggers: Optional[List[str]] = None
    activities: Optional[List[str]] = None
    physical_symptoms: Optional[List[str]] = None
    social_context: Optional[str] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = None
    weather: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    medication_taken: Optional[bool] = None
    medication_notes: Optional[str] = None

    @validator('mood')
    def validate_mood(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Mood cannot be empty')
        return v.strip() if v else v

    @validator('intensity')
    def validate_intensity(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Intensity must be between 1 and 10')
        return v

class MoodEntryResponse(BaseModel):
    """Schema for mood entry response with extended fields"""
    id: UUID
    user_id: UUID
    mood: str
    intensity: Optional[int]
    notes: Optional[str]
    source_type: str
    source_id: Optional[UUID]
    triggers: List[str]
    activities: List[str]
    physical_symptoms: List[str]
    social_context: Optional[str]
    sleep_quality: Optional[int]
    energy_level: Optional[int]
    location: Optional[str]
    weather: Optional[str]
    duration_minutes: Optional[int]
    medication_taken: bool
    medication_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Professional mood analysis fields
    mood_category: Optional[str] = None
    energy_level_category: Optional[str] = None
    valence: Optional[str] = None
    clinical_insights: Optional[List[str]] = None

    class Config:
        from_attributes = True

    @validator('mood_category', pre=True, always=True)
    def set_mood_category(cls, v, values):
        """Set mood category based on mood"""
        if 'mood' in values and values['mood']:
            category = get_mood_category(values['mood'])
            return category.value if hasattr(category, 'value') else str(category)
        return v

    @validator('energy_level_category', pre=True, always=True)
    def set_energy_level_category(cls, v, values):
        """Set energy level category based on mood"""
        if 'mood' in values and values['mood']:
            insights = get_mood_insights(values['mood'])
            return insights.get('energy_level')
        return v

    @validator('valence', pre=True, always=True)
    def set_valence(cls, v, values):
        """Set valence based on mood"""
        if 'mood' in values and values['mood']:
            insights = get_mood_insights(values['mood'])
            return insights.get('valence')
        return v

    @validator('clinical_insights', pre=True, always=True)
    def set_clinical_insights(cls, v, values):
        """Set clinical insights based on mood"""
        if 'mood' in values and values['mood']:
            insights = get_mood_insights(values['mood'])
            return insights.get('recommendations', [])
        return v

class MoodEntryHybridResponse(MoodEntryResponse):
    """Schema for hybrid mood entries with context from posts/journals"""
    context_content: Optional[str] = None
    context_title: Optional[str] = None
    # Additional fields for joined data with proper UUID handling
    post_id: Optional[UUID] = None
    post_content: Optional[str] = None
    journal_id: Optional[UUID] = None
    journal_title: Optional[str] = None

class ClinicalInsights(BaseModel):
    """Clinical insights from mood patterns"""
    dominant_category: Optional[str]
    pattern_insights: List[str]
    clinical_recommendations: List[str]
    risk_factors: List[str]
    positive_patterns: List[str]

class MoodStats(BaseModel):
    """Mood statistics response with clinical insights"""
    total_entries: int
    average_intensity: Optional[float]
    most_common_mood: Optional[str]
    mood_frequency: Dict[str, int]
    category_distribution: Dict[str, int]
    weekly_trend: List[Dict[str, Any]]
    source_distribution: Optional[List[Dict[str, Any]]] = []
    top_triggers: Optional[List[Dict[str, Any]]] = []
    top_activities: Optional[List[Dict[str, Any]]] = []
    clinical_insights: Optional[ClinicalInsights] = None

class MoodSummary(BaseModel):
    """Mood summary over a period"""
    period: str
    average_mood: float
    mood_entries: int
    top_triggers: List[str]
    top_activities: List[str]
    insights: List[str]

class MoodHistoryResponse(BaseModel):
    """Response for mood history with pagination"""
    entries: List[MoodEntryResponse]
    total: int
    page: int
    has_next: bool

class MoodHistoryQuery(BaseModel):
    """Query parameters for mood history"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    days: Optional[int] = Field(None, ge=1, le=365, description="Number of days to look back")

class MoodTrendQuery(BaseModel):
    """Query parameters for mood trends"""
    days: int = Field(7, ge=1, le=365, description="Number of days for trend analysis")

class MoodTaxonomyResponse(BaseModel):
    """Response for professional mood taxonomy"""
    categories: Dict[str, List[str]]
    total_moods: int
