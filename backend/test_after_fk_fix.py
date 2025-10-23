"""
Test if UPDATE operations work after fixing foreign key constraints
"""
import asyncio
from app.database.database import database

async def test_after_fk_fix():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== TESTING AFTER FOREIGN KEY FIX ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            print(f"Testing with participant: {participant['id']}")
            print(f"Current left_at: {participant['left_at']}")
            
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Test the leave_room UPDATE
            print("\n1. Testing leave_room UPDATE:")
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE room_id = $1 AND user_id = $2 AND left_at IS NULL
            """, participant['room_id'], user_id)
            print(f"   Result: {result}")
            
            # Check if it worked
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"   After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
            # Test a simple UPDATE
            print("\n2. Testing simple UPDATE:")
            result2 = await conn.execute("UPDATE live_audio_room_participants SET role = 'listener' WHERE id = $1", participant['id'])
            print(f"   Result: {result2}")
            
            after2 = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"   After update - role: {after2['role']}")
            
            # Check if triggers were recreated correctly
            print("\n3. Checking trigger types after fix:")
            triggers = await conn.fetch("""
                SELECT tgname, 
                    CASE WHEN tgtype & 4 != 0 THEN 'INSTEAD OF' ELSE 'NORMAL' END as trigger_type
                FROM pg_trigger 
                WHERE tgrelid = 'live_audio_room_participants'::regclass
            """)
            
            for trigger in triggers:
                print(f"   {trigger['tgname']}: {trigger['trigger_type']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_after_fk_fix())
