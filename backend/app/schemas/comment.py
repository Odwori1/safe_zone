from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum
from .base import TimeStampedSchema

class CommentStatus(str, Enum):
    """Comment status options"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ModerationStatus(str, Enum):
    """Moderation status options"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"

class CommentBase(BaseModel):
    """Base comment schema"""
    model_config = ConfigDict(from_attributes=True)

    content: str = Field(..., min_length=1, max_length=2000)
    is_anonymous: bool = False

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty"""
        if not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v.strip()

class CommentCreate(CommentBase):
    """Schema for creating a comment"""
    post_id: UUID
    parent_comment_id: Optional[UUID] = None

class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    model_config = ConfigDict(from_attributes=True)

    content: Optional[str] = Field(None, min_length=1, max_length=2000)

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate content is not empty"""
        if v is not None and not v.strip():
            raise ValueError('Comment content cannot be empty')
        return v.strip() if v else v

class CommentInDB(TimeStampedSchema):
    """Comment schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    post_id: UUID
    parent_comment_id: Optional[UUID] = None
    content: str
    is_anonymous: bool
    status: CommentStatus
    moderation_status: ModerationStatus

class CommentResponse(CommentInDB):
    """Comment schema for API responses"""
    username: Optional[str] = None  # Only show if not anonymous
    user_avatar: Optional[str] = None

class CommentThreadResponse(CommentResponse):
    """Comment with nested replies for thread display"""
    replies: List['CommentResponse'] = []

class CommentFeedResponse(BaseModel):
    """Response for comment feed"""
    comments: List[CommentResponse]
    total: int
    page: int
    has_next: bool

class CommentFilters(BaseModel):
    """Schema for comment filtering"""
    post_id: Optional[UUID] = None
    parent_comment_id: Optional[UUID] = None
    moderation_status: Optional[ModerationStatus] = None
