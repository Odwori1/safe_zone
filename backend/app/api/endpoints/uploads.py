from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional, Dict
from uuid import UUID, uuid4
import os
import shutil

from app.schemas.post import AudioUploadRequest, AudioUploadResponse, VideoUploadRequest, VideoUploadResponse, FileUploadResponse
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.post_audio import post_crud
from app.utils.file_upload import file_upload_handler

router = APIRouter()

@router.post("/audio/upload-url", response_model=AudioUploadResponse)
async def generate_audio_upload_url(
    upload_request: AudioUploadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a URL for uploading audio files
    Phase 3, Item 1: Audio Post Support
    """
    try:
        # For now, we'll use a simple approach with local file system
        # In Phase 3, Item 3 (S3 integration) this will be replaced with S3 presigned URLs

        # Generate upload data
        upload_data = await file_upload_handler.generate_upload_url(content_type='video', 
            user_id=str(current_user.id),
            filename=upload_request.filename,
            file_type="audio/mpeg",  # Default, can be made dynamic
            duration=upload_request.duration
        )

        # Create file upload record in database - FIXED: use dict access instead of object attributes
        file_upload_data = {
            "filename": upload_data["fields"]["filename"],
            "original_filename": upload_request.filename,
            "file_url": upload_data["url"],
            "file_size": 0,  # Will be updated after upload
            "mime_type": "audio/mpeg",
            "duration": upload_request.duration
        }

        file_record = await post_crud.create_file_upload_record(current_user.id, file_upload_data)

        return AudioUploadResponse(
            upload_url=upload_data["upload_url"],
            file_id=file_record["id"],
            fields=upload_data["fields"],
            url=upload_data["url"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating upload URL: {str(e)}"
        )

@router.put("/audio/{filename}")
async def upload_audio_file(
    filename: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload audio file to local storage
    Phase 3, Item 1: Audio Post Support
    Note: This will be replaced with S3 direct upload in Phase 3, Item 3
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only audio files are allowed"
            )

        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)

        # Secure filename
        safe_filename = f"{uuid4()}_{filename}"
        file_path = os.path.join("uploads", safe_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file size
        file_size = os.path.getsize(file_path)

        # Validate file
        await file_upload_handler.validate_audio_file(
            file_path, file.content_type, file_size
        )

        # Return file info
        return {
            "filename": safe_filename,
            "original_filename": filename,
            "file_url": f"/uploads/{safe_filename}",
            "file_size": file_size,
            "mime_type": file.content_type,
            "message": "File uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )
    finally:
        await file.close()

@router.get("/files", response_model=list[FileUploadResponse])
async def get_user_file_uploads(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's file uploads
    Phase 3, Item 1: Audio Post Support
    """
    try:
        uploads = await post_crud.get_user_file_uploads(current_user.id)
        return [FileUploadResponse(**dict(upload)) for upload in uploads]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving file uploads: {str(e)}"
        )

@router.post("/video/upload-url", response_model=VideoUploadResponse)
async def generate_video_upload_url(
    upload_request: VideoUploadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a URL for uploading video files
    Phase 3, Item 2: Video Post Support
    """
    try:
        # For now, we'll use a simple approach with local file system
        # In Phase 3, Item 3 (S3 integration) this will be replaced with S3 presigned URLs

        # Generate upload data
        upload_data = await file_upload_handler.generate_upload_url(content_type='video', 
            user_id=str(current_user.id),
            filename=upload_request.filename,
            file_type="video/mp4",  # Default, can be made dynamic
            duration=upload_request.duration
        )

        # Create file upload record in database
        file_upload_data = {
            "filename": upload_data["fields"]["filename"],
            "original_filename": upload_request.filename,
            "file_url": upload_data["url"],
            "file_size": 0,  # Will be updated after upload
            "mime_type": "video/mp4",
            "duration": upload_request.duration
        }

        file_record = await post_crud.create_file_upload_record(current_user.id, file_upload_data)

        return VideoUploadResponse(
            upload_url=upload_data["upload_url"],
            file_id=file_record["id"],
            fields=upload_data["fields"],
            url=upload_data["url"],
            thumbnail_url=None  # Would be generated in production
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating upload URL: {str(e)}"
        )

@router.put("/video/{filename}")
async def upload_video_file(
    filename: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload video file to local storage
    Phase 3, Item 2: Video Post Support
    Note: This will be replaced with S3 direct upload in Phase 3, Item 3
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only video files are allowed"
            )

        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)

        # Secure filename
        safe_filename = f"{uuid4()}_{filename}"
        file_path = os.path.join("uploads", safe_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file size
        file_size = os.path.getsize(file_path)

        # For now, skip video-specific validation
        # Return file info
        return {
            "filename": safe_filename,
            "original_filename": filename,
            "file_url": f"/uploads/{safe_filename}",
            "file_size": file_size,
            "mime_type": file.content_type,
            "message": "File uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )
    finally:
        await file.close()
