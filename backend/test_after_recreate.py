"""
Test if UPDATE works after table recreation
"""
import asyncio
from app.database.database import database

async def test_after_recreate():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== TESTING AFTER TABLE RECREATION ===\n")
            
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            print(f"Testing with participant: {participant['id']}")
            print(f"Current left_at: {participant['left_at']}, role: {participant['role']}")
            
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            # Test the leave_room UPDATE
            print("\n1. Testing leave_room UPDATE:")
            result = await conn.execute("""
                UPDATE live_audio_room_participants
                SET left_at = NOW(), is_active = false
                WHERE id = $1
            """, participant['id'])
            print(f"   Result: {result}")
            
            # Check if it worked
            after = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"   After update - left_at: {after['left_at']}, is_active: {after['is_active']}")
            
            # Test if we can run the original tests
            print("\n2. Running the original room leaving test:")
            from tests.test_room_leaving_fixed import main
            await main()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_after_recreate())
