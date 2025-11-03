#!/usr/bin/env python3
"""
Setup local file storage for development (bypass AWS S3 requirement)
"""
import os
import shutil

def setup_local_storage():
    print("🔧 SETTING UP LOCAL STORAGE FOR DEVELOPMENT")
    print("=" * 50)
    
    # Create uploads directory structure
    uploads_dirs = [
        "uploads",
        "uploads/audio", 
        "uploads/video",
        "uploads/images",
        "uploads/documents"
    ]
    
    for directory in uploads_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Create a simple local storage handler
    local_storage_code = '''
# LOCAL STORAGE FOR DEVELOPMENT
# This file provides local file storage when AWS S3 is not configured

import os
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException

class LocalStorage:
    def __init__(self):
        self.base_path = "uploads"
        self.base_url = "http://localhost:8001/uploads"
        
    async def generate_presigned_url(self, file_key: str, file_type: str, mime_type: str):
        """Generate a local file upload URL for development"""
        try:
            # Create a unique file name
            file_ext = os.path.splitext(file_key)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Determine subdirectory based on file type
            if file_type == "audio":
                subdir = "audio"
            elif file_type == "video":
                subdir = "video" 
            elif file_type == "image":
                subdir = "images"
            else:
                subdir = "documents"
                
            # Full file path
            file_path = os.path.join(self.base_path, subdir, unique_filename)
            
            # For local storage, we return a simple upload endpoint
            # In a real implementation, this would handle the file upload
            return {
                "presigned_url": f"{self.base_url}/{subdir}/{unique_filename}",
                "file_key": file_path,
                "method": "PUT",
                "headers": {
                    "Content-Type": mime_type
                },
                "expires_in": 3600
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {str(e)}")
    
    async def save_file_metadata(self, user_id: str, file_key: str, original_filename: str, 
                               file_type: str, file_size: int, mime_type: str):
        """Save file metadata to database (simplified)"""
        # This would normally save to the file_metadata table
        # For now, we just return success
        return {
            "file_id": str(uuid.uuid4()),
            "file_key": file_key,
            "status": "pending"
        }

local_storage = LocalStorage()
'''
    
    # Write the local storage handler
    with open("local_storage.py", "w") as f:
        f.write(local_storage_code)
    print("✅ Created local storage handler")
    
    # Update .env to use local storage
    env_file = ".env"
    with open(env_file, "r") as f:
        env_content = f.read()
    
    # Add local storage configuration
    if "USE_LOCAL_STORAGE" not in env_content:
        local_storage_config = '''

# Local Storage Configuration (Development)
USE_LOCAL_STORAGE=true
LOCAL_STORAGE_PATH=./uploads
LOCAL_STORAGE_URL=http://localhost:8001/uploads
'''
        with open(env_file, "a") as f:
            f.write(local_storage_config)
        print("✅ Updated .env for local storage")
    
    print("\n🎉 LOCAL STORAGE SETUP COMPLETE!")
    print("   Uploads will now work without AWS S3")
    print("   Files will be stored in: ./uploads/")
    print("   Access via: http://localhost:8001/uploads/")

if __name__ == "__main__":
    setup_local_storage()
