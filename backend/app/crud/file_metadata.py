"""
Secure CRUD operations for file_metadata table
Following security-first blueprint with RLS protection
"""

import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database

class FileMetadataCRUD:
    """
    Secure CRUD operations for file metadata
    All operations are protected by RLS
    """
    
    async def create(
        self, 
        user_id: UUID, 
        post_id: Optional[UUID], 
        file_data: dict
    ) -> Optional[asyncpg.Record]:
        """
        Create secure file metadata record
        RLS ensures user can only create their own records
        """
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO file_metadata 
                (user_id, post_id, s3_key, file_type, original_filename, 
                 file_size, mime_type, duration, upload_status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                """,
                user_id, post_id, file_data["s3_key"], file_data["file_type"],
                file_data["original_filename"], file_data["file_size"],
                file_data["mime_type"], file_data.get("duration"), "pending"
            )
    
    async def get_by_id(self, file_id: UUID) -> Optional[asyncpg.Record]:
        """
        Get file metadata by ID
        RLS ensures user can only access their own files
        """
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM file_metadata WHERE id = $1",
                file_id
            )
    
    async def get_by_user(
        self, 
        user_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[asyncpg.Record]:
        """
        Get user's file metadata
        RLS ensures user can only access their own files
        """
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT * FROM file_metadata 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )
    
    async def get_by_post(
        self, 
        post_id: UUID, 
        file_type: Optional[str] = None
    ) -> List[asyncpg.Record]:
        """
        Get file metadata for a post
        RLS ensures user can only access their own posts' files
        """
        async with database.pool.acquire() as conn:
            if file_type:
                return await conn.fetch(
                    """
                    SELECT * FROM file_metadata 
                    WHERE post_id = $1 AND file_type = $2
                    ORDER BY created_at DESC
                    """,
                    post_id, file_type
                )
            else:
                return await conn.fetch(
                    """
                    SELECT * FROM file_metadata 
                    WHERE post_id = $1
                    ORDER BY created_at DESC
                    """,
                    post_id
                )
    
    async def update_upload_status(
        self, 
        file_id: UUID, 
        status: str
    ) -> bool:
        """
        Update file upload status
        RLS ensures user can only update their own files
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE file_metadata SET upload_status = $1 WHERE id = $2",
                status, file_id
            )
            return "UPDATE 1" in result
    
    async def update_moderation_status(
        self, 
        file_id: UUID, 
        status: str
    ) -> bool:
        """
        Update file moderation status
        RLS ensures user can only update their own files
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE file_metadata SET moderation_status = $1 WHERE id = $2",
                status, file_id
            )
            return "UPDATE 1" in result
    
    async def associate_with_post(
        self, 
        file_id: UUID, 
        post_id: UUID
    ) -> bool:
        """
        Associate file with a post
        RLS ensures user can only update their own files
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE file_metadata SET post_id = $1 WHERE id = $2",
                post_id, file_id
            )
            return "UPDATE 1" in result
    
    async def delete(self, file_id: UUID) -> bool:
        """
        Delete file metadata (soft delete via status)
        RLS ensures user can only delete their own files
        """
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE file_metadata SET upload_status = 'failed' WHERE id = $1",
                file_id
            )
            return "UPDATE 1" in result

# Global file metadata CRUD instance
file_metadata_crud = FileMetadataCRUD()
