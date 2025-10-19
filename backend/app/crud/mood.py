import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from app.database.database import database

class CRUDMood:
    async def create(self, user_id: UUID, mood_in) -> Optional[asyncpg.Record]:
        """Create new mood entry"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO mood_entries (user_id, mood, intensity, notes)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                user_id, mood_in.mood, mood_in.intensity, mood_in.notes
            )

    async def get(self, entry_id: UUID, user_id: UUID) -> Optional[asyncpg.Record]:
        """Get mood entry by ID (user-specific)"""
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM mood_entries WHERE id = $1 AND user_id = $2",
                entry_id, user_id
            )

    async def get_user_entries(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get mood entries for user with pagination"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT * FROM mood_entries 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2 OFFSET $3
                """,
                user_id, limit, offset
            )

    async def get_recent_entries(self, user_id: UUID, days: int = 30) -> List[asyncpg.Record]:
        """Get recent mood entries for user"""
        async with database.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT * FROM mood_entries 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '$2 days'
                ORDER BY created_at DESC
                """,
                user_id, days
            )

    async def update(self, entry_id: UUID, user_id: UUID, mood_in) -> Optional[asyncpg.Record]:
        """Update mood entry - only by owner"""
        if hasattr(mood_in, 'dict'):
            update_data = mood_in.dict(exclude_unset=True)
        else:
            update_data = mood_in

        if not update_data:
            return await self.get(entry_id, user_id)

        update_fields = []
        values = []
        index = 1

        for field, value in update_data.items():
            update_fields.append(f"{field} = ${index}")
            values.append(value)
            index += 1

        values.extend([entry_id, user_id])
        query = f"""
            UPDATE mood_entries
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${index} AND user_id = ${index + 1}
            RETURNING *
        """

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, *values)

    async def delete(self, entry_id: UUID, user_id: UUID) -> bool:
        """Delete mood entry - only by owner"""
        async with database.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM mood_entries WHERE id = $1 AND user_id = $2",
                entry_id, user_id
            )
            return "DELETE 1" in result

    async def count_user_entries(self, user_id: UUID) -> int:
        """Count user's mood entries"""
        async with database.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM mood_entries WHERE user_id = $1",
                user_id
            )

    async def get_mood_stats(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get mood statistics for user"""
        async with database.pool.acquire() as conn:
            # Basic stats
            total_entries = await conn.fetchval(
                "SELECT COUNT(*) FROM mood_entries WHERE user_id = $1",
                user_id
            )

            average_intensity = await conn.fetchval(
                "SELECT AVG(intensity) FROM mood_entries WHERE user_id = $1 AND intensity IS NOT NULL",
                user_id
            )

            most_common_mood = await conn.fetchval(
                """
                SELECT mood FROM mood_entries 
                WHERE user_id = $1 
                GROUP BY mood 
                ORDER BY COUNT(*) DESC 
                LIMIT 1
                """,
                user_id
            )

            # Mood frequency
            mood_frequency_records = await conn.fetch(
                """
                SELECT mood, COUNT(*) as count 
                FROM mood_entries 
                WHERE user_id = $1 
                GROUP BY mood 
                ORDER BY count DESC
                """,
                user_id
            )

            mood_frequency = {record['mood']: record['count'] for record in mood_frequency_records}

            # Weekly trend (last 7 days)
            weekly_trend = await conn.fetch(
                """
                SELECT 
                    DATE(created_at) as date,
                    AVG(intensity) as avg_intensity,
                    COUNT(*) as entry_count
                FROM mood_entries 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                """,
                user_id
            )

            weekly_trend_list = []
            for record in weekly_trend:
                weekly_trend_list.append({
                    'date': record['date'].isoformat(),
                    'avg_intensity': float(record['avg_intensity']) if record['avg_intensity'] else None,
                    'entry_count': record['entry_count']
                })

            return {
                'total_entries': total_entries,
                'average_intensity': float(average_intensity) if average_intensity else None,
                'most_common_mood': most_common_mood,
                'mood_frequency': mood_frequency,
                'weekly_trend': weekly_trend_list
            }

# Create instance
mood_crud = CRUDMood()
