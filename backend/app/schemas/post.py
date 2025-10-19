from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.utils.timezone import timezone_handler
from .base import TimeStampedSchema

class PostVisibility(str, Enum):
    """Post visibility options"""
    PUBLIC = "public"
    PRIVATE = "private"
    SUPPORT_GROUP = "support_group"

class PostStatus(str, Enum):
    """Post status options"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ModerationStatus(str, Enum):
    """Moderation status options"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"

class PostContentType(str, Enum):
    """Post content types"""
    TEXT = "text"
    JOURNAL = "journal"  # For private journal entries

class PostBase(BaseModel):
    """Base post schema"""
    model_config = ConfigDict(from_attributes=True)

    content: str = Field(..., min_length=1, max_length=5000)
    content_type: PostContentType = PostContentType.TEXT
    mood: Optional[str] = Field(None, max_length=50)
    visibility: PostVisibility = PostVisibility.PUBLIC
    is_anonymous: bool = False

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content is not empty"""
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v: Optional[str]) -> Optional[str]:
        """Validate mood length"""
        if v and len(v) > 50:
            raise ValueError('Mood must be less than 50 characters')
        return v

class PostCreate(PostBase):
    """Schema for creating a post"""
    pass

class PostUpdate(BaseModel):
    """Schema for updating a post"""
    model_config = ConfigDict(from_attributes=True)

    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    mood: Optional[str] = Field(None, max_length=50)
    visibility: Optional[PostVisibility] = None
    status: Optional[PostStatus] = None

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate content is not empty"""
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip() if v else v

class PostInDB(TimeStampedSchema):
    """Post schema as stored in database"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    content: str
    content_type: PostContentType
    mood: Optional[str] = None
    visibility: PostVisibility
    is_anonymous: bool
    status: PostStatus
    moderation_status: ModerationStatus

class PostResponse(PostInDB):
    """Post schema for API responses"""
    username: Optional[str] = None  # Only show if not anonymous
    user_avatar: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def handle_anonymous_posts(cls, data: Any) -> Any:
        """Hide user info for anonymous posts - Pydantic V2 compatible"""
        if isinstance(data, dict):
            is_anonymous = data.get('is_anonymous', False)
            if is_anonymous:
                # Remove user information for anonymous posts
                data.pop('username', None)
                data.pop('user_avatar', None)
                # Explicitly set to None to ensure they're hidden
                data['username'] = None
                data['user_avatar'] = None
        return data

class PostWithUserInfo(PostResponse):
    """Post with full user info (for user's own posts)"""
    email: Optional[str] = None
    full_name: Optional[str] = None

class PostFeedResponse(BaseModel):
    """Response for post feed"""
    posts: List[PostResponse]
    total: int
    page: int
    has_next: bool

class PostFeedQuery(BaseModel):
    """Query parameters for post feed"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    visibility: Optional[PostVisibility] = None
    content_type: Optional[PostContentType] = None
    mood: Optional[str] = None

class ModerationQueueQuery(BaseModel):
    """Query parameters for moderation queue"""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    status: Optional[ModerationStatus] = ModerationStatus.PENDING

class ModerationAction(BaseModel):
    """Schema for moderation actions"""
    action: str = Field(..., description="approve, reject, or flag")
    reason: Optional[str] = Field(None, max_length=500, description="Moderation reason")
