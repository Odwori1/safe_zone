"""
Test if the missing UPDATE policy is indeed the root cause
"""
import asyncio
from app.database.database import database

async def test_policy_hypothesis():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # First, let's temporarily disable RLS to confirm our hypothesis
            print("=== TESTING RLS HYPOTHESIS ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 LIMIT 1", user_id)
            
            print("1. Testing with RLS ENABLED (current state):")
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            result1 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"   Result: {result1}")
            
            # We can't disable RLS without superuser privileges, but we can verify the policy is missing
            print("\n2. Confirming missing UPDATE policy:")
            update_policy_exists = await conn.fetchval("""
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'live_audio_room_participants' 
                AND cmd = 'UPDATE'
            """)
            print(f"   UPDATE policy exists: {update_policy_exists is not None}")
            
            print("\n3. The fix should be to add this policy:")
            print("   CREATE POLICY live_audio_room_participants_update_policy ON live_audio_room_participants")
            print("   FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_policy_hypothesis())
