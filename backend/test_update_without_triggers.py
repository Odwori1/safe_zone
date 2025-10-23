"""
Test if UPDATE works when we temporarily disable any constraints
"""
import asyncio
from app.database.database import database

async def test_direct():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get first participant record
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            print(f"Participant ID: {participant['id']}")
            print(f"Before - left_at: {participant['left_at']}, is_active: {participant['is_active']}")
            
            # Try direct update without WHERE conditions
            result = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"Direct update result: {result}")
            
            # Check result
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"After - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
    finally:
        await database.close()

asyncio.run(test_direct())
