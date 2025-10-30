import asyncpg
from uuid import UUID
from typing import List, Dict, Any
import logging
from app.database.database import database

logger = logging.getLogger(__name__)

async def get_simple_hybrid_entries(user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
    """
    SIMPLE HYBRID: Get mood entries with basic post/journal context without complex joins
    """
    try:
        # Use the same connection pattern as working endpoints
        async with database.pool.acquire() as conn:
            # Set RLS context
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            # First, get all mood entries for the user
            mood_query = """
                SELECT id, mood, intensity, source_type, source_id, created_at, 
                       triggers, activities, notes, physical_symptoms, 
                       social_context, sleep_quality, energy_level
                FROM mood_entries 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2
                ORDER BY created_at DESC
            """
            mood_entries = await conn.fetch(mood_query, user_id, days)
            
            hybrid_entries = []
            
            for entry in mood_entries:
                entry_dict = dict(entry)
                source_type = entry_dict.get('source_type')
                source_id = entry_dict.get('source_id')
                
                # Add basic context based on source type
                if source_type == 'post' and source_id:
                    try:
                        # Get post title if exists
                        post_query = "SELECT title, content FROM posts WHERE id = $1 AND user_id = $2"
                        post_data = await conn.fetchrow(post_query, source_id, user_id)
                        if post_data:
                            entry_dict['post_title'] = post_data['title']
                            entry_dict['post_content'] = post_data['content']
                            entry_dict['post_id'] = source_id
                    except Exception as e:
                        logger.warning(f"Could not fetch post data for {source_id}: {e}")
                
                elif source_type == 'journal' and source_id:
                    try:
                        # Get journal title if exists  
                        journal_query = "SELECT title, content FROM journals WHERE id = $1 AND user_id = $2"
                        journal_data = await conn.fetchrow(journal_query, source_id, user_id)
                        if journal_data:
                            entry_dict['journal_title'] = journal_data['title'] 
                            entry_dict['journal_content'] = journal_data['content']
                            entry_dict['journal_id'] = source_id
                    except Exception as e:
                        logger.warning(f"Could not fetch journal data for {source_id}: {e}")
                
                hybrid_entries.append(entry_dict)
            
            return hybrid_entries
            
    except Exception as e:
        logger.error(f"Error in simple hybrid query: {str(e)}")
        raise
