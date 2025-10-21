"""
Secure File Endpoints for Phase 3, Item 3 - UPDATED
Using secure file_metadata table with RLS protection
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID

from app.schemas.post import FileUploadRequest, FileUploadResponse, FileAccessResponse
from app.schemas.user import User
from app.core.security import get_current_user
from app.crud.file_metadata import file_metadata_crud
from app.services.s3_service import s3_service
from app.services.file_validation import file_validation
from app.crud.post_audio import post_crud  # For post verification

router = APIRouter()

@router.post("/posts/{post_id}/presigned-upload", response_model=FileUploadResponse)
async def generate_presigned_upload(
    post_id: UUID,
    upload_request: FileUploadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate presigned URL for secure file upload to S3
    SECURITY: Application never handles file bytes
    """
    try:
        # 1. VERIFY USER OWNS POST (RLS ENFORCED)
        post = await post_crud.get(post_id)
        if not post or post['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or access denied"
            )
        
        # 2. VALIDATE FILE UPLOAD REQUEST (SECURITY FIRST)
        await file_validation.validate_upload_request(
            file_type=upload_request.file_type,
            mime_type=upload_request.mime_type,
            file_size=upload_request.file_size,
            duration=upload_request.duration
        )
        
        # 3. GENERATE SECURE S3 KEY WITH USER ISOLATION
        s3_key = s3_service.generate_secure_s3_key(
            user_id=str(current_user.id),
            post_id=str(post_id),
            file_type=upload_request.file_type,
            filename=upload_request.filename
        )
        
        # 4. CREATE SECURE FILE METADATA RECORD (RLS PROTECTED)
        file_data = {
            "s3_key": s3_key,
            "file_type": upload_request.file_type,
            "original_filename": upload_request.filename,
            "file_size": upload_request.file_size,
            "mime_type": upload_request.mime_type,
            "duration": upload_request.duration
        }
        
        file_record = await file_metadata_crud.create(
            current_user.id, post_id, file_data
        )
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file metadata record"
            )
        
        # 5. GENERATE PRESIGNED UPLOAD URL
        presigned_url = await s3_service.generate_presigned_upload(
            s3_key=s3_key,
            mime_type=upload_request.mime_type,
            file_size=upload_request.file_size
        )
        
        return FileUploadResponse(
            upload_url=presigned_url,
            file_id=file_record["id"],
            s3_key=s3_key,
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating upload URL: {str(e)}"
        )

@router.post("/{file_id}/confirm-upload")
async def confirm_upload(
    file_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Confirm successful file upload to S3
    RLS ensures user can only update their own files
    """
    try:
        # Verify file exists and belongs to user (RLS enforced)
        file_record = await file_metadata_crud.get_by_id(file_id)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        
        # Update upload status to completed
        success = await file_metadata_crud.update_upload_status(file_id, "completed")
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to confirm upload"
            )
        
        # TODO: Trigger async processing (transcoding, moderation, etc.)
        # await process_file_upload.delay(file_id)
        
        return {"status": "upload_confirmed", "file_id": str(file_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirming upload: {str(e)}"
        )

@router.get("/{file_id}/presigned-url", response_model=FileAccessResponse)
async def get_presigned_download(
    file_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Generate presigned URL for secure file download from S3
    SECURITY: Application never serves files directly
    """
    try:
        # RLS ensures user can only access their own files
        file_record = await file_metadata_crud.get_by_id(file_id)
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        
        # Check if upload is completed
        if file_record['upload_status'] != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File upload not completed"
            )
        
        # Generate presigned download URL
        presigned_url = await s3_service.generate_presigned_download(
            file_record['s3_key']
        )
        
        return FileAccessResponse(
            download_url=presigned_url,
            file_type=file_record['file_type'],
            expires_in=900
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating download URL: {str(e)}"
        )

@router.get("/posts/{post_id}/files")
async def get_post_files(
    post_id: UUID,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get files associated with a post
    RLS ensures user can only access their own posts' files
    """
    try:
        # Verify user owns the post (RLS enforced)
        post = await post_crud.get(post_id)
        if not post or post['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or access denied"
            )
        
        # Get files for the post
        files = await file_metadata_crud.get_by_post(post_id, file_type)
        
        return {
            "post_id": str(post_id),
            "files": [
                {
                    "id": str(file["id"]),
                    "file_type": file["file_type"],
                    "original_filename": file["original_filename"],
                    "file_size": file["file_size"],
                    "upload_status": file["upload_status"],
                    "created_at": file["created_at"].isoformat() if file["created_at"] else None
                }
                for file in files
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving post files: {str(e)}"
        )
