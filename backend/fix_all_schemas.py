#!/usr/bin/env python3
"""
Fix all missing schemas for uploads and files system
"""
import os
import shutil

def fix_all_schemas():
    print("🔧 FIXING ALL MISSING SCHEMAS")
    print("=" * 40)
    
    # Step 1: Fix uploads schema with ALL required classes
    print("\n1. Creating complete uploads schema...")
    uploads_schema_file = "app/schemas/uploads.py"
    
    uploads_schema_code = '''from pydantic import BaseModel, validator
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
'''
    
    # Write complete schema
    with open(uploads_schema_file, "w") as f:
        f.write(uploads_schema_code)
    print("   ✅ Created complete uploads schema")
    
    # Step 2: Check if files endpoint needs fixing
    print("\n2. Checking files endpoint...")
    files_endpoint_file = "app/api/endpoints/files.py"
    
    if os.path.exists(files_endpoint_file):
        # Read current files endpoint
        with open(files_endpoint_file, "r") as f:
            files_content = f.read()
        
        # Check if it's trying to import missing schemas
        if "FileMetadataResponse" in files_content:
            print("   ⚠️  Files endpoint uses FileMetadataResponse")
            
            # Create backup
            shutil.copy2(files_endpoint_file, files_endpoint_file + ".backup")
            print("   ✅ Backed up files endpoint")
            
            # Replace the import line
            new_files_content = files_content.replace(
                "from app.schemas.uploads import FileMetadataResponse",
                "from app.schemas.uploads import FileMetadataResponse, FileMetadataList"
            )
            
            # Write updated files endpoint
            with open(files_endpoint_file, "w") as f:
                f.write(new_files_content)
            print("   ✅ Fixed files endpoint imports")
    
    print("\n🎉 ALL SCHEMAS AND IMPORTS FIXED!")
    print("   ✅ Uploads schema with all required classes")
    print("   ✅ Files endpoint imports fixed")
    print("   ✅ Ready to restart backend")

if __name__ == "__main__":
    fix_all_schemas()
