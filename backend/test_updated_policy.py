"""
Test the UPDATE policy after adding it
"""
import asyncio
from app.database.database import database

async def test_updated_policy():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== TESTING AFTER ADDING UPDATE POLICY ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            print(f"Testing with participant: {participant['id']}")
            print(f"Current left_at: {participant['left_at']}")
            
            # Check the exact policy that was created
            print("\n1. Checking UPDATE policy details:")
            update_policy = await conn.fetchrow("""
                SELECT policyname, qual, with_check
                FROM pg_policies 
                WHERE tablename = 'live_audio_room_participants' 
                AND cmd = 'UPDATE'
            """)
            print(f"   Policy: {update_policy['policyname']}")
            print(f"   Qual: {update_policy['qual']}")
            print(f"   With Check: {update_policy['with_check']}")
            
            # Test UPDATE with proper RLS context
            print("\n2. Testing UPDATE with RLS context:")
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            result = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"   UPDATE result: {result}")
            
            # Check if the update actually happened
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"   After update - left_at: {after['left_at']}")
            
            # Test a simpler UPDATE to isolate the issue
            print("\n3. Testing simpler UPDATE (changing role):")
            result2 = await conn.execute("UPDATE live_audio_room_participants SET role = 'listener' WHERE id = $1", participant['id'])
            print(f"   Simple UPDATE result: {result2}")
            
            after2 = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"   After simple update - role: {after2['role']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_updated_policy())
