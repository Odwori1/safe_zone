from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.core.security import get_current_user
from app.schemas.uploads import PresignedUrlRequest, PresignedUrlResponse, UploadCompleteRequest
import uuid
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

# Create upload directories
UPLOAD_BASE_DIR = Path("uploads")
UPLOAD_BASE_DIR.mkdir(exist_ok=True)
(UPLOAD_BASE_DIR / "images").mkdir(exist_ok=True)
(UPLOAD_BASE_DIR / "audio").mkdir(exist_ok=True)
(UPLOAD_BASE_DIR / "video").mkdir(exist_ok=True)
(UPLOAD_BASE_DIR / "documents").mkdir(exist_ok=True)

@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def generate_presigned_url(
    request: PresignedUrlRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate presigned URL for file upload - FIXED VERSION
    Now returns proper API endpoint for file upload
    """
    try:
        # Create unique file name
        file_ext = os.path.splitext(request.original_filename)[1] or '.bin'
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Determine file type for directory
        upload_dirs = {
            "audio": "audio",
            "video": "video", 
            "image": "images",
            "document": "documents"
        }

        file_type = upload_dirs.get(request.file_type, "documents")

        # Return API endpoint for file upload (not direct file path)
        return PresignedUrlResponse(
            presigned_url=f"/api/v1/uploads/files/{file_type}/{unique_filename}",
            file_key=f"uploads/{file_type}/{unique_filename}",
            method="POST",  # Changed to POST for FormData upload
            headers={
                "Content-Type": request.mime_type
            },
            expires_in=3600,
            upload_id=str(uuid.uuid4())
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload URL: {str(e)}"
        )

@router.post("/files/{file_type}/{filename}")
async def upload_file_direct(
    file_type: str,
    filename: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Handle direct file upload - FIXED VERSION
    This is the endpoint that the presigned URL points to
    """
    try:
        # Validate file type
        valid_file_types = ["images", "audio", "video", "documents"]
        if file_type not in valid_file_types:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Ensure directory exists
        upload_dir = UPLOAD_BASE_DIR / file_type
        upload_dir.mkdir(exist_ok=True)

        # Create full file path
        file_path = upload_dir / filename

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return file access URL
        file_access_url = f"/api/v1/uploads/files/{file_type}/{filename}"

        return {
            "message": "File uploaded successfully",
            "file_url": file_access_url,
            "file_path": str(file_path),
            "filename": filename,
            "file_type": file_type,
            "size": file_path.stat().st_size if file_path.exists() else 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/files/{file_type}/{filename}")
async def serve_uploaded_file(file_type: str, filename: str):
    """
    Serve uploaded files - FIXED VERSION
    """
    try:
        file_path = UPLOAD_BASE_DIR / file_type / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine content type based on file extension
        file_extension = Path(filename).suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo'
        }

        media_type = content_types.get(file_extension, 'application/octet-stream')

        return FileResponse(file_path, media_type=media_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File serving failed: {str(e)}")

@router.post("/complete")
async def complete_upload(
    request: UploadCompleteRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark upload as complete
    """
    return {
        "status": "completed",
        "message": "Upload marked as complete",
        "file_url": request.file_key
    }

@router.get("/files")
async def list_uploaded_files(
    current_user: dict = Depends(get_current_user)
):
    """
    List uploaded files for current user
    """
    # This would typically query a database for user's files
    # For now, return empty list
    return {
        "files": [],
        "total": 0
    }
