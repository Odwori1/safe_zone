"""
Test UPDATE without RLS context to isolate the issue
"""
import asyncio
from app.database.database import database

async def test_no_rls():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get participant record
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            print(f"Participant ID: {participant['id']}")
            
            print("Testing WITHOUT RLS context:")
            
            # Test without setting RLS context
            result = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"UPDATE result: {result}")
            
            # Check if it worked
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"After update - left_at: {after['left_at']}")
            
            # Test if we can update ANY record in this table
            print("\nTesting update on different record:")
            different_participant = await conn.fetchrow("SELECT id FROM live_audio_room_participants WHERE id != $1 LIMIT 1", participant['id'])
            if different_participant:
                result2 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", different_participant['id'])
                print(f"Different record UPDATE result: {result2}")
            
    finally:
        await database.close()

asyncio.run(test_no_rls())
