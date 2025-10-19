#!/usr/bin/env python3
"""
Update database schema to match current code
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def update_schema():
    """Add missing columns to users table"""
    try:
        await database.connect()
        print("✅ Database connected")
        
        async with database.pool.acquire() as conn:
            # Check current table structure
            print("📋 Current table structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']})")
            
            # Add missing columns
            print("\n🔧 Adding missing columns...")
            
            # Check and add full_name column
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(255);")
                print("✅ Added full_name column")
            except Exception as e:
                print(f"⚠️ full_name column: {e}")
            
            # Check and add timezone column  
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';")
                print("✅ Added timezone column")
            except Exception as e:
                print(f"⚠️ timezone column: {e}")
            
            # Check and add locale column
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN locale VARCHAR(10) DEFAULT 'en-US';")
                print("✅ Added locale column")
            except Exception as e:
                print(f"⚠️ locale column: {e}")
            
            # Check and add last_login column
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMPTZ;")
                print("✅ Added last_login column")
            except Exception as e:
                print(f"⚠️ last_login column: {e}")
            
            # Verify the updated structure
            print("\n📋 Updated table structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']})")
            
        print("🎉 Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        raise
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(update_schema())
