#!/usr/bin/env python3
"""
Convert crisis_resources columns from text to JSONB
"""
import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def convert_columns_to_jsonb():
    """Convert languages and tags columns to JSONB"""
    
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        print("🔧 Converting crisis_resources columns to JSONB...")
        
        # First, let's check the current column types
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'crisis_resources' 
            AND column_name IN ('languages', 'tags')
        """)
        
        print("📋 Current column types:")
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']}")
        
        # Convert languages column to JSONB
        print("\n🔄 Converting languages column...")
        await conn.execute("""
            ALTER TABLE crisis_resources 
            ALTER COLUMN languages TYPE JSONB 
            USING languages::JSONB
        """)
        print("✅ Converted languages to JSONB")
        
        # Convert tags column to JSONB
        print("🔄 Converting tags column...")
        await conn.execute("""
            ALTER TABLE crisis_resources 
            ALTER COLUMN tags TYPE JSONB 
            USING tags::JSONB
        """)
        print("✅ Converted tags to JSONB")
        
        # Verify the conversion
        columns_after = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'crisis_resources' 
            AND column_name IN ('languages', 'tags')
        """)
        
        print("\n📋 New column types:")
        for col in columns_after:
            print(f"   - {col['column_name']}: {col['data_type']}")
        
        # Test that the data is properly converted
        test_data = await conn.fetch("SELECT id, name, languages, tags FROM crisis_resources LIMIT 1")
        if test_data:
            print(f"\n🧪 Test data after conversion:")
            print(f"   - Name: {test_data[0]['name']}")
            print(f"   - Languages: {test_data[0]['languages']} (type: {type(test_data[0]['languages']).__name__})")
            print(f"   - Tags: {test_data[0]['tags']} (type: {type(test_data[0]['tags']).__name__})")
        
        await conn.close()
        print("\n🎉 Column conversion completed successfully!")
        
    except Exception as e:
        print(f"❌ Error converting columns: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(convert_columns_to_jsonb())
