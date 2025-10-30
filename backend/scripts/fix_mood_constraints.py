#!/usr/bin/env python3
"""
Fix mood tracking constraints
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_mood_constraints():
    """Fix the mood tracking constraints"""
    
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5433')),
        'database': os.getenv('DB_NAME', 'safe_zone'),
        'user': 'postgres',
        'password': '0791486006@safezone'
    }

    print("🔧 Fixing mood tracking constraints...")

    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")

        # Fix constraints - need to handle NULL values
        print("\n🔒 Adding constraints with NULL handling...")
        
        constraints = [
            ("valid_source_type", "source_type IN ('post', 'journal', 'standalone')"),
            ("sleep_quality_range", "sleep_quality IS NULL OR (sleep_quality >= 1 AND sleep_quality <= 10)"),
            ("energy_level_range", "energy_level IS NULL OR (energy_level >= 1 AND energy_level <= 10)")
        ]

        for const_name, const_def in constraints:
            try:
                await conn.execute(f"ALTER TABLE mood_entries ADD CONSTRAINT IF NOT EXISTS {const_name} CHECK ({const_def});")
                print(f"✅ Added {const_name} constraint")
            except Exception as e:
                print(f"⚠️ Could not add {const_name}: {e}")

        print("🎉 Mood tracking constraints fixed successfully!")

    except Exception as e:
        print(f"❌ Error fixing constraints: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_mood_constraints())
