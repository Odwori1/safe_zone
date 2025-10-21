"""
Secure S3 Service for Phase 3, Item 3
Following the security-first blueprint with presigned URLs only
"""

import boto3
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger("safe_zone.s3_service")

class S3Service:
    """
    Secure S3 service that only generates presigned URLs
    Application NEVER handles file bytes - zero-trust principle
    """
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket = settings.s3_bucket
        self.presigned_expiry = settings.s3_presigned_expiry
    
    async def generate_presigned_upload(
        self, 
        s3_key: str, 
        mime_type: str, 
        file_size: int
    ) -> str:
        """
        Generate presigned URL for client direct upload to S3
        Application never touches file bytes - security first
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key,
                    'ContentType': mime_type,
                    'ContentLength': file_size,
                    # Security: Add checksum validation in production
                },
                ExpiresIn=self.presigned_expiry
            )
            
            logger.info(f"Generated presigned upload URL for {s3_key}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Error generating presigned upload URL: {e}")
            raise
    
    async def generate_presigned_download(self, s3_key: str) -> str:
        """
        Generate presigned URL for client direct download from S3
        Application never serves files directly
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key,
                },
                ExpiresIn=900  # 15 minutes for downloads
            )
            
            logger.info(f"Generated presigned download URL for {s3_key}")
            return presigned_url
            
        except Exception as e:
            logger.error(f"Error generating presigned download URL: {e}")
            raise
    
    def generate_secure_s3_key(
        self, 
        user_id: str, 
        post_id: str, 
        file_type: str, 
        filename: str
    ) -> str:
        """
        Generate secure S3 key with user isolation
        Format: users/{user_id}/posts/{post_id}/{file_type}s/{uuid}.ext
        """
        import uuid
        from pathlib import Path
        
        # Validate file type
        if file_type not in ['video', 'audio', 'image']:
            raise ValueError(f"Invalid file type: {file_type}")
        
        # Get file extension
        file_ext = Path(filename).suffix.lower()
        if not file_ext:
            file_ext = '.mp4' if file_type == 'video' else '.mp3'
        
        # Generate secure key with user isolation
        unique_id = uuid.uuid4()
        s3_key = f"users/{user_id}/posts/{post_id}/{file_type}s/{unique_id}{file_ext}"
        
        return s3_key

# Global S3 service instance
s3_service = S3Service()
