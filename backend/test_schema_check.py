"""
Check exact table schema
"""
import asyncio
from app.database.database import database

async def test_schema():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check table columns
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'live_audio_room_participants'
                ORDER BY ordinal_position
            """)
            print("TABLE COLUMNS:")
            for col in columns:
                print(f"  {col['column_name']} - {col['data_type']} - nullable: {col['is_nullable']}")
            
            # Check triggers
            triggers = await conn.fetch("""
                SELECT trigger_name, event_manipulation, action_statement 
                FROM information_schema.triggers 
                WHERE event_object_table = 'live_audio_room_participants'
            """)
            print("\nTRIGGERS:")
            for trigger in triggers:
                print(f"  {trigger['trigger_name']} - {trigger['event_manipulation']}")
                
            # Check constraints
            constraints = await conn.fetch("""
                SELECT constraint_name, constraint_type 
                FROM information_schema.table_constraints 
                WHERE table_name = 'live_audio_room_participants'
            """)
            print("\nCONSTRAINTS:")
            for const in constraints:
                print(f"  {const['constraint_name']} - {const['constraint_type']}")
                
    finally:
        await database.close()

asyncio.run(test_schema())
