"""
Test if RLS policies are interfering with UPDATE operations
"""
import asyncio
from app.database.database import database

async def test_rls_interference():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            print("=== TESTING UPDATE WITH DIFFERENT RLS CONTEXTS ===\n")
            
            # Test 1: Without any RLS context (superuser-like)
            print("1. Testing WITHOUT RLS context:")
            participant = await conn.fetchrow("SELECT id FROM live_audio_room_participants WHERE user_id = $1 LIMIT 1", user_id)
            result1 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"   Result: {result1}")
            
            # Test 2: With RLS context set to the correct user
            print("2. Testing WITH correct user RLS context:")
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            result2 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"   Result: {result2}")
            
            # Test 3: With RLS context set to a different user (should fail due to RLS)
            print("3. Testing WITH different user RLS context:")
            different_user = await conn.fetchrow("SELECT id FROM users WHERE id != $1 LIMIT 1", user_id)
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(different_user['id']))
            result3 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"   Result: {result3}")
            
            # Test 4: Check if we can update a field that doesn't have RLS restrictions
            print("4. Testing UPDATE on non-RLS restricted operation:")
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Try creating a new room (INSERT should work based on our earlier tests)
            room_result = await conn.execute("""
                INSERT INTO live_audio_rooms (title, created_by, is_public)
                VALUES ('Test Room', $1, true)
            """, user_id)
            print(f"   Room INSERT result: {room_result}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_rls_interference())
