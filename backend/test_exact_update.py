"""
Test the exact UPDATE query from leave_room method
"""
import asyncio
from app.database.database import database

async def test_exact():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get first room
            room = await conn.fetchrow("SELECT room_id FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            room_id = room['room_id']
            print(f"Room: {room_id}")
            
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Test EXACT query from leave_room method
            print("Testing EXACT leave_room query:")
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, room_id, user_id)
            print(f"Result: {result}")
            
            # Check what actually changed
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE room_id = $1 AND user_id = $2", room_id, user_id)
            print(f"After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
    finally:
        await database.close()

asyncio.run(test_exact())
