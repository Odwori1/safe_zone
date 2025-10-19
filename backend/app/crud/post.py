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
        """Get post feed for user (public posts and user's own posts)"""
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
        """Create new post"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous)
                VALUES ($1, $2, $3, $4, $5, $6)
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

# Create instance
post_crud = CRUDPost()
