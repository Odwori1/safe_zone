"""
File upload utilities for Phase 3: Media Support
Following the existing architecture patterns
"""

import uuid
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("safe_zone.file_upload")

"""
File upload utilities for Phase 3: Media Support
Following the existing architecture patterns
"""

import uuid
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("safe_zone.file_upload")

class FileUploadHandler:
    """
    Handler for file uploads - currently local storage
    Can be extended to S3 in future iterations
    """

    def __init__(self):
        self.upload_dir = "uploads"
        
        # UPDATED: Added video MIME types
        self.allowed_audio_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg',
            'audio/x-m4a', 'audio/aac', 'audio/webm'
        ]
        
        self.allowed_video_types = [
            'video/mp4', 'video/mpeg', 'video/ogg', 'video/webm',
            'video/x-msvideo', 'video/quicktime', 'video/x-matroska'
        ]
        
        self.max_audio_size = 50 * 1024 * 1024  # 50MB
        self.max_video_size = 100 * 1024 * 1024  # 100MB for video
        self.max_duration = 10 * 60  # 10 minutes

    async def generate_upload_url(self, user_id: str, filename: str,
                                file_type: str, duration: Optional[int] = None,
                                content_type: str = 'audio') -> Dict[str, Any]:
        """
        Generate upload URL and metadata for file upload
        UPDATED: Added content_type parameter to distinguish audio/video
        """
        try:
            # Validate file type based on content_type
            if content_type == 'audio':
                if not self._is_valid_audio_type(file_type):
                    raise ValueError(f"Unsupported audio file type: {file_type}")
                max_size = self.max_audio_size
            elif content_type == 'video':
                if not self._is_valid_video_type(file_type):
                    raise ValueError(f"Unsupported video file type: {file_type}")
                max_size = self.max_video_size
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            # Generate unique filename
            file_ext = self._get_file_extension(filename, file_type, content_type)
            unique_filename = f"{uuid.uuid4()}{file_ext}"

            # Create upload directory if it doesn't exist
            os.makedirs(self.upload_dir, exist_ok=True)

            # Local file path (will be replaced with S3 URL in future)
            file_path = os.path.join(self.upload_dir, unique_filename)
            file_url = f"/{self.upload_dir}/{unique_filename}"

            # For now, we'll use local file system
            upload_data = {
                "upload_url": f"/api/v1/uploads/{unique_filename}",
                "file_id": str(uuid.uuid4()),
                "fields": {
                    "filename": unique_filename,
                    "file_path": file_path
                },
                "url": file_url,
                "method": "PUT",
                "max_size": max_size
            }

            logger.info(f"Generated upload URL for user {user_id}: {unique_filename} ({content_type})")
            return upload_data

        except Exception as e:
            logger.error(f"Error generating upload URL: {e}")
            raise

    async def validate_media_file(self, file_path: str, mime_type: str,
                                file_size: int, content_type: str = 'audio',
                                duration: Optional[int] = None) -> bool:
        """
        Validate media file constraints
        UPDATED: Added content_type parameter
        """
        try:
            # Check file size based on content type
            if content_type == 'audio':
                max_size = self.max_audio_size
                if not self._is_valid_audio_type(mime_type):
                    raise ValueError(f"Invalid audio type: {mime_type}")
            elif content_type == 'video':
                max_size = self.max_video_size
                if not self._is_valid_video_type(mime_type):
                    raise ValueError(f"Invalid video type: {mime_type}")
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} bytes. Maximum: {max_size}")

            # Check duration if provided
            if duration and duration > self.max_duration:
                raise ValueError(f"Media too long: {duration} seconds. Maximum: {self.max_duration}")

            return True

        except Exception as e:
            logger.error(f"Media file validation failed: {e}")
            raise

    def _is_valid_audio_type(self, mime_type: str) -> bool:
        """Check if MIME type is supported for audio"""
        return mime_type.lower() in self.allowed_audio_types

    def _is_valid_video_type(self, mime_type: str) -> bool:
        """Check if MIME type is supported for video"""
        return mime_type.lower() in self.allowed_video_types

    def _get_file_extension(self, filename: str, mime_type: str, content_type: str = 'audio') -> str:
        """Get appropriate file extension based on MIME type and content type"""
        if content_type == 'audio':
            extension_map = {
                'audio/mpeg': '.mp3',
                'audio/mp3': '.mp3',
                'audio/wav': '.wav',
                'audio/ogg': '.ogg',
                'audio/x-m4a': '.m4a',
                'audio/aac': '.aac',
                'audio/webm': '.webm'
            }
        else:  # video
            extension_map = {
                'video/mp4': '.mp4',
                'video/mpeg': '.mpeg',
                'video/ogg': '.ogv',
                'video/webm': '.webm',
                'video/x-msvideo': '.avi',
                'video/quicktime': '.mov',
                'video/x-matroska': '.mkv'
            }

        # Try to get extension from MIME type first
        extension = extension_map.get(mime_type.lower())

        # Fallback to original filename extension
        if not extension:
            _, extension = os.path.splitext(filename)
            if not extension:
                extension = '.mp4' if content_type == 'video' else '.audio'

        return extension

    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract basic file metadata
        """
        try:
            file_stats = os.stat(file_path)
            return {
                "file_size": file_stats.st_size,
                "created_at": datetime.fromtimestamp(file_stats.st_ctime),
                "modified_at": datetime.fromtimestamp(file_stats.st_mtime)
            }
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}")
            return {}

    async def cleanup_orphaned_files(self, older_than_hours: int = 24):
        """
        Clean up orphaned files that were uploaded but never associated with a post
        """
        try:
            # This would be implemented to clean up files without associated posts
            # For now, it's a placeholder for future implementation
            logger.info("File cleanup would run here in production")
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")

# Global file upload handler instance
file_upload_handler = FileUploadHandler()

