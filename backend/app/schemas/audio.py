from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class AudioRoomBase(BaseModel):
    title: str
    description: Optional[str] = None
    visibility: str = "public"
    max_participants: int = 10
    room_type: str = "support"
    is_active: bool = True

class AudioRoomCreate(AudioRoomBase):
    pass

class AudioRoomUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    max_participants: Optional[int] = None
    room_type: Optional[str] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    lock_reason: Optional[str] = None

class AudioRoomParticipant(BaseModel):
    id: UUID4
    user_id: UUID4
    username: str
    joined_at: datetime
    is_speaker: bool
    is_moderator: bool

class AudioRoom(AudioRoomBase):
    id: UUID4
    created_by: UUID4
    is_locked: bool = False
    locked_by: Optional[UUID4] = None
    lock_reason: Optional[str] = None
    locked_at: Optional[datetime] = None
    current_participants: int = 0
    host_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AudioRoomWithParticipants(AudioRoom):
    participants: List[AudioRoomParticipant] = []

class AudioRoomParticipantBase(BaseModel):
    is_speaker: bool = False
    is_moderator: bool = False

class AudioRoomParticipantCreate(AudioRoomParticipantBase):
    room_id: UUID4

class AudioRoomParticipantResponse(AudioRoomParticipantBase):
    id: UUID4
    room_id: UUID4
    user_id: UUID4
    username: str
    joined_at: datetime
    left_at: Optional[datetime] = None
