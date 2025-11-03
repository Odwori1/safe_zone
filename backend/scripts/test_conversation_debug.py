#!/usr/bin/env python3
"""
Debug script to test conversation creation
"""

import asyncio
import asyncpg
from uuid import UUID
from app.core.config import settings

async def test_conversation_creation():
    """Test conversation creation directly"""
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        user_id = UUID('8808956b-11fb-4253-91ef-98b9902ffbc8')  # Your test user
        
        # Set user context
        await conn.execute("SELECT set_config('app.current_user_id', $1, false)", str(user_id))
        
        # Try to create conversation
        result = await conn.fetchrow(
            "INSERT INTO conversations (is_group, title, created_by) VALUES ($1, $2, $3) RETURNING *",
            False, "Test Debug Conversation", user_id
        )
        
        print("✅ Conversation created successfully!")
        print(f"Conversation ID: {result['id']}")
        
        # Add participant
        await conn.execute(
            "INSERT INTO conversation_participants (conversation_id, user_id, role) VALUES ($1, $2, 'admin')",
            result['id'], user_id
        )
        
        print("✅ Participant added successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_conversation_creation())
