"""
Investigate if the table has unusual properties causing INSTEAD OF triggers
"""
import asyncio
from app.database.database import database

async def investigate_table_origin():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== INVESTIGATING TABLE PROPERTIES ===\n")
            
            # Check table inheritance
            inheritance = await conn.fetch("""
                SELECT inhparent::regclass as parent_table
                FROM pg_inherits 
                WHERE inhrelid = 'live_audio_room_participants'::regclass
            """)
            
            print("TABLE INHERITANCE:")
            if inheritance:
                for inherit in inheritance:
                    print(f"  Inherits from: {inherit['parent_table']}")
            else:
                print("  No inheritance")
            
            # Check if table was created with special options
            table_options = await conn.fetchval("""
                SELECT reloptions 
                FROM pg_class 
                WHERE relname = 'live_audio_room_participants'
            """)
            print(f"Table options: {table_options}")
            
            # Check table access method (should be 'heap' for normal tables)
            access_method = await conn.fetchval("""
                SELECT amname 
                FROM pg_class c
                JOIN pg_am a ON c.relam = a.oid
                WHERE c.relname = 'live_audio_room_participants'
            """)
            print(f"Access method: {access_method}")
            
            # Let's try a different approach - check if we can identify the exact issue
            print("\n=== CHECKING FOR WORKAROUNDS ===\n")
            
            # Since the table seems to have fundamental issues, let's test if we can use
            # the existing working pattern from the join_room method
            test_user_email = "final_test1_13e795af@example.com"
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", test_user_email)
            user_id = user['id']
            
            # Get a room to test with
            room = await conn.fetchrow("SELECT id FROM live_audio_rooms LIMIT 1")
            
            print("Testing INSERT-based approach (like join_room):")
            # The join_room method works by using INSERT - maybe we need a similar pattern for "leaving"
            
            # Since we can't UPDATE, maybe we need to use a different strategy
            print("Since UPDATE doesn't work due to INSTEAD OF triggers, we might need to:")
            print("1. Use INSERT with a 'left' status instead of UPDATE")
            print("2. Recreate the entire table properly")
            print("3. Use application-level logic to track leaving instead of database updates")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(investigate_table_origin())
