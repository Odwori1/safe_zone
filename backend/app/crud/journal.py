"""
Enhanced Journal CRUD Operations - Using separate journals table
"""

import asyncpg
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.database.database import database

class CRUDJournal:
    async def create_entry(self, user_id: UUID, journal_in) -> asyncpg.Record:
        """Create a new journal entry in separate journals table"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            # Calculate word count and read time
            content = journal_in.content
            word_count = len(content.split())
            read_time_minutes = max(1, word_count // 200)  # 200 words per minute

            return await conn.fetchrow(
                """
                INSERT INTO journals (
                    user_id, title, content, mood, mood_intensity, tags,
                    prompt_id, word_count, read_time_minutes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
                """,
                user_id,
                getattr(journal_in, 'title', None),
                content,
                getattr(journal_in, 'mood', None),
                getattr(journal_in, 'mood_intensity', None),
                getattr(journal_in, 'tags', None),
                getattr(journal_in, 'prompt_id', None),
                word_count,
                read_time_minutes
            )

    async def get_entry(self, entry_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get a specific journal entry from journals table - ROBUST ERROR HANDLING"""
        async with database.pool.acquire() as conn:
            try:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
                result = await conn.fetchrow(
                    """
                    SELECT j.*, p.prompt_text, p.category as prompt_category
                    FROM journals j
                    LEFT JOIN journal_prompts p ON j.prompt_id = p.id
                    WHERE j.id = $1 AND j.status != 'deleted'
                    """,
                    entry_id
                )
                return result
            except Exception as e:
                # If there's any error (including RLS permission issues), return None
                # This could be due to: journal doesn't exist, RLS blocks access, etc.
                return None

    async def get_user_entries(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[asyncpg.Record]:
        """Get all journal entries for a user from journals table - FIXED PARAMETER BINDING"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            query = """
                SELECT j.*, p.prompt_text, p.category as prompt_category
                FROM journals j
                LEFT JOIN journal_prompts p ON j.prompt_id = p.id
                WHERE j.user_id = $1
            """
            params = [user_id]
            param_count = 1

            if status:
                param_count += 1
                query += f" AND j.status = ${param_count}"
                params.append(status)
            else:
                query += " AND j.status != 'deleted'"

            # Always use consistent parameter positions for pagination
            # $<param_count + 1> for LIMIT, $<param_count + 2> for OFFSET
            query += f" ORDER BY j.created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])

            return await conn.fetch(query, *params)

    async def update_entry(self, entry_id: UUID, user_id: UUID, journal_in) -> Optional[asyncpg.Record]:
        """Update a journal entry in journals table"""
        if hasattr(journal_in, 'dict'):
            update_data = journal_in.dict(exclude_unset=True)
        else:
            update_data = journal_in

        if not update_data:
            return await self.get_entry(entry_id, user_id)

        # Recalculate word count if content is updated
        if 'content' in update_data:
            content = update_data['content']
            word_count = len(content.split())
            read_time_minutes = max(1, word_count // 200)
            update_data['word_count'] = word_count
            update_data['read_time_minutes'] = read_time_minutes

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        # Append entry_id and user_id for WHERE clause
        values.extend([entry_id, user_id])
        query = f"""
            UPDATE journals
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index} AND user_id = ${index + 1}
            RETURNING *
        """

        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(query, *values)

    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> bool:
        """Soft delete a journal entry from journals table"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute(
                "UPDATE journals SET status = 'deleted' WHERE id = $1 AND user_id = $2",
                entry_id, user_id
            )
            return "UPDATE 1" in result

    async def count_user_entries(self, user_id: UUID, status: Optional[str] = None) -> int:
        """Count user's journal entries"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            query = "SELECT COUNT(*) FROM journals WHERE user_id = $1"
            params = [user_id]

            if status:
                query += " AND status = $2"
                params.append(status)
            else:
                query += " AND status != 'deleted'"

            return await conn.fetchval(query, *params)

    async def get_journal_stats(self, user_id: UUID) -> dict:
        """Get enhanced journal statistics for user"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            # Enhanced stats from journals table
            stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) as total_entries,
                    COALESCE(SUM(word_count), 0) as total_words,
                    AVG(mood_intensity) as average_mood,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as entries_this_week,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as entries_this_month
                FROM journals
                WHERE user_id = $1 AND status = 'active'
            """, user_id)

            # Most common mood
            common_mood = await conn.fetchval("""
                SELECT mood FROM journals
                WHERE user_id = $1 AND status = 'active' AND mood IS NOT NULL
                GROUP BY mood ORDER BY COUNT(*) DESC LIMIT 1
            """, user_id)

            # Most used tags
            tags_result = await conn.fetch("""
                SELECT UNNEST(tags) as tag, COUNT(*) as count
                FROM journals
                WHERE user_id = $1 AND tags IS NOT NULL AND status = 'active'
                GROUP BY tag
                ORDER BY count DESC
                LIMIT 5
            """, user_id)

            most_used_tags = [row['tag'] for row in tags_result]

            return {
                'total_entries': stats['total_entries'],
                'total_words': stats['total_words'],
                'average_mood': float(stats['average_mood']) if stats['average_mood'] else None,
                'most_used_tags': most_used_tags,
                'entries_this_week': stats['entries_this_week'],
                'entries_this_month': stats['entries_this_month'],
                'most_common_mood': common_mood
            }

    async def get_prompts(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[asyncpg.Record]:
        """Get journal prompts from journal_prompts table"""
        async with database.pool.acquire() as conn:
            query = "SELECT * FROM journal_prompts WHERE is_active = true"
            params = []

            if category:
                query += " AND category = $1"
                params.append(category)

            if difficulty:
                query += " AND difficulty_level = $2"
                params.append(difficulty)

            query += " ORDER BY created_at DESC"

            return await conn.fetch(query, *params)

# Create instance
journal_crud = CRUDJournal()
