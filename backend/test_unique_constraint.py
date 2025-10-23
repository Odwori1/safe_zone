"""
Test if the UNIQUE constraint is blocking updates
"""
import asyncio
from app.database.database import database

async def test_unique():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Check for duplicate room_id + user_id combinations
            duplicates = await conn.fetch("""
                SELECT room_id, user_id, COUNT(*) as count
                FROM live_audio_room_participants 
                WHERE user_id = $1
                GROUP BY room_id, user_id
                HAVING COUNT(*) > 1
            """, user_id)
            
            print("DUPLICATE CHECK:")
            if duplicates:
                print("  Found duplicates (this would violate UNIQUE constraint):")
                for dup in duplicates:
                    print(f"    Room: {dup['room_id']}, Count: {dup['count']}")
            else:
                print("  No duplicates found")
            
            # Test if we can insert a new record for the same room+user
            room = await conn.fetchrow("SELECT room_id FROM live_audio_room_participants WHERE user_id = $1 LIMIT 1", user_id)
            room_id = room['room_id']
            
            print(f"\nTesting UNIQUE constraint for room {room_id}, user {user_id}:")
            
            # Try to insert a duplicate (should fail)
            try:
                result = await conn.execute("""
                    INSERT INTO live_audio_room_participants (room_id, user_id, role)
                    VALUES ($1, $2, 'participant')
                """, room_id, user_id)
                print(f"  INSERT result: {result}")
            except Exception as e:
                print(f"  INSERT failed (expected): {e}")
            
    finally:
        await database.close()

asyncio.run(test_unique())
