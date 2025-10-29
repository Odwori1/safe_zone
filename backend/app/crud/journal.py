import asyncpg
from typing import Optional, List
from uuid import UUID
from app.database.database import database
from app.schemas.post import PostContentType, PostVisibility

class CRUDJournal:
    async def create_entry(self, user_id: UUID, journal_in) -> asyncpg.Record:
        """Create a new private journal entry - FIXED to set user context for RLS"""
        async with database.pool.acquire() as conn:
            # CRITICAL: Set user context for RLS policies
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                """
                INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, content, mood, created_at, updated_at
                """,
                user_id, journal_in.content, PostContentType.JOURNAL, 
                journal_in.mood, PostVisibility.PRIVATE, False
            )

    async def get_entry(self, entry_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get a specific journal entry (only if user owns it)"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                """
                SELECT id, content, mood, created_at, updated_at
                FROM posts 
                WHERE id = $1 AND user_id = $2 AND content_type = 'journal' AND status != 'deleted'
                """,
                entry_id, user_id
            )

    async def get_user_entries(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get all journal entries for a user"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetch(
                """
                SELECT id, content, mood, created_at, updated_at
                FROM posts 
                WHERE user_id = $1 AND content_type = 'journal' AND status = 'active'
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

    async def update_entry(self, entry_id: UUID, user_id: UUID, journal_in) -> Optional[asyncpg.Record]:
        """Update a journal entry - only by owner"""
        if hasattr(journal_in, 'dict'):
            update_data = journal_in.dict(exclude_unset=True)
        else:
            update_data = journal_in

        if not update_data:
            return await self.get_entry(entry_id, user_id)

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        values.extend([entry_id, user_id])
        query = f"""
            UPDATE posts
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index} AND user_id = ${index + 1} AND content_type = 'journal'
            RETURNING id, content, mood, created_at, updated_at
        """

        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(query, *values)

    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> bool:
        """Soft delete a journal entry - only by owner"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "UPDATE posts SET status = 'deleted' WHERE id = $1 AND user_id = $2 AND content_type = 'journal'",
                entry_id, user_id
            )
            return "UPDATE 1" in result

    async def count_user_entries(self, user_id: UUID) -> int:
        """Count user's active journal entries"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE user_id = $1 AND content_type = 'journal' AND status = 'active'",
                user_id
            )

    async def get_journal_stats(self, user_id: UUID) -> dict:
        """Get journal statistics for user"""
        async with database.pool.acquire() as conn:
            # Set user context for RLS
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            # Total entries
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE user_id = $1 AND content_type = 'journal' AND status = 'active'",
                user_id
            )
            
            # Entries this week
            week_count = await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE user_id = $1 AND content_type = 'journal' AND status = 'active' AND created_at >= NOW() - INTERVAL '7 days'",
                user_id
            )
            
            # Entries this month
            month_count = await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE user_id = $1 AND content_type = 'journal' AND status = 'active' AND created_at >= NOW() - INTERVAL '30 days'",
                user_id
            )
            
            # Most common mood
            common_mood = await conn.fetchval(
                "SELECT mood FROM posts WHERE user_id = $1 AND content_type = 'journal' AND status = 'active' AND mood IS NOT NULL GROUP BY mood ORDER BY COUNT(*) DESC LIMIT 1",
                user_id
            )
            
            return {
                'total_entries': total,
                'entries_this_week': week_count,
                'entries_this_month': month_count,
                'most_common_mood': common_mood
            }

# Create instance
journal_crud = CRUDJournal()
