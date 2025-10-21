# Read the current post.py schemas
with open('app/schemas/post.py', 'r') as f:
    content = f.read()

# Add new schemas for secure file metadata
new_schemas = '''

# ========== PHASE 3, ITEM 3: SECURE S3 FILE SCHEMAS ==========

class FileUploadRequest(BaseModel):
    """Schema for secure file upload request"""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_type: str = Field(..., description="File type: video, audio, or image")
    mime_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    duration: Optional[int] = Field(None, ge=1, le=3600, description="Duration in seconds for media files")
    width: Optional[int] = Field(None, ge=1, le=3840, description="Width in pixels for images/video")
    height: Optional[int] = Field(None, ge=1, le=2160, description="Height in pixels for images/video")

class FileUploadResponse(BaseModel):
    """Schema for secure file upload response"""
    upload_url: str = Field(..., description="Presigned URL for direct S3 upload")
    file_id: UUID = Field(..., description="ID of the file metadata record")
    s3_key: str = Field(..., description="Secure S3 key for the file")
    expires_in: int = Field(..., description="URL expiration time in seconds")

class FileAccessResponse(BaseModel):
    """Schema for secure file access response"""
    download_url: str = Field(..., description="Presigned URL for direct S3 download")
    file_type: str = Field(..., description="Type of file: video, audio, or image")
    expires_in: int = Field(..., description="URL expiration time in seconds")
'''

# Find where to insert the new schemas (after existing upload schemas)
insertion_point = '# ========== PHASE 3: NEW FILE UPLOAD SCHEMAS =========='
if insertion_point in content:
    # Insert after the existing upload schemas section
    parts = content.split(insertion_point)
    if len(parts) > 1:
        # Find the end of the existing upload schemas section
        existing_schemas_end = parts[1].find('\n\nclass', 100)  # Find next class after some content
        if existing_schemas_end != -1:
            new_content = (
                parts[0] + 
                insertion_point + 
                parts[1][:existing_schemas_end] + 
                '\n\n' + new_schemas + 
                parts[1][existing_schemas_end:]
            )
        else:
            new_content = content + '\n\n' + new_schemas
    else:
        new_content = content + '\n\n' + new_schemas
else:
    new_content = content + '\n\n' + new_schemas

# Write updated schemas
with open('app/schemas/post.py', 'w') as f:
    f.write(new_content)

print("✅ Updated schemas with secure S3 file schemas")
