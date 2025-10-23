"""
Check if this is actually a view with INSTEAD OF triggers
"""
import asyncio
from app.database.database import database

async def test_view():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check if it's a view
            table_info = await conn.fetchrow("""
                SELECT 
                    table_name,
                    table_type,
                    is_insertable_into
                FROM information_schema.tables 
                WHERE table_name = 'live_audio_room_participants'
            """)
            
            print(f"Table: {table_info['table_name']}")
            print(f"Type: {table_info['table_type']}")
            print(f"Insertable: {table_info['is_insertable_into']}")
            
            # Check view definition if it's a view
            if table_info['table_type'] == 'VIEW':
                view_def = await conn.fetchval("""
                    SELECT definition 
                    FROM pg_views 
                    WHERE viewname = 'live_audio_room_participants'
                """)
                print(f"View definition: {view_def}")
            
            # Check the actual table definition
            table_def = await conn.fetchval("""
                SELECT pg_get_tabledef('live_audio_room_participants'::regclass)
            """)
            print(f"\nTable definition:\n{table_def}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_view())
