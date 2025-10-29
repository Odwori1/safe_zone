#!/usr/bin/env python3
"""
Fix journals mood constraint to allow any mood values
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_journals_mood_constraint():
    """Remove or update the mood constraint on journals table"""
    
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5433')),
        'database': os.getenv('DB_NAME', 'safe_zone'),
        'user': 'postgres',
        'password': '0791486006@safezone'
    }
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected as postgres superuser")
        
        # Check existing constraints
        constraints = await conn.fetch("""
            SELECT constraint_name, constraint_type, check_clause
            FROM information_schema.table_constraints 
            JOIN information_schema.check_constraints 
            USING (constraint_name)
            WHERE table_name = 'journals' AND constraint_name LIKE '%mood%';
        """)
        
        print("📋 Current mood constraints:")
        for const in constraints:
            print(f"   - {const['constraint_name']}: {const['check_clause']}")
        
        # Drop the restrictive mood constraint
        await conn.execute("ALTER TABLE journals DROP CONSTRAINT IF EXISTS journals_mood_check;")
        print("✅ Dropped restrictive mood constraint")
        
        # Add a more permissive constraint if needed (or leave it without constraint)
        await conn.execute("""
            ALTER TABLE journals 
            ADD CONSTRAINT journals_mood_length 
            CHECK (mood IS NULL OR length(mood) <= 50);
        """)
        print("✅ Added permissive mood length constraint")
        
        # Verify the fix
        remaining_constraints = await conn.fetch("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'journals';
        """)
        
        print("\n📋 Remaining journals constraints:")
        for const in remaining_constraints:
            print(f"   - {const['constraint_name']} ({const['constraint_type']})")
        
        await conn.close()
        print("\n🎉 Journals mood constraint fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_journals_mood_constraint())
