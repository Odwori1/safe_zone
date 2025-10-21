import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_schema():
    try:
        # Use the same connection method as the app
        from app.core.config import settings
        conn = await asyncpg.connect(settings.database_url)
        
        print("📊 CHECKING CURRENT DATABASE SCHEMA")
        print("=" * 50)
        
        # Check if file_uploads table exists and has RLS
        table_info = await conn.fetchrow("""
            SELECT 
                table_name,
                row_level_security
            FROM information_schema.tables 
            WHERE table_name = 'file_uploads'
        """)
        
        if table_info:
            print(f"✅ file_uploads table exists")
            print(f"   - RLS enabled: {table_info['row_level_security']}")
            
            # Check columns
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'file_uploads'
                ORDER BY ordinal_position
            """)
            
            print("   - Columns:")
            for col in columns:
                print(f"     {col['column_name']} ({col['data_type']})")
                
            # Check for user_id column (critical for RLS)
            has_user_id = any(col['column_name'] == 'user_id' for col in columns)
            if has_user_id:
                print("   ✅ user_id column exists (required for RLS)")
            else:
                print("   ❌ user_id column missing (RLS will not work)")
                
        else:
            print("❌ file_uploads table not found")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

asyncio.run(check_schema())
