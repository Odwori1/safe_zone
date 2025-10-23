"""
Systematically investigate what the INSTEAD OF triggers are doing
"""
import asyncio
from app.database.database import database

async def test_trigger_behavior():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # First, let's understand exactly what these triggers are
            print("=== INVESTIGATING INSTEAD OF TRIGGERS ===\n")
            
            # Get the exact trigger definitions
            triggers = await conn.fetch("""
                SELECT 
                    t.tgname as trigger_name,
                    c.relname as table_name,
                    p.proname as function_name,
                    CASE 
                        WHEN t.tgtype & 1 > 0 THEN 'BEFORE'
                        WHEN t.tgtype & 2 > 0 THEN 'AFTER' 
                        WHEN t.tgtype & 4 > 0 THEN 'INSTEAD OF'
                    END as timing,
                    CASE 
                        WHEN t.tgtype & 16 > 0 THEN 'INSERT'
                        WHEN t.tgtype & 32 > 0 THEN 'DELETE'
                        WHEN t.tgtype & 64 > 0 THEN 'UPDATE'
                    END as operation
                FROM pg_trigger t
                JOIN pg_class c ON t.tgrelid = c.oid
                JOIN pg_proc p ON t.tgfoid = p.oid
                WHERE c.relname IN ('live_audio_rooms', 'live_audio_room_participants')
                AND (t.tgtype & 4) != 0  -- INSTEAD OF triggers
            """)
            
            print("INSTEAD OF TRIGGERS FOUND:")
            for trigger in triggers:
                print(f"  Table: {trigger['table_name']}")
                print(f"  Trigger: {trigger['trigger_name']}")
                print(f"  Timing: {trigger['timing']}")
                print(f"  Operation: {trigger['operation']}")
                print(f"  Function: {trigger['function_name']}")
                print()
            
            # Let's check if these are normal foreign key triggers
            print("=== CHECKING IF THIS IS NORMAL BEHAVIOR ===\n")
            
            # Check other tables with foreign keys to see if they have similar triggers
            other_fk_tables = await conn.fetch("""
                SELECT 
                    c.relname as table_name,
                    COUNT(t.tgname) as instead_of_triggers
                FROM pg_class c
                LEFT JOIN pg_trigger t ON c.oid = t.tgrelid AND (t.tgtype & 4) != 0
                WHERE c.relname IN ('users', 'posts', 'comments')  -- Other tables with FKs
                GROUP BY c.relname
            """)
            
            print("INSTEAD OF TRIGGERS ON OTHER TABLES:")
            for table in other_fk_tables:
                print(f"  {table['table_name']}: {table['instead_of_triggers']} INSTEAD OF triggers")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_trigger_behavior())
