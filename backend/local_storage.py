
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
