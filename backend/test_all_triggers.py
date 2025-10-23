"""
Check ALL triggers on the database
"""
import asyncio
from app.database.database import database

async def test_all_triggers():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check ALL triggers in the database
            triggers = await conn.fetch("""
                SELECT 
                    tgname as trigger_name,
                    tgrelid::regclass as table_name,
                    tgfoid::regproc as function_name,
                    tgenabled as enabled,
                    tgtype as trigger_type
                FROM pg_trigger 
                WHERE tgrelid = 'live_audio_room_participants'::regclass
                OR tgname LIKE '%audio%'
            """)
            
            print("ALL RELEVANT TRIGGERS:")
            if not triggers:
                print("  No triggers found")
            for trigger in triggers:
                trigger_type = []
                if trigger['trigger_type'] & 1: trigger_type.append("BEFORE")
                if trigger['trigger_type'] & 2: trigger_type.append("AFTER") 
                if trigger['trigger_type'] & 4: trigger_type.append("INSTEAD OF")
                
                print(f"  {trigger['trigger_name']} on {trigger['table_name']}")
                print(f"    Function: {trigger['function_name']}")
                print(f"    Enabled: {trigger['enabled']}")
                print(f"    Type: {' '.join(trigger_type)}")
                
            # Check if there are any system triggers we're missing
            system_triggers = await conn.fetch("""
                SELECT tgname, tgrelid::regclass, tgfoid::regproc
                FROM pg_trigger 
                WHERE tgname LIKE 'RI_ConstraintTrigger%'
                AND tgrelid = 'live_audio_room_participants'::regclass
            """)
            
            print("\nSYSTEM CONSTRAINT TRIGGERS:")
            for trigger in system_triggers:
                print(f"  {trigger['tgname']} on {trigger['tgrelid']} calls {trigger['tgfoid']}")
                
    finally:
        await database.close()

asyncio.run(test_all_triggers())
