"""
Test with the correct RLS pattern applied
"""
import asyncio
from app.database.database import database

async def test_with_correct_rls():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== TESTING WITH CORRECT RLS PATTERN ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"Test user: {user_id}")
            
            # First, ensure we have a public room to join
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Create a public room if none exists
            public_room = await conn.fetchrow("""
                SELECT id FROM live_audio_rooms 
                WHERE visibility = 'public' AND is_active = true 
                LIMIT 1
            """)
            
            if not public_room:
                print("Creating a public room...")
                public_room = await conn.fetchrow("""
                    INSERT INTO live_audio_rooms (title, created_by, visibility, is_active)
                    VALUES ('Public Test Room', $1, 'public', true)
                    RETURNING id
                """, user_id)
                print(f"Created public room: {public_room['id']}")
            else:
                print(f"Using existing public room: {public_room['id']}")
            
            # Now test joining the room (INSERT)
            print("\nTesting room join (INSERT):")
            participant = await conn.fetchrow("""
                INSERT INTO live_audio_room_participants (room_id, user_id, role)
                VALUES ($1, $2, 'participant')
                RETURNING *
            """, public_room['id'], user_id)
            
            print(f"✅ Successfully joined room. Participant ID: {participant['id']}")
            print(f"Before update - left_at: {participant['left_at']}, is_active: {participant['is_active']}")
            
            # Test the UPDATE (leave room)
            print("\nTesting room leave (UPDATE):")
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE id = $1
            """, participant['id'])
            print(f"UPDATE result: {result}")
            
            # Check if it worked
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
            # Test the exact leave_room method query
            print("\nTesting exact leave_room method query:")
            result2 = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, public_room['id'], user_id)
            print(f"leave_room query result: {result2}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_with_correct_rls())
