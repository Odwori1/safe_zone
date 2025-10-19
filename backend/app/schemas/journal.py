from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from .post import PostContentType, PostVisibility

class JournalEntryBase(BaseModel):
    """Base journal entry schema"""
    model_config = ConfigDict(from_attributes=True)

    content: str = Field(..., min_length=1, max_length=5000)
    mood: Optional[str] = Field(None, max_length=50)

class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry"""
    pass

class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry"""
    model_config = ConfigDict(from_attributes=True)

    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    mood: Optional[str] = Field(None, max_length=50)

class JournalEntryResponse(JournalEntryBase):
    """Journal entry schema for API responses"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    mood: Optional[str] = None

class JournalFeedResponse(BaseModel):
    """Response for journal feed"""
    entries: List[JournalEntryResponse]
    total: int
    page: int
    has_next: bool

class JournalStats(BaseModel):
    """Journal statistics for user"""
    total_entries: int
    entries_this_week: int
    entries_this_month: int
    most_common_mood: Optional[str] = None
