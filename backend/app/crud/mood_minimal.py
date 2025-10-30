import asyncpg
from uuid import UUID
from typing import List, Dict, Any
import logging
from app.database.database import database

logger = logging.getLogger(__name__)

async def get_minimal_mood_with_context(user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
    """
    MINIMAL APPROACH: Use the working basic query and add minimal context
    """
    try:
        async with database.pool.acquire() as conn:
            # Set RLS context
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            # Use the exact same query that works in basic endpoints
            query = """
                SELECT 
                    id, mood, intensity, source_type, source_id, created_at,
                    triggers, activities, notes, physical_symptoms,
                    social_context, sleep_quality, energy_level
                FROM mood_entries 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2
                ORDER BY created_at DESC
            """
            entries = await conn.fetch(query, user_id, days)
            
            # Convert to list of dicts - this should definitely work
            result = []
            for entry in entries:
                entry_dict = dict(entry)
                result.append(entry_dict)
            
            return result
            
    except Exception as e:
        logger.error(f"Error in minimal mood query: {str(e)}")
        raise
