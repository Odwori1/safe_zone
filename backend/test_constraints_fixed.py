"""
Check constraints with correct query
"""
import asyncio
from app.database.database import database

async def test_constraints():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Get detailed info about the constraint triggers
            constraints = await conn.fetch("""
                SELECT 
                    conname as constraint_name,
                    contype as constraint_type,
                    pg_get_constraintdef(oid) as definition
                FROM pg_constraint 
                WHERE conrelid = 'live_audio_room_participants'::regclass
            """)
            
            print("TABLE CONSTRAINTS:")
            for const in constraints:
                print(f"  {const['constraint_name']} ({const['constraint_type']}): {const['definition']}")
            
            # Check if there are any check constraints that might block the update
            check_constraints = await conn.fetch("""
                SELECT conname, pg_get_constraintdef(oid) as definition
                FROM pg_constraint 
                WHERE conrelid = 'live_audio_room_participants'::regclass 
                AND contype = 'c'
            """)
            
            print("\nCHECK CONSTRAINTS:")
            if not check_constraints:
                print("  No check constraints found")
            for check in check_constraints:
                print(f"  {check['conname']}: {check['definition']}")
                
    finally:
        await database.close()

asyncio.run(test_constraints())
