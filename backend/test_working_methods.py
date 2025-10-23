"""
Examine how the working methods handle database operations
"""
import asyncio
from app.database.database import database

async def test_working_methods():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Test 1: Check how JOIN works (this is working according to tests)
            print("1. Testing JOIN operation pattern:")
            
            # First, let's see what happens when we try to join a room
            room = await conn.fetchrow("SELECT id FROM live_audio_rooms LIMIT 1")
            if room:
                # Set RLS context like the join_room method does
                await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
                
                # Try the exact INSERT from join_room method
                try:
                    join_result = await conn.execute("""
                        INSERT INTO live_audio_room_participants (room_id, user_id, role)
                        VALUES ($1, $2, 'participant')
                    """, room['id'], user_id)
                    print(f"   JOIN INSERT result: {join_result}")
                except Exception as e:
                    print(f"   JOIN INSERT failed: {e}")
            
            # Test 2: Check if SELECT operations work
            print("2. Testing SELECT operations:")
            select_result = await conn.fetch("SELECT * FROM live_audio_room_participants WHERE user_id = $1 LIMIT 2", user_id)
            print(f"   SELECT found {len(select_result)} records")
            
            # Test 3: Let's see what the actual working UPDATE pattern should be
            print("3. Let's examine a participant record that should be updatable:")
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            if participant:
                print(f"   Participant ID: {participant['id']}")
                print(f"   Room ID: {participant['room_id']}") 
                print(f"   User ID: {participant['user_id']}")
                print(f"   Left at: {participant['left_at']}")
                
                # Try the simplest possible UPDATE
                simple_update = await conn.execute("UPDATE live_audio_room_participants SET role = 'test_role' WHERE id = $1", participant['id'])
                print(f"   Simple UPDATE result: {simple_update}")
                
    finally:
        await database.close()

asyncio.run(test_working_methods())
