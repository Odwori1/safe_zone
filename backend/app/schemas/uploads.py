from pydantic import BaseModel, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class FileType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    DOCUMENT = "document"

class UploadStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class ModerationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PresignedUrlRequest(BaseModel):
    file_name: str
    file_type: FileType
    original_filename: str
    file_size: int
    mime_type: str
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        if v > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError('File size must be less than 50MB')
        return v

class PresignedUrlResponse(BaseModel):
    presigned_url: str
    file_key: str
    method: str
    headers: dict
    expires_in: int
    upload_id: str

class UploadCompleteRequest(BaseModel):
    upload_id: str
    file_key: str
    file_size: int

class FileMetadataResponse(BaseModel):
    id: str
    user_id: str
    s3_key: str
    file_type: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_status: UploadStatus
    moderation_status: ModerationStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FileMetadataList(BaseModel):
    files: List[FileMetadataResponse]
    total: int
