"""
Secure File Upload Endpoints for Phase 3, Item 3
Following EXACT same patterns as other endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

from app.schemas.uploads import (
    FileUploadCreate, FileUpload, PresignedURLResponse,
    UploadCompleteRequest, FileMetadataResponse
)
from app.crud.file_metadata import file_metadata_crud
from app.core.security import get_current_user
from app.schemas.user import User
from app.utils.file_upload import file_upload_handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/presigned-url", response_model=PresignedURLResponse)
async def generate_upload_url(
    file_data: FileUploadCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Generate upload URL for file upload
    SECURITY: RLS ensures user can only create their own uploads
    """
    try:
        # Validate file type using the existing handler
        if file_data.file_type == 'audio':
            content_type = 'audio'
            if not file_upload_handler._is_valid_audio_type(file_data.mime_type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid audio file type"
                )
        elif file_data.file_type == 'video':
            content_type = 'video'
            if not file_upload_handler._is_valid_video_type(file_data.mime_type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid video file type"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type must be audio or video"
            )

        # Validate file size
        if file_data.file_type == 'audio' and file_data.file_size > file_upload_handler.max_audio_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio file too large. Maximum size: {file_upload_handler.max_audio_size} bytes"
            )
        elif file_data.file_type == 'video' and file_data.file_size > file_upload_handler.max_video_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Video file too large. Maximum size: {file_upload_handler.max_video_size} bytes"
            )

        # Create file metadata record
        file_metadata = {
            "s3_key": f"uploads/{current_user.id}/{file_data.original_filename}",
            "file_type": file_data.file_type,
            "original_filename": file_data.original_filename,
            "file_size": file_data.file_size,
            "mime_type": file_data.mime_type,
            "duration": file_data.duration
        }

        file_record = await file_metadata_crud.create(
            current_user.id, None, file_metadata
        )

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create upload record"
            )

        # Generate upload URL using existing handler
        upload_data = await file_upload_handler.generate_upload_url(
            str(current_user.id),
            file_data.original_filename,
            file_data.mime_type,
            file_data.duration,
            content_type
        )

        return PresignedURLResponse(
            upload_id=file_record["id"],
            presigned_url=upload_data["upload_url"],
            s3_key=file_record["s3_key"],
            expires_in=3600  # 1 hour
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating upload URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )

@router.post("/complete", response_model=FileMetadataResponse)
async def complete_upload(
    completion_data: UploadCompleteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Mark upload as completed
    SECURITY: RLS ensures user can only update their own uploads
    """
    try:
        if completion_data.success:
            success = await file_metadata_crud.update_upload_status(
                completion_data.upload_id, "completed"
            )
        else:
            success = await file_metadata_crud.update_upload_status(
                completion_data.upload_id, "failed"
            )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload record not found"
            )

        # Get updated file metadata
        file_record = await file_metadata_crud.get_by_id(completion_data.upload_id)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload record not found"
            )

        return FileMetadataResponse(
            id=file_record["id"],
            file_type=file_record["file_type"],
            original_filename=file_record["original_filename"],
            file_size=file_record["file_size"],
            mime_type=file_record["mime_type"],
            duration=file_record["duration"],
            upload_status=file_record["upload_status"],
            created_at=file_record["created_at"],
            url=f"/uploads/{file_record['s3_key'].split('/')[-1]}"  # Use local URL for now
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete upload"
        )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file (soft delete)
    SECURITY: RLS ensures user can only delete their own files
    """
    try:
        success = await file_metadata_crud.delete(file_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
