from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class LiveAudioRoomBase(BaseModel):
    """Base schema for live audio rooms - FOLLOWING EXACT PATTERNS"""
    title: str
    description: Optional[str] = None
    visibility: str = "public"  # public, private
    max_participants: int = 50
    room_type: str = "support"  # support, discussion, social

    @validator('title')
    def validate_title_length(cls, v):
        if len(v) < 1 or len(v) > 255:
            raise ValueError('Title must be between 1 and 255 characters')
        return v

    @validator('visibility')
    def validate_visibility(cls, v):
        if v not in ['public', 'private']:
            raise ValueError('Visibility must be public or private')
        return v

    @validator('max_participants')
    def validate_max_participants(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Max participants must be between 1 and 100')
        return v

    @validator('room_type')
    def validate_room_type(cls, v):
        if v not in ['support', 'discussion', 'social']:
            raise ValueError('Room type must be support, discussion, or social')
        return v

class LiveAudioRoomCreate(LiveAudioRoomBase):
    """Schema for creating a live audio room"""
    pass

class LiveAudioRoomUpdate(BaseModel):
    """Schema for updating a live audio room"""
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('title')
    def validate_title_length(cls, v):
        if v is not None and (len(v) < 1 or len(v) > 255):
            raise ValueError('Title must be between 1 and 255 characters')
        return v

    @validator('visibility')
    def validate_visibility(cls, v):
        if v is not None and v not in ['public', 'private']:
            raise ValueError('Visibility must be public or private')
        return v

class LiveAudioRoom(LiveAudioRoomBase):
    """Schema for live audio room response"""
    id: UUID
    created_by: UUID
    is_active: bool
    current_participants: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoomParticipantBase(BaseModel):
    """Base schema for room participants"""
    role: str = "participant"

    @validator('role')
    def validate_role(cls, v):
        if v not in ['participant', 'speaker', 'moderator', 'host']:
            raise ValueError('Invalid role')
        return v

class RoomParticipantJoin(RoomParticipantBase):
    """Schema for joining a room"""
    pass

class RoomParticipant(RoomParticipantBase):
    """Schema for room participant response"""
    id: UUID
    room_id: UUID
    user_id: UUID
    username: str
    email: str
    joined_at: datetime
    left_at: Optional[datetime]
    last_active_at: datetime

    class Config:
        from_attributes = True

class WebRTCOffer(BaseModel):
    """Schema for WebRTC offer"""
    target_user_id: UUID
    offer: Dict[str, Any]

class WebRTCAnswer(BaseModel):
    """Schema for WebRTC answer"""
    target_user_id: UUID
    answer: Dict[str, Any]

class ICECandidate(BaseModel):
    """Schema for ICE candidate"""
    target_user_id: UUID
    candidate: Dict[str, Any]

class RoomModerationAction(BaseModel):
    """Schema for room moderation actions"""
    target_user_id: UUID
    action_type: str  # mute, remove, ban, warning
    reason: Optional[str] = None
    duration_minutes: Optional[int] = None

    @validator('action_type')
    def validate_action_type(cls, v):
        if v not in ['mute', 'remove', 'ban', 'warning']:
            raise ValueError('Invalid action type')
        return v

class UserPresenceUpdate(BaseModel):
    """Schema for user presence updates"""
    is_speaking: bool = False
    audio_enabled: bool = True
    video_enabled: bool = False
