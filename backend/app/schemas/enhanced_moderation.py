"""
Enhanced Moderation Schemas for Phase 3, Item 6
Following EXACT same patterns as live_audio_rooms.py schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class ModerationActionType(str, Enum):
    MUTE = "mute"
    UNMUTE = "unmute" 
    REMOVE = "remove"
    BAN = "ban"
    WARN = "warn"
    PROMOTE = "promote"
    DEMOTE = "demote"
    LOCK_ROOM = "lock_room"
    UNLOCK_ROOM = "unlock_room"

class ModerationActionCreate(BaseModel):
    target_user_id: UUID
    action_type: ModerationActionType
    reason: Optional[str] = None
    duration_minutes: Optional[int] = None  # For temporary actions
    
class ModerationActionResponse(BaseModel):
    id: UUID
    room_id: UUID
    moderator_id: UUID
    target_user_id: UUID
    action_type: ModerationActionType
    reason: Optional[str]
    duration_minutes: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportContentCreate(BaseModel):
    content_type: str  # 'message', 'post', 'comment', 'room'
    content_id: UUID
    reason: str
    description: Optional[str] = None

class RoomLockStatus(BaseModel):
    room_id: UUID
    is_locked: bool
    locked_by: Optional[UUID]
    lock_reason: Optional[str]
