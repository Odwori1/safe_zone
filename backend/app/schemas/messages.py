"""
Message Schemas for Phase 3, Item 4
Following EXACT same patterns as other schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ConversationBase(BaseModel):
    """Base schema for conversations"""
    is_group: bool = False
    title: Optional[str] = None

    @validator('title')
    def validate_title_length(cls, v):
        if v is not None and (len(v) < 1 or len(v) > 255):
            raise ValueError('Title must be between 1 and 255 characters')
        return v

class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""
    participant_ids: Optional[List[UUID]] = None

class Conversation(ConversationBase):
    """Schema for conversation response"""
    id: UUID
    created_by: UUID  # ADD THIS LINE
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    """Base schema for messages"""
    content: str
    content_type: str = "text"  # text, audio, video, file
    file_metadata_id: Optional[UUID] = None

    @validator('content')
    def validate_content_length(cls, v):
        if len(v) < 1 or len(v) > 5000:
            raise ValueError('Message content must be between 1 and 5000 characters')
        return v

    @validator('content_type')
    def validate_content_type(cls, v):
        if v not in ['text', 'audio', 'video', 'file']:
            raise ValueError('Content type must be text, audio, video, or file')
        return v

class MessageCreate(MessageBase):
    """Schema for creating a message"""
    pass

class Message(MessageBase):
    """Schema for message response"""
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    username: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted: bool = False
    moderated: bool = False
    moderation_status: Optional[str] = None

    class Config:
        from_attributes = True

class ConversationParticipantBase(BaseModel):
    """Base schema for conversation participants"""
    role: str = "participant"  # participant, admin, moderator

    @validator('role')
    def validate_role(cls, v):
        if v not in ['participant', 'admin', 'moderator']:
            raise ValueError('Role must be participant, admin, or moderator')
        return v

class ConversationParticipant(ConversationParticipantBase):
    """Schema for conversation participant response"""
    id: UUID
    conversation_id: UUID
    user_id: UUID
    username: str
    email: str
    joined_at: datetime
    last_active_at: datetime

    class Config:
        from_attributes = True

class ConversationWithDetails(Conversation):
    """Extended conversation schema with details"""
    last_message_content: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_sender_id: Optional[UUID] = None
    message_count: int = 0
    participant_count: int = 0

class WebRTCMessage(BaseModel):
    """Schema for WebRTC signaling messages"""
    target_user_id: UUID
    message_type: str  # offer, answer, candidate, hangup
    data: Dict[str, Any]

    @validator('message_type')
    def validate_message_type(cls, v):
        if v not in ['offer', 'answer', 'candidate', 'hangup']:
            raise ValueError('Message type must be offer, answer, candidate, or hangup')
        return v

class TypingIndicator(BaseModel):
    """Schema for typing indicators"""
    is_typing: bool
    conversation_id: UUID

class MessageReadReceipt(BaseModel):
    """Schema for message read receipts"""
    message_id: UUID
    read_at: datetime
