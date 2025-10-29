"""
Missing Phase 1 & 2 Features Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# ===== PASSWORD RESET SCHEMAS =====

class PasswordResetRequest(BaseModel):
    email: str = Field(..., max_length=255)

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class PasswordResetTokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    expires_at: datetime
    used: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ===== REACTION SCHEMAS =====

class ReactionBase(BaseModel):
    reaction_type: str = Field(..., pattern='^(heart|hug|star|lightbulb)$')

class ReactionCreate(ReactionBase):
    post_id: UUID

class ReactionResponse(ReactionBase):
    id: UUID
    user_id: UUID
    post_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class PostReactionsResponse(BaseModel):
    reaction_type: str
    count: int
    user_reacted: bool

    class Config:
        from_attributes = True

# ===== SAVED POSTS SCHEMAS =====

class SavedPostBase(BaseModel):
    post_id: UUID

class SavedPostResponse(SavedPostBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ===== CIRCLES SCHEMAS =====

class CircleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    topic: str = Field(..., max_length=50)
    is_public: Optional[bool] = True
    allow_anonymous_posts: Optional[bool] = False

class CircleCreate(CircleBase):
    pass

class CircleResponse(CircleBase):
    id: UUID
    moderator_id: Optional[UUID]
    moderator_username: Optional[str]
    member_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CircleMemberResponse(BaseModel):
    id: UUID
    circle_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True

class CirclePostBase(BaseModel):
    circle_id: UUID
    is_anonymous: Optional[bool] = False

class CirclePostCreate(CirclePostBase):
    post_id: UUID

class CirclePostResponse(CirclePostBase):
    id: UUID
    post_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# ===== HEALTH SCHEMA =====

class MissingFeaturesHealthResponse(BaseModel):
    status: str
    service: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
