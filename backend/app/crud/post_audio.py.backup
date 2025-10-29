import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database

class CRUDPost:
    async def get(self, post_id: UUID) -> Optional[asyncpg.Record]:
        """Get post by ID - UPDATED for audio support"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM posts WHERE id = $1 AND status != 'deleted'",
                post_id
            )

    async def get_by_user(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get posts by user ID - UPDATED for audio support"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT p.*, u.username, u.profile_picture as user_avatar
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                WHERE p.user_id = $1 AND p.status != 'deleted'
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

    async def get_feed(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[asyncpg.Record]:
        """Get post feed for user - UPDATED for audio support"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT p.*,
                       CASE WHEN p.is_anonymous THEN NULL ELSE u.username END as username,
                       CASE WHEN p.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                WHERE p.status = 'active'
                AND p.moderation_status = 'approved'
                AND (p.visibility = 'public' OR p.user_id = $1)
                AND u.is_active = true
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

    async def create(self, user_id: UUID, post_in) -> asyncpg.Record:
        """Create new post - UPDATED for audio support"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                 audio_url, audio_duration, file_size, mime_type)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
                """,
                user_id, post_in.content, post_in.content_type, post_in.mood,
                post_in.visibility, post_in.is_anonymous,
                post_in.audio_url, post_in.audio_duration, post_in.file_size, post_in.mime_type
            )

    async def update(self, post_id: UUID, user_id: UUID, post_in) -> Optional[asyncpg.Record]:
        """Update post - only by owner - UPDATED for audio support"""
        if hasattr(post_in, 'dict'):
            update_data = post_in.dict(exclude_unset=True)
        else:
            update_data = post_in

        if not update_data:
            return await self.get(post_id)

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        values.extend([post_id, user_id])
        query = f"""
            UPDATE posts
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index} AND user_id = ${index + 1}
            RETURNING *
        """

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, *values)

    async def delete(self, post_id: UUID, user_id: UUID) -> bool:
        """Soft delete post - only by owner"""
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE posts SET status = 'deleted' WHERE id = $1 AND user_id = $2",
                post_id, user_id
            )
            return "UPDATE 1" in result

    async def count_user_posts(self, user_id: UUID) -> int:
        """Count user's active posts"""
        async with database.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE user_id = $1 AND status != 'deleted'",
                user_id
            )

    # Phase 3: Audio-specific methods
    async def get_audio_posts(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[asyncpg.Record]:
        """Get audio posts for user"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT p.*,
                       CASE WHEN p.is_anonymous THEN NULL ELSE u.username END as username,
                       CASE WHEN p.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                WHERE p.status = 'active'
                AND p.moderation_status = 'approved'
                AND p.content_type = 'audio'
                AND (p.visibility = 'public' OR p.user_id = $1)
                AND u.is_active = true
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

    async def create_file_upload_record(self, user_id: UUID, upload_data) -> Optional[asyncpg.Record]:
        """Create file upload record for tracking"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO file_uploads
                (user_id, filename, original_filename, file_url, file_size, mime_type, duration)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                user_id, upload_data["filename"], upload_data["original_filename"],
                upload_data["file_url"], upload_data["file_size"], upload_data["mime_type"],
                upload_data["duration"]
            )

    async def update_file_upload_with_post(self, file_id: UUID, post_id: UUID) -> bool:
        """Associate file upload with a post"""
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE file_uploads SET post_id = $1 WHERE id = $2",
                post_id, file_id
            )
            return "UPDATE 1" in result

    async def get_user_file_uploads(self, user_id: UUID, limit: int = 50) -> List[asyncpg.Record]:
        """Get user's file uploads"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT * FROM file_uploads WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
                user_id, limit
            )

    # Phase 3: Video-specific methods
    async def get_video_posts(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[asyncpg.Record]:
        """Get video posts for user"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT p.*,
                       CASE WHEN p.is_anonymous THEN NULL ELSE u.username END as username,
                       CASE WHEN p.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar
                FROM posts p
                LEFT JOIN users u ON p.user_id = u.id
                WHERE p.status = 'active'
                AND p.moderation_status = 'approved'
                AND p.content_type = 'video'
                AND (p.visibility = 'public' OR p.user_id = $1)
                AND u.is_active = true
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

# Create instance
post_crud = CRUDPost()
