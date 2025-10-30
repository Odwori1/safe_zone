#!/usr/bin/env python3
"""
Fix mood tracking constraints - detailed approach
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_mood_constraints_detailed():
    """Fix the mood tracking constraints with detailed approach"""
    
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5433')),
        'database': os.getenv('DB_NAME', 'safe_zone'),
        'user': 'postgres',
        'password': '0791486006@safezone'
    }

    print("🔧 Fixing mood tracking constraints with detailed approach...")

    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")

        # First, let's check if constraints already exist
        print("\n📋 Checking existing constraints...")
        existing_constraints = await conn.fetch("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'mood_entries' AND constraint_type = 'CHECK';
        """)
        
        for constraint in existing_constraints:
            print(f"   - Existing constraint: {constraint['constraint_name']}")

        # Drop only the specific constraints we want to replace
        print("\n🗑️ Dropping target constraints if they exist...")
        constraints_to_drop = [
            'valid_source_type',
            'sleep_quality_range', 
            'energy_level_range'
        ]
        
        for constraint_name in constraints_to_drop:
            try:
                await conn.execute(f"ALTER TABLE mood_entries DROP CONSTRAINT IF EXISTS {constraint_name};")
                print(f"✅ Dropped {constraint_name} constraint")
            except Exception as e:
                print(f"⚠️ Could not drop {constraint_name}: {e}")

        # Now add the constraints with proper syntax
        print("\n🔒 Adding new constraints...")
        
        # For source_type - only allow specific values when not NULL
        try:
            await conn.execute("""
                ALTER TABLE mood_entries 
                ADD CONSTRAINT valid_source_type 
                CHECK (source_type IS NULL OR source_type IN ('post', 'journal', 'standalone'));
            """)
            print("✅ Added valid_source_type constraint")
        except Exception as e:
            print(f"❌ Could not add valid_source_type: {e}")

        # For sleep_quality - only validate when not NULL
        try:
            await conn.execute("""
                ALTER TABLE mood_entries 
                ADD CONSTRAINT sleep_quality_range 
                CHECK (sleep_quality IS NULL OR (sleep_quality >= 1 AND sleep_quality <= 10));
            """)
            print("✅ Added sleep_quality_range constraint")
        except Exception as e:
            print(f"❌ Could not add sleep_quality_range: {e}")

        # For energy_level - only validate when not NULL
        try:
            await conn.execute("""
                ALTER TABLE mood_entries 
                ADD CONSTRAINT energy_level_range 
                CHECK (energy_level IS NULL OR (energy_level >= 1 AND energy_level <= 10));
            """)
            print("✅ Added energy_level_range constraint")
        except Exception as e:
            print(f"❌ Could not add energy_level_range: {e}")

        # Verify constraints were added
        print("\n📋 Final constraints check...")
        final_constraints = await conn.fetch("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'mood_entries' AND constraint_type = 'CHECK'
            ORDER BY constraint_name;
        """)
        
        print("Final constraints on mood_entries:")
        for constraint in final_constraints:
            print(f"   - {constraint['constraint_name']}")

        print("🎉 Mood tracking constraints fix completed!")

    except Exception as e:
        print(f"❌ Error fixing constraints: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_mood_constraints_detailed())
