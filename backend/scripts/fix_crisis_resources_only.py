#!/usr/bin/env python3
"""
Fix only the crisis_resources table RLS
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_crisis_resources():
    """Enable RLS on crisis_resources using app user"""
    try:
        database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")

        # Get a user ID for RLS context
        user_id = await conn.fetchval("SELECT id FROM users LIMIT 1;")
        if user_id:
            await conn.execute("SELECT set_current_user_id($1);", user_id)
            print(f"🔧 RLS context set with user: {user_id}")

        # Try to enable RLS on crisis_resources
        try:
            await conn.execute("ALTER TABLE crisis_resources ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled for crisis_resources")
        except Exception as e:
            print(f"⚠️ Could not enable RLS: {e}")

        # Try to create basic policies
        try:
            # Drop existing policies if any
            await conn.execute("DROP POLICY IF EXISTS crisis_resources_view_policy ON crisis_resources;")
            await conn.execute("DROP POLICY IF EXISTS crisis_resources_manage_policy ON crisis_resources;")
            
            # Create read policy for all authenticated users
            await conn.execute("""
                CREATE POLICY crisis_resources_view_policy ON crisis_resources
                FOR SELECT USING (true);
            """)
            print("✅ Read policy created for crisis_resources")
            
            # Create manage policy for resource creators
            await conn.execute("""
                CREATE POLICY crisis_resources_manage_policy ON crisis_resources
                FOR ALL USING (created_by = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ Manage policy created for crisis_resources")
            
        except Exception as e:
            print(f"⚠️ Could not create policies: {e}")

        await conn.close()
        print("🎉 Crisis resources fix attempted!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Fixing crisis_resources RLS...")
    asyncio.run(fix_crisis_resources())
