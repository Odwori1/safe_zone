import asyncpg
from typing import List, Dict, Any
from uuid import UUID
from app.database.database import database

class CRUDMoodHybrid:
    async def get_hybrid_entries_working(self, user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
        """
        WORKING HYBRID: Uses the exact same pattern as basic endpoints
        """
        async with database.pool.acquire() as conn:
            # Set RLS context - THIS IS THE KEY
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            # Simple query that works (no complex joins)
            query = """
                SELECT 
                    id, mood, intensity, source_type, source_id, 
                    created_at, triggers, activities, notes,
                    physical_symptoms, social_context, sleep_quality, 
                    energy_level
                FROM mood_entries 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2
                ORDER BY created_at DESC
            """
            entries = await conn.fetch(query, user_id, days)
            
            # Convert to list of dicts
            return [dict(entry) for entry in entries]

# Create instance
mood_hybrid_crud = CRUDMoodHybrid()
