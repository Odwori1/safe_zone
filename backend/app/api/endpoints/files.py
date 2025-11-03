"""
File Management Endpoints for Phase 3, Item 3
Following EXACT same patterns as other endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

from app.schemas.uploads import FileMetadataResponse
from app.crud.file_metadata import file_metadata_crud
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[FileMetadataResponse])
async def get_user_files(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get user's uploaded files
    SECURITY: RLS ensures user can only access their own files
    """
    try:
        files = await file_metadata_crud.get_by_user(current_user.id, limit, offset)
        return [
            FileMetadataResponse(
                id=file["id"],
                file_type=file["file_type"],
                original_filename=file["original_filename"],
                file_size=file["file_size"],
                mime_type=file["mime_type"],
                duration=file["duration"],
                upload_status=file["upload_status"],
                created_at=file["created_at"],
                url=f"/uploads/{file['s3_key'].split('/')[-1]}" if file["upload_status"] == "completed" else None
            )
            for file in files
        ]
    except Exception as e:
        logger.error(f"Error fetching user files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch files"
        )

@router.get("/{file_id}", response_model=FileMetadataResponse)
async def get_file_metadata(
    file_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get file metadata by ID
    SECURITY: RLS ensures user can only access their own files
    """
    try:
        file_record = await file_metadata_crud.get_by_id(file_id)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
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
            url=f"/uploads/{file_record['s3_key'].split('/')[-1]}" if file_record["upload_status"] == "completed" else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching file metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch file metadata"
        )

@router.get("/post/{post_id}", response_model=List[FileMetadataResponse])
async def get_post_files(
    post_id: UUID,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get files associated with a post
    SECURITY: RLS ensures user can only access their own posts' files
    """
    try:
        files = await file_metadata_crud.get_by_post(post_id, file_type)
        return [
            FileMetadataResponse(
                id=file["id"],
                file_type=file["file_type"],
                original_filename=file["original_filename"],
                file_size=file["file_size"],
                mime_type=file["mime_type"],
                duration=file["duration"],
                upload_status=file["upload_status"],
                created_at=file["created_at"],
                url=f"/uploads/{file['s3_key'].split('/')[-1]}" if file["upload_status"] == "completed" else None
            )
            for file in files
        ]
    except Exception as e:
        logger.error(f"Error fetching post files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch post files"
        )

@router.post("/{file_id}/associate/{post_id}")
async def associate_file_with_post(
    file_id: UUID,
    post_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Associate a file with a post
    SECURITY: RLS ensures user can only update their own files
    """
    try:
        success = await file_metadata_crud.associate_with_post(file_id, post_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        return {"message": "File associated with post successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error associating file with post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to associate file with post"
        )
