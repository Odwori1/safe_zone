"""
Test if disabling triggers fixes the UPDATE issue
"""
import asyncio
from app.database.database import database

async def test_disable_triggers():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user and participant
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            
            print(f"Testing with participant: {participant['id']}")
            print(f"Before - left_at: {participant['left_at']}")
            
            # Disable triggers temporarily
            await conn.execute("ALTER TABLE live_audio_room_participants DISABLE TRIGGER ALL")
            
            # Test UPDATE with triggers disabled
            result = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"UPDATE with triggers disabled: {result}")
            
            # Check result
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"After - left_at: {after['left_at']}")
            
            # Re-enable triggers
            await conn.execute("ALTER TABLE live_audio_room_participants ENABLE TRIGGER ALL")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_disable_triggers())
