#!/usr/bin/env python3
"""
Final schema fix to match Pydantic models
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def fix_schema_final():
    """Fix schema to match Pydantic models exactly"""
    try:
        await database.connect()
        print("✅ Database connected")
        
        async with database.pool.acquire() as conn:
            # Check current columns
            print("📋 Current columns:")
            columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            
            for col in columns:
                print(f"   - {col['column_name']}")
            
            # Rename user_type to role
            print("\n🔄 Renaming user_type to role...")
            try:
                await conn.execute("ALTER TABLE users RENAME COLUMN user_type TO role;")
                print("✅ Renamed user_type to role")
            except Exception as e:
                print(f"⚠️ Rename user_type: {e}")
            
            # Add is_verified column
            print("\n➕ Adding is_verified column...")
            try:
                await conn.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT false;")
                print("✅ Added is_verified column")
            except Exception as e:
                print(f"⚠️ Add is_verified: {e}")
            
            # Update existing records to have default values
            print("\n🔄 Setting default values for existing users...")
            await conn.execute("""
                UPDATE users 
                SET role = COALESCE(role, 'seeker'),
                    is_verified = COALESCE(is_verified, false)
                WHERE role IS NULL OR is_verified IS NULL;
            """)
            print("✅ Set default values for existing users")
            
            # Verify final structure
            print("\n📋 Final table structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']})")
            
            # Verify a sample user has all required fields
            sample_user = await conn.fetchrow("SELECT * FROM users LIMIT 1;")
            if sample_user:
                print(f"\n👤 Sample user fields: {list(sample_user.keys())}")
            
        print("🎉 Schema fixed successfully!")
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        raise
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(fix_schema_final())
