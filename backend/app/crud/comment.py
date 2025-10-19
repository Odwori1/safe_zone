import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database

class CRUDComment:
    async def get(self, comment_id: UUID) -> Optional[asyncpg.Record]:
        """Get comment by ID"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM comments WHERE id = $1 AND status != 'deleted'",
                comment_id
            )

    async def get_by_post(self, post_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get comments by post ID"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT c.*, 
                       CASE WHEN c.is_anonymous THEN NULL ELSE u.username END as username,
                       CASE WHEN c.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar
                FROM comments c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.post_id = $1 AND c.status = 'active' AND c.parent_comment_id IS NULL
                ORDER BY c.created_at ASC
                LIMIT $2 OFFSET $3
                """,
                post_id, limit, offset
            )

    async def get_replies(self, parent_comment_id: UUID) -> List[asyncpg.Record]:
        """Get replies to a comment"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT c.*, 
                       CASE WHEN c.is_anonymous THEN NULL ELSE u.username END as username,
                       CASE WHEN c.is_anonymous THEN NULL ELSE u.profile_picture END as user_avatar
                FROM comments c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.parent_comment_id = $1 AND c.status = 'active'
                ORDER BY c.created_at ASC
                """,
                parent_comment_id
            )

    async def create(self, user_id: UUID, comment_in) -> asyncpg.Record:
        """Create new comment"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO comments (user_id, post_id, parent_comment_id, content, is_anonymous)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id, comment_in.post_id, comment_in.parent_comment_id, 
                comment_in.content, comment_in.is_anonymous
            )

    async def update(self, comment_id: UUID, user_id: UUID, comment_in) -> Optional[asyncpg.Record]:
        """Update comment - only by owner"""
        if hasattr(comment_in, 'dict'):
            update_data = comment_in.dict(exclude_unset=True)
        else:
            update_data = comment_in

        if not update_data:
            return await self.get(comment_id)

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        values.extend([comment_id, user_id])
        query = f"""
            UPDATE comments
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index} AND user_id = ${index + 1}
            RETURNING *
        """

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, *values)

    async def delete(self, comment_id: UUID, user_id: UUID) -> bool:
        """Soft delete comment - only by owner"""
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE comments SET status = 'deleted' WHERE id = $1 AND user_id = $2",
                comment_id, user_id
            )
            return "UPDATE 1" in result

    async def count_post_comments(self, post_id: UUID) -> int:
        """Count active comments for a post"""
        async with database.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM comments WHERE post_id = $1 AND status = 'active'",
                post_id
            )

# Create instance
comment_crud = CRUDComment()
