"""
File Validation Service for Phase 3, Item 3
Security-first file validation before generating presigned URLs
"""

from typing import Dict, Any
import logging

logger = logging.getLogger("safe_zone.file_validation")

class FileValidationService:
    """
    Validates file upload requests before generating presigned URLs
    Security: Validate before allowing any upload
    """
    
    # Allowed file types - security restricted
    ALLOWED_VIDEO_TYPES = [
        'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'
    ]
    
    ALLOWED_AUDIO_TYPES = [
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/x-m4a', 'audio/aac'
    ]
    
    ALLOWED_IMAGE_TYPES = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp'
    ]
    
    # Security: Size limits
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB
    MAX_IMAGE_SIZE = 20 * 1024 * 1024   # 20MB
    
    def __init__(self):
        self.type_limits = {
            'video': {'types': self.ALLOWED_VIDEO_TYPES, 'max_size': self.MAX_VIDEO_SIZE},
            'audio': {'types': self.ALLOWED_AUDIO_TYPES, 'max_size': self.MAX_AUDIO_SIZE},
            'image': {'types': self.ALLOWED_IMAGE_TYPES, 'max_size': self.MAX_IMAGE_SIZE},
        }
    
    async def validate_upload_request(
        self, 
        file_type: str, 
        mime_type: str, 
        file_size: int,
        duration: int = None
    ) -> bool:
        """
        Validate file upload request against security constraints
        """
        try:
            # Validate file type exists
            if file_type not in self.type_limits:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            limits = self.type_limits[file_type]
            
            # Validate MIME type
            if mime_type not in limits['types']:
                raise ValueError(f"Unsupported {file_type} format: {mime_type}")
            
            # Validate file size
            if file_size > limits['max_size']:
                raise ValueError(
                    f"{file_type.capitalize()} file too large: {file_size} bytes. "
                    f"Maximum: {limits['max_size']} bytes"
                )
            
            # Validate duration for media files
            if file_type in ['video', 'audio'] and duration:
                if duration > 3600:  # 1 hour max
                    raise ValueError(f"{file_type.capitalize()} too long: {duration} seconds")
                if duration < 1:
                    raise ValueError(f"{file_type.capitalize()} duration must be positive")
            
            logger.info(f"File validation passed: {file_type}, {mime_type}, {file_size} bytes")
            return True
            
        except Exception as e:
            logger.error(f"File validation failed: {e}")
            raise

# Global file validation service instance
file_validation = FileValidationService()
