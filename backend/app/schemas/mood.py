from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.utils.timezone import timezone_handler
from .base import TimeStampedSchema

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

    mood: str = Field(..., min_length=1, max_length=50, description="Mood description (e.g., happy, sad, anxious)")
    intensity: Optional[MoodIntensity] = Field(None, description="Mood intensity from 1-10")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes about the mood")

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v: str) -> str:
        """Validate mood is not empty"""
        if not v.strip():
            raise ValueError('Mood cannot be empty')
        return v.strip()

    @field_validator('intensity')
    @classmethod
    def validate_intensity(cls, v: Optional[int]) -> Optional[int]:
        """Validate intensity is between 1-10"""
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Intensity must be between 1 and 10')
        return v

class MoodEntryCreate(MoodBase):
    """Schema for creating a mood entry"""
    pass

class MoodEntryUpdate(BaseModel):
    """Schema for updating a mood entry"""
    model_config = ConfigDict(from_attributes=True)

    mood: Optional[str] = Field(None, min_length=1, max_length=50)
    intensity: Optional[MoodIntensity] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v: Optional[str]) -> Optional[str]:
        """Validate mood is not empty"""
        if v is not None and not v.strip():
            raise ValueError('Mood cannot be empty')
        return v.strip() if v else v

class MoodEntryInDB(TimeStampedSchema):
    """Mood entry schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    mood: str
    intensity: Optional[int] = None
    notes: Optional[str] = None

class MoodEntryResponse(MoodEntryInDB):
    """Mood entry schema for API responses"""
    pass

class MoodHistoryResponse(BaseModel):
    """Response for mood history with pagination"""
    entries: List[MoodEntryResponse]
    total: int
    page: int
    has_next: bool

class MoodStats(BaseModel):
    """Mood statistics response"""
    total_entries: int
    average_intensity: Optional[float] = None
    most_common_mood: Optional[str] = None
    mood_frequency: Dict[str, int]
    weekly_trend: List[Dict[str, Any]]

class MoodHistoryQuery(BaseModel):
    """Query parameters for mood history"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    days: Optional[int] = Field(None, ge=1, le=365, description="Number of days to look back")

class MoodTrendQuery(BaseModel):
    """Query parameters for mood trends"""
    days: int = Field(7, ge=1, le=365, description="Number of days for trend analysis")
