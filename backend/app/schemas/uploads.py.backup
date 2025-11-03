"""
Upload Schemas for Phase 3, Item 3
Following EXACT same patterns as other schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class FileUploadBase(BaseModel):
    """Base schema for file uploads"""
    file_type: str  # audio, video, image, document
    original_filename: str
    file_size: int
    mime_type: str
    duration: Optional[int] = None  # For audio/video files

    @validator('file_type')
    def validate_file_type(cls, v):
        if v not in ['audio', 'video', 'image', 'document']:
            raise ValueError('File type must be audio, video, image, or document')
        return v

    @validator('file_size')
    def validate_file_size(cls, v):
        if v < 1 or v > 500 * 1024 * 1024:  # 500MB max
            raise ValueError('File size must be between 1 byte and 500MB')
        return v

class FileUploadCreate(FileUploadBase):
    """Schema for creating a file upload"""
    pass

class FileUpload(FileUploadBase):
    """Schema for file upload response"""
    id: UUID
    user_id: UUID
    post_id: Optional[UUID]
    s3_key: str
    upload_status: str  # pending, uploading, completed, failed
    moderation_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PresignedURLResponse(BaseModel):
    """Schema for presigned URL response"""
    upload_id: UUID
    presigned_url: str
    s3_key: str
    expires_in: int

class UploadCompleteRequest(BaseModel):
    """Schema for upload completion request"""
    upload_id: UUID
    success: bool
    error_message: Optional[str] = None

class FileMetadataResponse(BaseModel):
    """Schema for file metadata response"""
    id: UUID
    file_type: str
    original_filename: str
    file_size: int
    mime_type: str
    duration: Optional[int]
    upload_status: str
    created_at: datetime
    url: Optional[str] = None  # CDN URL for accessing the file
