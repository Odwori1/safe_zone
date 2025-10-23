"""
Check table structure and constraints
"""
import asyncio
from app.database.database import database

async def test_structure():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get participant record
            participant = await conn.fetchrow("""
                SELECT * FROM live_audio_room_participants 
                WHERE user_id = $1 AND left_at IS NULL 
                LIMIT 1
            """, user_id)
            
            if participant:
                print(f"Participant ID: {participant['id']}")
                print(f"Room ID: {participant['room_id']}")
                print(f"Left at: {participant['left_at']}")
                print(f"Is active: {participant['is_active']}")
                
                # Try direct update by ID
                result = await conn.execute("""
                    UPDATE live_audio_room_participants 
                    SET left_at = NOW() 
                    WHERE id = $1
                """, participant['id'])
                print(f"Update by ID result: {result}")
                
    finally:
        await database.close()

asyncio.run(test_structure())
