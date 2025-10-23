"""
Test RLS UPDATE policy
"""
import asyncio
from app.database.database import database

async def test_rls():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get a room user is in
            room = await conn.fetchrow("SELECT room_id FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            room_id = room['room_id']
            print(f"Room: {room_id}")
            
            # Test WITHOUT RLS context
            print("Testing WITHOUT RLS context:")
            result1 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE room_id = $1 AND user_id = $2", room_id, user_id)
            print(f"Result: {result1}")
            
            # Test WITH RLS context
            print("Testing WITH RLS context:")
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            result2 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE room_id = $1 AND user_id = $2", room_id, user_id)
            print(f"Result: {result2}")
            
    finally:
        await database.close()

asyncio.run(test_rls())
