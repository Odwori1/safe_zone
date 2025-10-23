"""
Check table permissions and locks
"""
import asyncio
from app.database.database import database

async def test_permissions():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check table permissions
            permissions = await conn.fetch("""
                SELECT 
                    table_name,
                    grantee,
                    privilege_type
                FROM information_schema.table_privileges 
                WHERE table_name = 'live_audio_room_participants'
            """)
            
            print("TABLE PERMISSIONS:")
            for perm in permissions:
                print(f"  {perm['grantee']}: {perm['privilege_type']}")
            
            # Check if table is locked
            locks = await conn.fetch("""
                SELECT 
                    relation::regclass as table_name,
                    mode,
                    granted
                FROM pg_locks 
                WHERE relation = 'live_audio_room_participants'::regclass
            """)
            
            print("\nTABLE LOCKS:")
            if not locks:
                print("  No active locks found")
            for lock in locks:
                print(f"  {lock['table_name']}: {lock['mode']} - {'GRANTED' if lock['granted'] else 'WAITING'}")
            
            # Test INSERT to see if that works
            print("\nTesting INSERT operation:")
            try:
                # Get a room and user that exist
                room = await conn.fetchrow("SELECT id FROM live_audio_rooms LIMIT 1")
                user = await conn.fetchrow("SELECT id FROM users WHERE email = 'final_test1_13e795af@example.com'")
                
                if room and user:
                    insert_result = await conn.execute("""
                        INSERT INTO live_audio_room_participants (room_id, user_id, role)
                        VALUES ($1, $2, 'listener')
                    """, room['id'], user['id'])
                    print(f"INSERT result: {insert_result}")
            except Exception as e:
                print(f"INSERT failed: {e}")
                
    finally:
        await database.close()

asyncio.run(test_permissions())
