"""
Check for missing triggers
"""
import asyncio
from app.database.database import database

async def test_missing_triggers():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check all triggers on the participants table
            triggers = await conn.fetch("""
                SELECT trigger_name, action_timing, event_manipulation
                FROM information_schema.triggers 
                WHERE event_object_table = 'live_audio_room_participants'
            """)
            
            print("CURRENT TRIGGERS:")
            if not triggers:
                print("  No triggers found!")
            for trigger in triggers:
                print(f"  {trigger['trigger_name']} - {trigger['action_timing']} {trigger['event_manipulation']}")
            
            # Check if the specific triggers from create_live_audio_rooms.sql exist
            expected_triggers = [
                'update_participant_count_on_join',
                'update_participant_count_on_leave'
            ]
            
            print("\nCHECKING EXPECTED TRIGGERS:")
            for expected in expected_triggers:
                exists = await conn.fetchval("""
                    SELECT 1 FROM information_schema.triggers 
                    WHERE trigger_name = $1
                """, expected)
                print(f"  {expected}: {'EXISTS' if exists else 'MISSING'}")
                
    finally:
        await database.close()

asyncio.run(test_missing_triggers())
