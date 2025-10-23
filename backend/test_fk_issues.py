"""
Check for foreign key constraint issues
"""
import asyncio
from app.database.database import database

async def test_fk_issues():
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Check for any constraint violations that might be causing issues
            fk_violations = await conn.fetch("""
                SELECT 
                    c.conname as constraint_name,
                    c.contype as constraint_type,
                    c.confrelid::regclass as referenced_table
                FROM pg_constraint c
                WHERE c.conrelid = 'live_audio_room_participants'::regclass
                AND c.contype = 'f'
            """)
            
            print("FOREIGN KEY CONSTRAINTS:")
            for fk in fk_violations:
                print(f"Constraint: {fk['constraint_name']}")
                print(f"Type: {fk['constraint_type']}")
                print(f"References: {fk['referenced_table']}")
                
                # Check if there are any violations for this constraint
                violations = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM live_audio_room_participants p
                    WHERE NOT EXISTS (
                        SELECT 1 FROM $1 r WHERE r.id = p.room_id
                    )
                """, fk['referenced_table'])
                print(f"Violations: {violations}")
                print("---")
            
            # Check if we can identify why INSTEAD OF triggers exist
            print("\nChecking for unusual table properties...")
            
            # Check table inheritance
            inheritance = await conn.fetch("""
                SELECT inhparent::regclass as parent_table
                FROM pg_inherits 
                WHERE inhrelid = 'live_audio_room_participants'::regclass
            """)
            
            if inheritance:
                print("TABLE INHERITANCE:")
                for inherit in inheritance:
                    print(f"  Parent: {inherit['parent_table']}")
            else:
                print("  No table inheritance found")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_fk_issues())
