"""
Final test of UPDATE functionality after all fixes
"""
import asyncio
from app.database.database import database

async def test_final_update():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== FINAL UPDATE TEST ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"Test user: {user_id}")
            
            # First, let's create a test participant
            room = await conn.fetchrow("SELECT id FROM live_audio_rooms LIMIT 1")
            if not room:
                print("No rooms found, creating one...")
                await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
                room = await conn.fetchrow("""
                    INSERT INTO live_audio_rooms (title, created_by, is_active)
                    VALUES ('Test Room', $1, true)
                    RETURNING *
                """, user_id)
                print(f"Created room: {room['id']}")
            
            # Join the room
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            participant = await conn.fetchrow("""
                INSERT INTO live_audio_room_participants (room_id, user_id, role)
                VALUES ($1, $2, 'participant')
                RETURNING *
            """, room['id'], user_id)
            
            print(f"Created participant: {participant['id']}")
            print(f"Before update - left_at: {participant['left_at']}, is_active: {participant['is_active']}")
            
            # Test the UPDATE
            print("\nTesting UPDATE (leave room):")
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE id = $1
            """, participant['id'])
            print(f"UPDATE result: {result}")
            
            # Check the result
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
            # Test the exact query from the leave_room method
            print("\nTesting exact leave_room method query:")
            result2 = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, room['id'], user_id)
            print(f"leave_room query result: {result2}")
            
            # Run the actual test
            print("\n=== RUNNING ACTUAL TEST SUITE ===\n")
            from tests.test_room_leaving_fixed import main
            await main()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_final_update())
