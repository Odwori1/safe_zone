"""
Test UPDATE with error details
"""
import asyncio
from app.database.database import database

async def test_update_error():
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
            
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Try to understand why UPDATE fails
            print("Testing individual conditions:")
            
            # Check if record exists with the conditions
            exists = await conn.fetchval("""
                SELECT 1 FROM live_audio_room_participants 
                WHERE id = $1 AND room_id = $2 AND user_id = $3 AND left_at IS NULL
            """, participant['id'], participant['room_id'], participant['user_id'])
            print(f"Record exists with conditions: {exists is not None}")
            
            # Try a simple test update
            print("Testing simple UPDATE:")
            result = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"Simple UPDATE result: {result}")
            
            # Check current state
            current = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"Current state - left_at: {current['left_at']}")
            
    finally:
        await database.close()

asyncio.run(test_update_error())
