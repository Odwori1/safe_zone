"""
Check if database triggers are blocking UPDATE operations
"""
import asyncio
from app.database.database import database

async def test_triggers_blocking():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== INVESTIGATING TRIGGERS BLOCKING UPDATES ===\n")
            
            # Check all triggers on the participants table
            triggers = await conn.fetch("""
                SELECT 
                    tgname as trigger_name,
                    tgenabled as enabled,
                    tgtype as trigger_type,
                    tgisinternal as internal,
                    p.proname as function_name
                FROM pg_trigger t
                JOIN pg_proc p ON t.tgfoid = p.oid
                WHERE t.tgrelid = 'live_audio_room_participants'::regclass
            """)
            
            print("ALL TRIGGERS ON live_audio_room_participants:")
            for trigger in triggers:
                trigger_type = []
                if trigger['trigger_type'] & 1: trigger_type.append("BEFORE")
                if trigger['trigger_type'] & 2: trigger_type.append("AFTER") 
                if trigger['trigger_type'] & 4: trigger_type.append("INSTEAD OF")
                if trigger['trigger_type'] & 8: trigger_type.append("ROW")
                if trigger['trigger_type'] & 16: trigger_type.append("INSERT")
                if trigger['trigger_type'] & 32: trigger_type.append("DELETE")
                if trigger['trigger_type'] & 64: trigger_type.append("UPDATE")
                
                print(f"  {trigger['trigger_name']}")
                print(f"    Enabled: {trigger['enabled']}")
                print(f"    Type: {' '.join(trigger_type)}")
                print(f"    Internal: {trigger['internal']}")
                print(f"    Function: {trigger['function_name']}")
                print()
            
            # Check if there are any rules that might be intercepting
            rules = await conn.fetch("""
                SELECT rulename, definition
                FROM pg_rules 
                WHERE tablename = 'live_audio_room_participants'
            """)
            
            print("RULES:")
            if not rules:
                print("  No rules found")
            for rule in rules:
                print(f"  {rule['rulename']}: {rule['definition']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_triggers_blocking())
