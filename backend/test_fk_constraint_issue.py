"""
Investigate foreign key constraint issues causing INSTEAD OF triggers
"""
import asyncio
from app.database.database import database

async def test_fk_constraint_issue():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            print("=== INVESTIGATING FOREIGN KEY CONSTRAINT ISSUES ===\n")
            
            # Get detailed foreign key information
            fk_info = await conn.fetch("""
                SELECT 
                    conname as constraint_name,
                    conrelid::regclass as table_name,
                    confrelid::regclass as referenced_table,
                    confupdtype as update_action,
                    confdeltype as delete_action,
                    conkey as local_columns,
                    confkey as foreign_columns
                FROM pg_constraint
                WHERE conrelid = 'live_audio_room_participants'::regclass
                AND contype = 'f'
            """)
            
            print("FOREIGN KEY CONSTRAINTS:")
            for fk in fk_info:
                print(f"Constraint: {fk['constraint_name']}")
                print(f"Table: {fk['table_name']}")
                print(f"References: {fk['referenced_table']}")
                print(f"On Update: {fk['update_action']}")
                print(f"On Delete: {fk['delete_action']}")
                print()
            
            # Check if there are any constraint violations
            print("CHECKING FOR CONSTRAINT VIOLATIONS:")
            
            # Check room_id foreign key
            room_violations = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM live_audio_room_participants p
                WHERE NOT EXISTS (
                    SELECT 1 FROM live_audio_rooms r WHERE r.id = p.room_id
                )
            """)
            print(f"Invalid room_id references: {room_violations}")
            
            # Check user_id foreign key  
            user_violations = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM live_audio_room_participants p
                WHERE NOT EXISTS (
                    SELECT 1 FROM users u WHERE u.id = p.user_id
                )
            """)
            print(f"Invalid user_id references: {user_violations}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_fk_constraint_issue())
