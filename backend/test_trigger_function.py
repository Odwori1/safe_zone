"""
Check trigger functions
"""
import asyncio
from app.database.database import database

async def test_triggers():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check for the update_room_participant_count function
            functions = await conn.fetch("""
                SELECT proname, prosrc 
                FROM pg_proc 
                WHERE proname = 'update_room_participant_count'
            """)
            
            print("TRIGGER FUNCTIONS:")
            for func in functions:
                print(f"Function: {func['proname']}")
                print(f"Source: {func['prosrc']}")
            
            # Check triggers again with more detail
            triggers = await conn.fetch("""
                SELECT 
                    tgname as trigger_name,
                    tgrelid::regclass as table_name,
                    tgfoid::regproc as function_name
                FROM pg_trigger 
                WHERE tgrelid = 'live_audio_room_participants'::regclass
            """)
            
            print("\nDETAILED TRIGGERS:")
            for trigger in triggers:
                print(f"Trigger: {trigger['trigger_name']} on {trigger['table_name']} calls {trigger['function_name']}")
                
    finally:
        await database.close()

asyncio.run(test_triggers())
