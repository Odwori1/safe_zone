"""
Enhanced Journal Schemas - Using separate journals table with professional features
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class JournalStatus(str, Enum):
    """Journal status options"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class JournalBase(BaseModel):
    """Base journal schema - Enhanced for mental health features"""
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, max_length=500, description="Optional journal title")
    content: str = Field(..., min_length=1, max_length=10000, description="Journal content")
    mood: Optional[str] = Field(None, max_length=50, description="Current mood")
    mood_intensity: Optional[int] = Field(None, ge=1, le=10, description="Mood intensity 1-10")
    tags: Optional[List[str]] = Field(None, description="Tags for organization")
    prompt_id: Optional[UUID] = Field(None, description="Optional writing prompt")

class JournalCreate(JournalBase):
    """Schema for creating a journal entry"""
    pass

class JournalUpdate(BaseModel):
    """Schema for updating a journal entry"""
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    mood: Optional[str] = Field(None, max_length=50)
    mood_intensity: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    prompt_id: Optional[UUID] = None
    status: Optional[JournalStatus] = None

class JournalResponse(BaseModel):
    """Journal schema for API responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: Optional[str]
    content: str
    content_type: str = "journal"
    mood: Optional[str]
    mood_intensity: Optional[int]
    tags: Optional[List[str]]
    word_count: int
    read_time_minutes: int
    is_encrypted: bool
    status: JournalStatus
    prompt_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

class JournalWithPrompt(JournalResponse):
    """Journal with prompt information"""
    prompt_text: Optional[str] = None
    prompt_category: Optional[str] = None

class JournalPrompt(BaseModel):
    """Journal prompt schema"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt_text: str
    category: str
    difficulty_level: str
    is_active: bool
    created_at: datetime

class JournalFeedResponse(BaseModel):
    """Response for journal feed"""
    entries: List[JournalWithPrompt]
    total: int
    page: int
    has_next: bool

class JournalStats(BaseModel):
    """Enhanced journal statistics for user"""
    total_entries: int
    total_words: int
    average_mood: Optional[float]
    most_used_tags: List[str]
    entries_this_week: int
    entries_this_month: int
    most_common_mood: Optional[str] = None
