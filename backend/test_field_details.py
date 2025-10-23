"""
Test different UPDATE approaches to isolate the issue
"""
import asyncio
from app.database.database import database

async def test_field_details():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Get participant record
            participant = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE user_id = $1 AND left_at IS NULL LIMIT 1", user_id)
            print(f"Participant ID: {participant['id']}")
            print(f"Current left_at: {participant['left_at']}")
            print(f"Current is_active: {participant['is_active']}")
            
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(user_id))
            
            print("\nTesting different UPDATE approaches:")
            
            # Test 1: Update only left_at
            print("1. Update only left_at:")
            result1 = await conn.execute("UPDATE live_audio_room_participants SET left_at = NOW() WHERE id = $1", participant['id'])
            print(f"   Result: {result1}")
            
            # Test 2: Update only is_active  
            print("2. Update only is_active:")
            result2 = await conn.execute("UPDATE live_audio_room_participants SET is_active = false WHERE id = $1", participant['id'])
            print(f"   Result: {result2}")
            
            # Test 3: Update a different field
            print("3. Update role field:")
            result3 = await conn.execute("UPDATE live_audio_room_participants SET role = 'listener' WHERE id = $1", participant['id'])
            print(f"   Result: {result3}")
            
            # Check final state
            final = await conn.fetchrow("SELECT * FROM live_audio_room_participants WHERE id = $1", participant['id'])
            print(f"\nFinal state - left_at: {final['left_at']}, is_active: {final['is_active']}, role: {final['role']}")
            
    finally:
        await database.close()

asyncio.run(test_field_details())
