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
                    tgisinternal,
                    tgconstrname,
                    tgconstrrelid::regclass as constraint_table
                FROM pg_trigger 
                WHERE tgrelid = 'live_audio_room_participants'::regclass
                AND (tgtype & 4) != 0  -- INSTEAD OF triggers
            """)
            
            print("INSTEAD OF TRIGGER DETAILS:")
            for trigger in triggers:
                print(f"Trigger: {trigger['tgname']}")
                print(f"Enabled: {trigger['tgenabled']}")
                print(f"Internal: {trigger['tgisinternal']}")
                print(f"Constraint: {trigger['tgconstrname']}")
                print(f"Constraint Table: {trigger['constraint_table']}")
                print("---")
            
            # Check if these are related to foreign key constraints
            fk_constraints = await conn.fetch("""
                SELECT 
                    conname,
                    contype,
                    confrelid::regclass as referenced_table,
                    confupdtype,
                    confdeltype
                FROM pg_constraint
                WHERE conrelid = 'live_audio_room_participants'::regclass
                AND contype = 'f'
            """)
            
            print("\nFOREIGN KEY CONSTRAINTS:")
            for fk in fk_constraints:
                print(f"Constraint: {fk['conname']}")
                print(f"Referenced table: {fk['referenced_table']}")
                print(f"On update: {fk['confupdtype']}")
                print(f"On delete: {fk['confdeltype']}")
                print("---")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_trigger_details())
