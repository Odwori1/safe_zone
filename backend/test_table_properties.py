"""
Check if the problematic tables have special properties or are actually views
"""
import asyncio
from app.database.database import database

async def test_table_props():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check both problematic tables
            tables = ['live_audio_rooms', 'live_audio_room_participants']
            
            for table_name in tables:
                print(f"\n=== {table_name} ===")
                
                # Check basic table info
                info = await conn.fetchrow("""
                    SELECT 
                        table_name,
                        table_type,
                        is_insertable_into,
                        is_updatable
                    FROM information_schema.tables 
                    WHERE table_name = $1
                """, table_name)
                
                if info:
                    print(f"Table type: {info['table_type']}")
                    print(f"Insertable: {info['is_insertable_into']}")
                    print(f"Updatable: {info['is_updatable']}")
                
                # Check if it has INSTEAD OF triggers
                triggers = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM pg_trigger 
                    WHERE tgrelid = $1::regclass
                    AND (tgtype & 4) != 0  -- INSTEAD OF triggers
                """, table_name)
                
                print(f"INSTEAD OF triggers: {triggers}")
                
                # Check table owner
                owner = await conn.fetchval("""
                    SELECT relowner::regrole 
                    FROM pg_class 
                    WHERE relname = $1
                """, table_name)
                
                print(f"Table owner: {owner}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_table_props())
