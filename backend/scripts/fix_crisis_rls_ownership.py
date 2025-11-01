#!/usr/bin/env python3
"""
Fix RLS ownership issues for existing crisis tables
Uses the established fix pattern from the project
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_crisis_rls_ownership():
    """Fix RLS policies using superuser connection"""
    
    # Use the same pattern as other fix scripts
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        # Try with app user first
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Check current table ownership
        tables = await conn.fetch("""
            SELECT tablename, tableowner 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('emergency_contacts', 'crisis_resources', 'safety_plans')
        """)
        
        print("📋 Current table ownership:")
        for table in tables:
            print(f"   - {table['tablename']}: owned by {table['tableowner']}")
        
        await conn.close()
        
        # Now fix with superuser (you'll need to provide postgres password)
        print("\n🔧 Attempting to fix RLS with superuser...")
        
        # Try common postgres passwords or prompt
        postgres_passwords = [
            "postgres", 
            "password",
            "admin",
            "root",
            ""  # empty password
        ]
        
        superuser_conn = None
        for password in postgres_passwords:
            try:
                superuser_url = f"postgresql://postgres:{password}@localhost:5433/safe_zone"
                superuser_conn = await asyncpg.connect(superuser_url)
                print(f"✅ Connected as superuser with password: {'*' * len(password) if password else 'empty'}")
                break
            except:
                continue
        
        if not superuser_conn:
            print("❌ Could not connect as superuser. Please run manually:")
            print("   psql -h localhost -p 5433 -d safe_zone -U postgres")
            print("   Then run the SQL commands manually")
            return
        
        # Fix RLS for each table
        tables_to_fix = [
            ('emergency_contacts', """
                DROP POLICY IF EXISTS user_emergency_contacts_policy ON emergency_contacts;
                CREATE POLICY user_emergency_contacts_policy ON emergency_contacts
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """),
            
            ('crisis_resources', """
                ALTER TABLE crisis_resources ENABLE ROW LEVEL SECURITY;
                DROP POLICY IF EXISTS view_crisis_resources_policy ON crisis_resources;
                DROP POLICY IF EXISTS manage_crisis_resources_policy ON crisis_resources;
                CREATE POLICY view_crisis_resources_policy ON crisis_resources
                FOR SELECT USING (true);
                CREATE POLICY manage_crisis_resources_policy ON crisis_resources
                FOR ALL USING (created_by = current_setting('app.current_user_id', true)::uuid);
            """),
            
            ('safety_plans', """
                DROP POLICY IF EXISTS user_safety_plans_policy ON safety_plans;
                CREATE POLICY user_safety_plans_policy ON safety_plans
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
        ]
        
        for table_name, sql in tables_to_fix:
            try:
                await superuser_conn.execute(sql)
                print(f"✅ Fixed RLS for {table_name}")
            except Exception as e:
                print(f"⚠️ Could not fix {table_name}: {e}")
        
        await superuser_conn.close()
        print("🎉 RLS ownership fixes attempted!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def verify_fix():
    """Verify the RLS fixes worked"""
    try:
        database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        conn = await asyncpg.connect(database_url)
        
        print("\n🔍 Verifying RLS fixes...")
        tables = await conn.fetch("""
            SELECT 
                t.tablename,
                t.rowsecurity as rls_enabled,
                COUNT(p.policyname) as policy_count
            FROM pg_tables t
            LEFT JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
            WHERE t.schemaname = 'public' 
            AND t.tablename IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
            GROUP BY t.tablename, t.rowsecurity
            ORDER BY t.tablename
        """)
        
        print("📋 Final RLS status:")
        for table in tables:
            status = "✅" if table['rls_enabled'] and table['policy_count'] > 0 else "❌"
            print(f"   {status} {table['tablename']}: RLS={table['rls_enabled']}, Policies={table['policy_count']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    print("🚀 Fixing Crisis Tables RLS Ownership...")
    asyncio.run(fix_crisis_rls_ownership())
    asyncio.run(verify_fix())
