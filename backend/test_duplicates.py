"""
Check for duplicate participant entries
"""
import asyncio
from app.database.database import database

async def test_duplicates():
    await database.connect()
    
    test_user_email = "final_test1_13e795af@example.com"
    
    try:
        async with database.pool.acquire() as conn:
            # Get test user
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            print(f"User: {user_id}")
            
            # Check ALL participant records for this user
            participants = await conn.fetch("""
                SELECT * FROM live_audio_room_participants 
                WHERE user_id = $1
                ORDER BY joined_at DESC
            """, user_id)
            
            print(f"Found {len(participants)} participant records:")
            for p in participants:
                print(f"  ID: {p['id']}, Room: {p['room_id']}, Left: {p['left_at']}, Active: {p['is_active']}")
            
            # Check if there are multiple active entries for same room
            duplicates = await conn.fetch("""
                SELECT room_id, COUNT(*) as count
                FROM live_audio_room_participants 
                WHERE user_id = $1 AND left_at IS NULL
                GROUP BY room_id 
                HAVING COUNT(*) > 1
            """, user_id)
            
            print(f"\nDuplicate active entries: {len(duplicates)}")
            for dup in duplicates:
                print(f"  Room: {dup['room_id']}, Count: {dup['count']}")
                
    finally:
        await database.close()

asyncio.run(test_duplicates())
