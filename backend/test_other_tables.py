"""
Test if UPDATE works on other tables to see if this is a table-specific issue
"""
import asyncio
from app.database.database import database

async def test_other_tables():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            print("Testing UPDATE on other tables:")
            
            # Test 1: Update users table (should work)
            print("1. Testing UPDATE on users table:")
            user_update = await conn.execute("UPDATE users SET updated_at = NOW() WHERE id = $1", user_id)
            print(f"   Users UPDATE result: {user_update}")
            
            # Test 2: Update live_audio_rooms table
            print("2. Testing UPDATE on live_audio_rooms table:")
            room = await conn.fetchrow("SELECT id FROM live_audio_rooms WHERE created_by = $1 LIMIT 1", user_id)
            if room:
                room_update = await conn.execute("UPDATE live_audio_rooms SET updated_at = NOW() WHERE id = $1", room['id'])
                print(f"   Rooms UPDATE result: {room_update}")
            else:
                print("   No room found to test")
                
            # Test 3: Let's check if DELETE works on the participants table
            print("3. Testing DELETE on live_audio_room_participants:")
            participant = await conn.fetchrow("SELECT id FROM live_audio_room_participants WHERE user_id = $1 LIMIT 1", user_id)
            if participant:
                delete_result = await conn.execute("DELETE FROM live_audio_room_participants WHERE id = $1", participant['id'])
                print(f"   DELETE result: {delete_result}")
            else:
                print("   No participant found to delete")
                
    finally:
        await database.close()

asyncio.run(test_other_tables())
