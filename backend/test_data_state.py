"""
Check the current state of data after table recreation
"""
import asyncio
from app.database.database import database

async def test_data_state():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== CHECKING DATA STATE AFTER RECREATION ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"Test user: {user_id}")
            
            # Check all participant records for this user
            participants = await conn.fetch("""
                SELECT * FROM live_audio_room_participants 
                WHERE user_id = $1
            """, user_id)
            
            print(f"Found {len(participants)} participant records:")
            for p in participants:
                print(f"  ID: {p['id']}, Room: {p['room_id']}, Left: {p['left_at']}, Active: {p['is_active']}")
            
            # Check if we have any active participants
            active_participants = await conn.fetch("""
                SELECT * FROM live_audio_room_participants 
                WHERE user_id = $1 AND left_at IS NULL
            """, user_id)
            
            print(f"\nActive participants: {len(active_participants)}")
            
            if active_participants:
                participant = active_participants[0]
                print(f"\nTesting UPDATE with participant: {participant['id']}")
                
                # Set RLS context
                await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
                
                # Test UPDATE
                result = await conn.execute("""
                    UPDATE live_audio_room_participants
                    SET left_at = NOW(), is_active = false
                    WHERE id = $1
                """, participant['id'])
                print(f"UPDATE result: {result}")
                
                # Check result
                after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
                print(f"After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
            else:
                print("No active participants found. Creating one for testing...")
                
                # Create a test room and participant
                room = await conn.fetchrow("SELECT id FROM live_audio_rooms LIMIT 1")
                if room:
                    await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
                    
                    # Join a room
                    join_result = await conn.execute("""
                        INSERT INTO live_audio_room_participants (room_id, user_id, role)
                        VALUES ($1, $2, 'participant')
                    """, room['id'], user_id)
                    print(f"Created participant: {join_result}")
                    
                    # Now test UPDATE
                    new_participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL", user_id)
                    if new_participant:
                        update_result = await conn.execute("""
                            UPDATE live_audio_room_participants
                            SET left_at = NOW(), is_active = false
                            WHERE id = $1
                        """, new_participant['id'])
                        print(f"UPDATE result: {update_result}")
                        
                        after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", new_participant['id'])
                        print(f"After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_data_state())
