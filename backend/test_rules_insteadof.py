"""
Check for rules or INSTEAD OF triggers that might intercept UPDATE
"""
import asyncio
from app.database.database import database

async def test_rules():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check for rules
            rules = await conn.fetch("""
                SELECT rulename, definition 
                FROM pg_rules 
                WHERE tablename = 'live_audio_room_participants'
            """)
            
            print("DATABASE RULES:")
            if not rules:
                print("  No rules found")
            for rule in rules:
                print(f"  {rule['rulename']}: {rule['definition']}")
            
            # Check for INSTEAD OF triggers (usually on views)
            instead_of_triggers = await conn.fetch("""
                SELECT tgname, tgtype 
                FROM pg_trigger 
                WHERE tgrelid = 'live_audio_room_participants'::regclass
                AND (tgtype & 4) != 0  -- INSTEAD OF trigger flag
            """)
            
            print("\nINSTEAD OF TRIGGERS:")
            if not instead_of_triggers:
                print("  No INSTEAD OF triggers found")
            for trigger in instead_of_triggers:
                print(f"  {trigger['tgname']}")
                
            # Check if this is actually a view
            is_view = await conn.fetchval("""
                SELECT table_type 
                FROM information_schema.tables 
                WHERE table_name = 'live_audio_room_participants'
            """)
            print(f"\nTable type: {is_view}")
            
    finally:
        await database.close()

asyncio.run(test_rules())
