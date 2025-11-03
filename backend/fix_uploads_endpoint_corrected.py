#!/usr/bin/env python3
"""
Temporarily modify uploads endpoint to work without S3 for development
"""
import os
import shutil  # Add the missing import

def fix_uploads_endpoint():
    print("🔧 CREATING DEVELOPMENT UPLOADS ENDPOINT")
    print("=" * 45)
    
    uploads_file = "app/api/endpoints/uploads.py"
    
    # Backup original file
    if os.path.exists(uploads_file):
        shutil.copy2(uploads_file, uploads_file + ".backup")
        print("✅ Backed up original uploads.py")
    
    # Create development version of uploads endpoint
    dev_uploads_code = '''from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.uploads import PresignedUrlRequest, PresignedUrlResponse
import uuid
import os
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def generate_presigned_url(
    request: PresignedUrlRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate presigned URL for file upload (Development Version)
    This version works without AWS S3 credentials
    """
    try:
        # Validate file type
        allowed_types = ["audio", "video", "image", "document"]
        if request.file_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type must be one of: {', '.join(allowed_types)}"
            )
        
        # Create unique file name
        file_ext = os.path.splitext(request.original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Determine upload directory
        upload_dirs = {
            "audio": "uploads/audio",
            "video": "uploads/video", 
            "image": "uploads/images",
            "document": "uploads/documents"
        }
        
        upload_dir = upload_dirs.get(request.file_type, "uploads/documents")
        
        # Ensure directory exists
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(upload_dir, unique_filename)
        
        # For development, we return a simple success response
        return {
            "presigned_url": f"http://localhost:8001/{file_path}",
            "file_key": file_path,
            "method": "PUT",
            "headers": {
                "Content-Type": request.mime_type
            },
            "expires_in": 3600,
            "upload_id": str(uuid.uuid4())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate upload URL: {str(e)}"
        )

@router.post("/complete")
async def complete_upload(
    upload_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark upload as complete (Development Version)
    """
    return {
        "status": "completed",
        "message": "Upload marked as complete",
        "file_url": upload_data.get("file_key", "")
    }
'''
    
    # Write the development uploads endpoint
    with open(uploads_file, "w") as f:
        f.write(dev_uploads_code)
    
    print("✅ Created development uploads endpoint")
    print("   This endpoint works without AWS S3 credentials")
    print("   Returns local file paths for development")

if __name__ == "__main__":
    fix_uploads_endpoint()
