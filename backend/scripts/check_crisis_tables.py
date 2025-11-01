#!/usr/bin/env python3
"""
Check crisis tables structure
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_table_structure():
    """Check the structure of crisis tables"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Check crisis_resources columns
        print("\n📋 crisis_resources table structure:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'crisis_resources'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"   - {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        # Check emergency_contacts columns
        print("\n📋 emergency_contacts table structure:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'emergency_contacts'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"   - {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        # Check what data exists
        print("\n🔍 Existing crisis resources:")
        resources = await conn.fetch("SELECT * FROM crisis_resources LIMIT 5")
        for resource in resources:
            print(f"   - {resource}")
        
        print("\n🔍 Existing emergency contacts:")
        contacts = await conn.fetch("SELECT * FROM emergency_contacts LIMIT 5")
        for contact in contacts:
            print(f"   - {contact}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure())
