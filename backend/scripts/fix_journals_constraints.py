#!/usr/bin/env python3
"""
Fix the missing constraints for journals table
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_journals_constraints():
    """Add missing constraints to journals table"""
    
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
        
        # Add mood_intensity constraint (without IF NOT EXISTS)
        try:
            await conn.execute("""
                ALTER TABLE journals 
                ADD CONSTRAINT mood_intensity_range 
                CHECK (mood_intensity >= 1 AND mood_intensity <= 10);
            """)
            print("✅ Added mood_intensity_range constraint")
        except Exception as e:
            print(f"⚠️ mood_intensity constraint already exists: {e}")
        
        # Add journal status constraint (without IF NOT EXISTS)
        try:
            await conn.execute("""
                ALTER TABLE journals 
                ADD CONSTRAINT valid_journal_status 
                CHECK (status IN ('active', 'archived', 'deleted'));
            """)
            print("✅ Added valid_journal_status constraint")
        except Exception as e:
            print(f"⚠️ status constraint already exists: {e}")
        
        # Add foreign key constraint (without IF NOT EXISTS)
        try:
            await conn.execute("""
                ALTER TABLE journals 
                ADD CONSTRAINT journals_prompt_id_fkey 
                FOREIGN KEY (prompt_id) REFERENCES journal_prompts(id);
            """)
            print("✅ Added prompt_id foreign key constraint")
        except Exception as e:
            print(f"⚠️ Foreign key constraint already exists: {e}")
        
        # Verify constraints were added
        constraints = await conn.fetch("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'journals';
        """)
        print("\n📋 Current journals constraints:")
        for const in constraints:
            print(f"   - {const['constraint_name']} ({const['constraint_type']})")
        
        await conn.close()
        print("\n🎉 Journals constraints fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_journals_constraints())
