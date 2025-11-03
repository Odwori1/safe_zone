"""
Moderation Schemas for Phase 3, Item 6
Following EXACT same patterns as other schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ContentReportBase(BaseModel):
    """Base schema for content reports"""
    content_type: str  # post, comment, message, user_profile
    content_id: UUID
    reason: str
    description: Optional[str] = None

    @validator('content_type')
    def validate_content_type(cls, v):
        if v not in ['post', 'comment', 'message', 'user_profile']:
            raise ValueError('Content type must be post, comment, message, or user_profile')
        return v

    @validator('reason')
    def validate_reason_length(cls, v):
        if len(v) < 1 or len(v) > 500:
            raise ValueError('Reason must be between 1 and 500 characters')
        return v

class ContentReportCreate(ContentReportBase):
    """Schema for creating a content report"""
    pass

class ContentReport(ContentReportBase):
    """Schema for content report response"""
    id: UUID
    reporter_id: UUID
    status: str  # pending, reviewed, action_taken, dismissed
    moderator_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ModerationActionBase(BaseModel):
    """Base schema for moderation actions"""
    action_type: str  # warn, mute, remove, ban, suspend
    target_user_id: UUID
    reason: str
    duration_minutes: Optional[int] = None

    @validator('action_type')
    def validate_action_type(cls, v):
        if v not in ['warn', 'mute', 'remove', 'ban', 'suspend']:
            raise ValueError('Action type must be warn, mute, remove, ban, or suspend')
        return v

class ModerationActionCreate(ModerationActionBase):
    """Schema for creating a moderation action"""
    pass

class ModerationAction(ModerationActionBase):
    """Schema for moderation action response"""
    id: UUID
    moderator_id: UUID
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BulkModerationRequest(BaseModel):
    """Schema for bulk moderation actions"""
    content_ids: List[UUID]
    action_type: str
    reason: str

class ModerationStats(BaseModel):
    """Schema for moderation statistics"""
    total_reports: int
    pending_reports: int
    resolved_reports: int
    active_moderators: int
    average_response_time: float
