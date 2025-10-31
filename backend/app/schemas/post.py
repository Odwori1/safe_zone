from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Any, Dict
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
    """Post content types - EXTENDED for Phase 3"""
    TEXT = "text"
    JOURNAL = "journal"  # For private journal entries
    AUDIO = "audio"      # Phase 3: Audio posts
    VIDEO = "video"      # Phase 3: Video posts

class PostBase(BaseModel):
    """Base post schema - EXTENDED for audio and video support"""
    model_config = ConfigDict(from_attributes=True)

    content: str = Field(..., min_length=1, max_length=5000)
    content_type: PostContentType = PostContentType.TEXT
    mood: Optional[str] = Field(None, max_length=50)
    visibility: PostVisibility = PostVisibility.PUBLIC
    is_anonymous: bool = False

    # Phase 3: Audio-specific fields (OPTIONAL - only for audio posts)
    audio_url: Optional[str] = Field(None, max_length=500, description="URL to audio file")
    audio_duration: Optional[int] = Field(None, ge=1, le=3600, description="Audio duration in seconds")
    file_size: Optional[int] = Field(None, ge=1, description="File size in bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME type of the file")

    # Phase 3: Video-specific fields (OPTIONAL - only for video posts)
    video_url: Optional[str] = Field(None, max_length=500, description="URL to video file")
    video_duration: Optional[int] = Field(None, ge=1, le=3600, description="Video duration in seconds")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="URL to video thumbnail")
    video_width: Optional[int] = Field(None, ge=1, le=3840, description="Video width in pixels")
    video_height: Optional[int] = Field(None, ge=1, le=2160, description="Video height in pixels")

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

    @field_validator('audio_url')
    @classmethod
    def validate_audio_url(cls, v: Optional[str], info) -> Optional[str]:
        """Validate audio URL when content_type is AUDIO"""
        if info.data.get('content_type') == PostContentType.AUDIO and not v:
            raise ValueError('Audio URL is required for audio posts')
        return v

    @field_validator('video_url')
    @classmethod
    def validate_video_url(cls, v: Optional[str], info) -> Optional[str]:
        """Validate video URL when content_type is VIDEO"""
        if info.data.get('content_type') == PostContentType.VIDEO and not v:
            raise ValueError('Video URL is required for video posts')
        return v

class PostCreate(PostBase):
    """Schema for creating a post - EXTENDED for audio and video"""
    pass

class PostUpdate(BaseModel):
    """Schema for updating a post - EXTENDED for audio and video"""
    model_config = ConfigDict(from_attributes=True)

    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    mood: Optional[str] = Field(None, max_length=50)
    visibility: Optional[PostVisibility] = None
    status: Optional[PostStatus] = None

    # Phase 3: Audio-specific update fields
    audio_url: Optional[str] = Field(None, max_length=500)
    audio_duration: Optional[int] = Field(None, ge=1, le=3600)
    file_size: Optional[int] = Field(None, ge=1)
    mime_type: Optional[str] = Field(None, max_length=100)

    # Phase 3: Video-specific update fields
    video_url: Optional[str] = Field(None, max_length=500)
    video_duration: Optional[int] = Field(None, ge=1, le=3600)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    video_width: Optional[int] = Field(None, ge=1, le=3840)
    video_height: Optional[int] = Field(None, ge=1, le=2160)

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate content is not empty"""
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip() if v else v

class PostInDB(TimeStampedSchema):
    """Post schema as stored in database - EXTENDED for audio and video"""
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

    # Phase 3: Audio-specific fields
    audio_url: Optional[str] = None
    audio_duration: Optional[int] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    # Phase 3: Video-specific fields
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None

class PostResponse(PostInDB):
    """Post schema for API responses - EXTENDED for audio and video"""
    username: Optional[str] = None  # Only show if not anonymous
    user_avatar: Optional[str] = None

    like_count: int = 0
    user_has_liked: bool = False
    share_count: int = 0
    user_has_shared: bool = False

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

# ========== PHASE 3: NEW FILE UPLOAD SCHEMAS ==========

class FileUploadCreate(BaseModel):
    """Schema for creating a file upload record"""
    filename: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    file_url: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., ge=1)
    mime_type: str = Field(..., min_length=1, max_length=100)
    duration: Optional[int] = Field(None, ge=1, le=3600)



# ========== PHASE 3, ITEM 3: SECURE S3 FILE SCHEMAS ==========

class FileUploadRequest(BaseModel):
    """Schema for secure file upload request"""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_type: str = Field(..., description="File type: video, audio, or image")
    mime_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    duration: Optional[int] = Field(None, ge=1, le=3600, description="Duration in seconds for media files")
    width: Optional[int] = Field(None, ge=1, le=3840, description="Width in pixels for images/video")
    height: Optional[int] = Field(None, ge=1, le=2160, description="Height in pixels for images/video")

class FileUploadResponse(BaseModel):
    """Schema for secure file upload response"""
    upload_url: str = Field(..., description="Presigned URL for direct S3 upload")
    file_id: UUID = Field(..., description="ID of the file metadata record")
    s3_key: str = Field(..., description="Secure S3 key for the file")
    expires_in: int = Field(..., description="URL expiration time in seconds")

class FileAccessResponse(BaseModel):
    """Schema for secure file access response"""
    download_url: str = Field(..., description="Presigned URL for direct S3 download")
    file_type: str = Field(..., description="Type of file: video, audio, or image")
    expires_in: int = Field(..., description="URL expiration time in seconds")


class AudioUploadRequest(BaseModel):
    """Schema for audio upload request"""
    filename: str = Field(..., min_length=1, max_length=255, description="Name for the audio file")
    duration: Optional[int] = Field(None, ge=1, le=3600, description="Audio duration in seconds")

class AudioUploadResponse(BaseModel):
    """Schema for audio upload response"""
    upload_url: str = Field(..., description="URL for uploading the audio file")
    file_id: UUID = Field(..., description="ID of the file upload record")
    fields: Dict[str, str] = Field(..., description="Form fields for upload")
    url: str = Field(..., description="URL where the file will be accessible")

class VideoUploadRequest(BaseModel):
    """Schema for video upload request"""
    filename: str = Field(..., min_length=1, max_length=255, description="Name for the video file")
    duration: Optional[int] = Field(None, ge=1, le=3600, description="Video duration in seconds")
    width: Optional[int] = Field(None, ge=1, le=3840, description="Video width in pixels")
    height: Optional[int] = Field(None, ge=1, le=2160, description="Video height in pixels")

class VideoUploadResponse(BaseModel):
    """Schema for video upload response"""
    upload_url: str = Field(..., description="URL for uploading the video file")
    file_id: UUID = Field(..., description="ID of the file upload record")
    fields: Dict[str, str] = Field(..., description="Form fields for upload")
    url: str = Field(..., description="URL where the file will be accessible")
    thumbnail_url: Optional[str] = Field(None, description="URL for video thumbnail")
