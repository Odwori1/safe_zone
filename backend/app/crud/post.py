import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database

class CRUDPost:
    async def get(self, post_id: UUID) -> Optional[asyncpg.Record]:
        """Get post by ID"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM posts WHERE id = $1 AND status != 'deleted'",
                post_id
            )

    async def get_by_user(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get posts by user ID"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
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

    async def get_feed(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        mood: Optional[str] = None,
        visibility: Optional[str] = None,
        user_id_filter: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> List[asyncpg.Record]:
        """Get post feed for user (public posts and user's own posts) with optional filters"""
        # Start building the query
        query_parts = [
            """
            SELECT p.*,
                   CASE WHEN p.is_anonymous THEN NULL ELSE u.username END as username,
                   CASE WHEN p.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.status = 'active'
            AND (p.moderation_status = 'approved' OR p.user_id = $1)
            AND u.is_active = true
            """
        ]
        
        params = [user_id]
        param_count = 1
        
        # Add visibility filter
        if visibility:
            param_count += 1
            query_parts.append(f"AND p.visibility = ${param_count}")
            params.append(visibility)
        else:
            # Default visibility filter (show public posts and user's own posts)
            query_parts.append("AND (p.visibility = 'public' OR p.user_id = $1)")
        
        # Add mood filter
        if mood:
            param_count += 1
            query_parts.append(f"AND p.mood = ${param_count}")
            params.append(mood)
        
        # Add user_id filter (for "my posts" functionality)
        if user_id_filter:
            param_count += 1
            query_parts.append(f"AND p.user_id = ${param_count}")
            params.append(user_id_filter)
        
        # Add search filter (text search in post content)
        if search:
            param_count += 1
            query_parts.append(f"AND p.content ILIKE ${param_count}")
            params.append(f"%{search}%")
        
        # Add ordering and pagination
        query_parts.append("ORDER BY p.created_at DESC")
        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(limit)
        param_count += 1
        query_parts.append(f"OFFSET ${param_count}")
        params.append(offset)
        
        # Combine all query parts
        final_query = "\n".join(query_parts)
        
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetch(final_query, *params)

    async def create(self, user_id: UUID, post_in) -> asyncpg.Record:
        """Create new post - FIXED to properly set user context with AUTO-APPROVAL"""
        async with database.pool.acquire() as conn:
            # CRITICAL: Set user context for RLS policies
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            # Build the INSERT query based on available fields
            if hasattr(post_in, 'audio_url') and post_in.audio_url:
                # Audio post with additional fields - AUTO-APPROVED
                return await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous,
                                     audio_url, audio_duration, file_size, mime_type, moderation_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'approved')
                    RETURNING *
                    """,
                    user_id, post_in.content, post_in.content_type, post_in.mood,
                    post_in.visibility, post_in.is_anonymous,
                    getattr(post_in, 'audio_url', None),
                    getattr(post_in, 'audio_duration', None),
                    getattr(post_in, 'file_size', None),
                    getattr(post_in, 'mime_type', None)
                )
            else:
                # Regular text post - AUTO-APPROVED
                return await conn.fetchrow(
                    """
                    INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous, moderation_status)
                    VALUES ($1, $2, $3, $4, $5, $6, 'approved')
                    RETURNING *
                    """,
                    user_id, post_in.content, post_in.content_type, post_in.mood,
                    post_in.visibility, post_in.is_anonymous
                )

    async def update(self, post_id: UUID, user_id: UUID, post_in) -> Optional[asyncpg.Record]:
        """Update post - only by owner"""
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
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(query, *values)

    async def delete(self, post_id: UUID, user_id: UUID) -> bool:
        """Soft delete post - only by owner"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
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

    # The following methods are now properly indented as part of the class
    async def has_user_liked(self, post_id: UUID, user_id: UUID) -> bool:
        """Check if user has liked a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.fetchval(
                "SELECT 1 FROM post_likes WHERE post_id = $1 AND user_id = $2",
                post_id, user_id
            )
            return result is not None

    async def add_like(self, post_id: UUID, user_id: UUID) -> bool:
        """Add a like to a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            try:
                result = await conn.execute(
                    "INSERT INTO post_likes (post_id, user_id) VALUES ($1, $2)",
                    post_id, user_id
                )
                return "INSERT 0 1" in result
            except asyncpg.exceptions.UniqueViolationError:
                # User already liked this post (RLS will prevent this but handle gracefully)
                return False

    async def remove_like(self, post_id: UUID, user_id: UUID) -> bool:
        """Remove a like from a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "DELETE FROM post_likes WHERE post_id = $1 AND user_id = $2",
                post_id, user_id
            )
            return "DELETE 1" in result

    async def get_like_count(self, post_id: UUID, user_id: UUID) -> int:
        """Get the number of likes for a post - FOLLOWING RLS PATTERN"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS (same pattern as other methods)
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchval(
                "SELECT COUNT(*) FROM post_likes WHERE post_id = $1",
                post_id
            )

# Create instance
post_crud = CRUDPost()
