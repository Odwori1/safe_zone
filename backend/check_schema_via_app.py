import asyncio
import sys
import os

# Add the app directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def check_schema():
    try:
        from app.database.database import database
        from app.core.config import settings
        
        print("📊 CHECKING DATABASE SCHEMA VIA APPLICATION")
        print("=" * 50)
        
        # Initialize database connection using app's method
        await database.connect()
        
        # Check file_uploads table
        result = await database.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'file_uploads'
            )
        """)
        
        if result:
            print("✅ file_uploads table exists")
            
            # Check RLS
            rls_enabled = await database.fetchval("""
                SELECT row_level_security 
                FROM information_schema.tables 
                WHERE table_name = 'file_uploads'
            """)
            print(f"   - RLS enabled: {rls_enabled}")
            
            # Check columns
            columns = await database.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'file_uploads'
                ORDER BY ordinal_position
            """)
            
            print("   - Columns:")
            critical_columns = ['user_id', 's3_key', 'file_type', 'upload_status']
            for col in columns:
                status = "✅" if col['column_name'] in critical_columns else "  "
                print(f"     {status} {col['column_name']} ({col['data_type']})")
                
            # Check for user_id (critical for RLS)
            has_user_id = any(col['column_name'] == 'user_id' for col in columns)
            if not has_user_id:
                print("   ❌ CRITICAL: user_id column missing - RLS cannot work!")
                
        else:
            print("❌ file_uploads table not found")
            
        await database.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(check_schema())
