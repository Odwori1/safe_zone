"""
Get proper table definition
"""
import asyncio
from app.database.database import database

async def test_table_def():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Get table definition using a different approach
            table_def = await conn.fetchval("""
                SELECT 'CREATE TABLE ' || relname || E'\\n(' || 
                       array_to_string(
                           array_agg(
                               '    ' || column_name || ' ' || type || 
                               case when not null then ' not null' else '' end
                           ), 
                           E',\\n'
                       ) || E'\\n);'
                FROM (
                    SELECT 
                        c.relname,
                        a.attname AS column_name,
                        pg_catalog.format_type(a.atttypid, a.atttypmod) AS type,
                        a.attnotnull AS not_null
                    FROM pg_class c
                    JOIN pg_attribute a ON a.attrelid = c.oid
                    WHERE c.relname = 'live_audio_room_participants'
                    AND a.attnum > 0
                    AND NOT a.attisdropped
                    ORDER BY a.attnum
                ) AS t
                GROUP BY relname
            """)
            
            print("TABLE DEFINITION:")
            print(table_def)
            
            # Check if there are any rules that might be causing INSTEAD OF behavior
            rules = await conn.fetch("""
                SELECT 
                    schemaname,
                    tablename,
                    rulename,
                    definition
                FROM pg_rules
                WHERE tablename = 'live_audio_room_participants'
            """)
            
            print("\nRULES:")
            if not rules:
                print("  No rules found")
            for rule in rules:
                print(f"  {rule['rulename']}: {rule['definition']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_table_def())
