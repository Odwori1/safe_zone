#!/usr/bin/env python3
"""
Check ALL crisis tables structure to see what actually exists
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_all_crisis_tables():
    """Check the structure of all crisis tables"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        crisis_tables = [
            'safety_plans',
            'wellness_checkins', 
            'crisis_alerts',
            'user_crisis_preferences'
        ]
        
        for table in crisis_tables:
            print(f"\n📋 {table} table structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table)
            
            if not columns:
                print(f"   Table '{table}' does not exist or has no columns")
                continue
                
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
            
            # Show sample data if any exists
            sample_data = await conn.fetch(f"SELECT * FROM {table} LIMIT 1")
            if sample_data:
                print(f"   Sample row: {dict(sample_data[0]) if sample_data else 'No data'}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_all_crisis_tables())
