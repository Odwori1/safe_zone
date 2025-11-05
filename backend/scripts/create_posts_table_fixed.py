#!/usr/bin/env python3
"""
Script to add image_url column to posts table
Fixes: "column 'image_url' of relation 'posts' does not exist"
"""

import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def add_image_url_column():
    """Add image_url column to posts table"""
    print("🔄 Connecting to database...")
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("🔍 Checking if image_url column exists...")
        
        # Check if column exists
        column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'posts' AND column_name = 'image_url'
            );
        """)
        
        if column_exists:
            print("✅ image_url column already exists")
            return
        
        print("📝 Adding image_url column to posts table...")
        
        # Add the image_url column
        await conn.execute("""
            ALTER TABLE posts 
            ADD COLUMN image_url TEXT;
        """)
        
        print("✅ Successfully added image_url column to posts table")
        
        # Verify the column was added
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'posts' 
            ORDER BY ordinal_position;
        """)
        
        print("📊 Current posts table columns:")
        for col in columns:
            print(f"   - {col['column_name']}: {col['data_type']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()

async def main():
    """Main function"""
    print("🚀 Starting database schema update...")
    print("📋 Task: Add image_url column to posts table")
    
    try:
        await add_image_url_column()
        print("🎉 Database schema update completed successfully!")
    except Exception as e:
        print(f"💥 Failed to update database schema: {e}")

if __name__ == "__main__":
    asyncio.run(main())
