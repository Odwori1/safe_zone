"""
Get detailed information about the INSTEAD OF triggers
"""
import asyncio
from app.database.database import database

async def test_trigger_details():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Get detailed trigger information
            triggers = await conn.fetch("""
                SELECT 
                    tgname,
                    tgenabled,
                    tgtype,
                    tgisinternal
                FROM pg_trigger 
                WHERE tgrelid = 'live_audio_room_participants'::regclass
                AND (tgtype & 4) != 0  -- INSTEAD OF triggers
            """)
            
            print("INSTEAD OF TRIGGER DETAILS:")
            for trigger in triggers:
                print(f"Trigger: {trigger['tgname']}")
                print(f"Enabled: {trigger['tgenabled']}")
                print(f"Internal: {trigger['tgisinternal']}")
                print("---")
            
            # Check the actual function being called by these triggers
            trigger_funcs = await conn.fetch("""
                SELECT 
                    t.tgname as trigger_name,
                    p.proname as function_name,
                    p.prosrc as function_source
                FROM pg_trigger t
                JOIN pg_proc p ON t.tgfoid = p.oid
                WHERE t.tgrelid = 'live_audio_room_participants'::regclass
                AND (t.tgtype & 4) != 0
            """)
            
            print("\nTRIGGER FUNCTIONS:")
            for func in trigger_funcs:
                print(f"Trigger: {func['trigger_name']}")
                print(f"Function: {func['function_name']}")
                print(f"Source: {func['function_source'][:200]}...")  # First 200 chars
                print("---")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_trigger_details())
