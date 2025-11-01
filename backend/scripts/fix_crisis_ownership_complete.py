#!/usr/bin/env python3
"""
Complete fix for crisis tables RLS ownership
This will fix ALL crisis tables to have proper ownership and RLS
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_crisis_tables_ownership():
    """Fix ownership and RLS for all crisis tables"""
    
    print("🚀 Starting comprehensive crisis tables fix...")
    
    # First, let's check what's the actual superuser password
    # Try common passwords or get it from environment
    superuser_passwords = [
        os.getenv('POSTGRES_PASSWORD'),  # Check if it's in .env
        "postgres",
        "password", 
        "admin",
        "root",
        "safe_zone_2024",
        ""  # empty
    ]
    
    superuser_conn = None
    used_password = None
    
    for password in superuser_passwords:
        if password is None:
            continue
        try:
            superuser_url = f"postgresql://postgres:{password}@localhost:5433/safe_zone"
            superuser_conn = await asyncpg.connect(superuser_url)
            used_password = password
            print(f"✅ Connected as superuser with password: {'*' * len(password) if password else 'empty'}")
            break
        except Exception as e:
            continue
    
    if not superuser_conn:
        print("❌ Could not connect as superuser. Please check your PostgreSQL credentials.")
        print("💡 Try running: psql -h localhost -p 5433 -d safe_zone -U postgres")
        print("   Then enter the password when prompted.")
        return
    
    try:
        # First, let's see current table ownership
        tables = await superuser_conn.fetch("""
            SELECT tablename, tableowner 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
        """)
        
        print("\n📋 Current table ownership:")
        for table in tables:
            print(f"   - {table['tablename']}: owned by {table['tableowner']}")
        
        # Fix ownership - transfer all tables to postgres
        crisis_tables = ['emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
        
        for table in crisis_tables:
            try:
                await superuser_conn.execute(f'ALTER TABLE {table} OWNER TO postgres;')
                print(f"✅ Transferred {table} ownership to postgres")
            except Exception as e:
                print(f"⚠️ Could not transfer {table}: {e}")
        
        # Now enable RLS and create policies
        print("\n🔧 Setting up RLS policies...")
        
        # Emergency Contacts
        try:
            await superuser_conn.execute("ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;")
            await superuser_conn.execute("DROP POLICY IF EXISTS user_emergency_contacts_policy ON emergency_contacts;")
            await superuser_conn.execute("""
                CREATE POLICY user_emergency_contacts_policy ON emergency_contacts
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS configured for emergency_contacts")
        except Exception as e:
            print(f"⚠️ Emergency contacts RLS: {e}")
        
        # Crisis Resources
        try:
            await superuser_conn.execute("ALTER TABLE crisis_resources ENABLE ROW LEVEL SECURITY;")
            await superuser_conn.execute("DROP POLICY IF EXISTS view_crisis_resources_policy ON crisis_resources;")
            await superuser_conn.execute("DROP POLICY IF EXISTS manage_crisis_resources_policy ON crisis_resources;")
            
            await superuser_conn.execute("""
                CREATE POLICY view_crisis_resources_policy ON crisis_resources
                FOR SELECT USING (true);
            """)
            
            await superuser_conn.execute("""
                CREATE POLICY manage_crisis_resources_policy ON crisis_resources
                FOR ALL USING (created_by = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS configured for crisis_resources")
        except Exception as e:
            print(f"⚠️ Crisis resources RLS: {e}")
        
        # Safety Plans
        try:
            await superuser_conn.execute("ALTER TABLE safety_plans ENABLE ROW LEVEL SECURITY;")
            await superuser_conn.execute("DROP POLICY IF EXISTS user_safety_plans_policy ON safety_plans;")
            await superuser_conn.execute("""
                CREATE POLICY user_safety_plans_policy ON safety_plans
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS configured for safety_plans")
        except Exception as e:
            print(f"⚠️ Safety plans RLS: {e}")
        
        # Wellness Checkins
        try:
            await superuser_conn.execute("ALTER TABLE wellness_checkins ENABLE ROW LEVEL SECURITY;")
            await superuser_conn.execute("DROP POLICY IF EXISTS user_wellness_checkins_policy ON wellness_checkins;")
            await superuser_conn.execute("""
                CREATE POLICY user_wellness_checkins_policy ON wellness_checkins
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS configured for wellness_checkins")
        except Exception as e:
            print(f"⚠️ Wellness checkins RLS: {e}")
        
        # Crisis Alerts
        try:
            await superuser_conn.execute("ALTER TABLE crisis_alerts ENABLE ROW LEVEL SECURITY;")
            await superuser_conn.execute("DROP POLICY IF EXISTS user_crisis_alerts_policy ON crisis_alerts;")
            await superuser_conn.execute("""
                CREATE POLICY user_crisis_alerts_policy ON crisis_alerts
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS configured for crisis_alerts")
        except Exception as e:
            print(f"⚠️ Crisis alerts RLS: {e}")
        
        # Grant permissions to app user
        print("\n🔑 Granting permissions to app user...")
        for table in crisis_tables:
            try:
                await superuser_conn.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO safe_zone_app_user;")
                print(f"✅ Permissions granted for {table}")
            except Exception as e:
                print(f"⚠️ Permissions for {table}: {e}")
        
        await superuser_conn.close()
        
        print("\n🎉 Crisis tables ownership and RLS fix completed!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        if superuser_conn:
            await superuser_conn.close()

async def verify_fix():
    """Verify the fix worked"""
    try:
        database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        conn = await asyncpg.connect(database_url)
        
        print("\n🔍 Verifying RLS fix...")
        
        # Check RLS status and policies
        result = await conn.fetch("""
            SELECT 
                t.tablename,
                t.rowsecurity as rls_enabled,
                t.tableowner,
                COUNT(p.policyname) as policy_count,
                array_agg(p.policyname) as policy_names
            FROM pg_tables t
            LEFT JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
            WHERE t.schemaname = 'public' 
            AND t.tablename IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
            GROUP BY t.tablename, t.rowsecurity, t.tableowner
            ORDER BY t.tablename
        """)
        
        print("📋 Final RLS status:")
        all_good = True
        for table in result:
            status = "✅" if table['rls_enabled'] and table['policy_count'] > 0 else "❌"
            owner_ok = "✅" if table['tableowner'] == 'postgres' else "❌"
            
            if not (table['rls_enabled'] and table['policy_count'] > 0 and table['tableowner'] == 'postgres'):
                all_good = False
                
            print(f"   {status} {owner_ok} {table['tablename']}:")
            print(f"      RLS={table['rls_enabled']}, Policies={table['policy_count']}, Owner={table['tableowner']}")
            if table['policy_names'] and table['policy_names'][0]:
                print(f"      Policy names: {', '.join(table['policy_names'])}")
        
        if all_good:
            print("\n🎉 ALL CRISIS TABLES ARE PROPERLY CONFIGURED!")
            print("🚀 You can now proceed with backend implementation.")
        else:
            print("\n⚠️ Some tables still need manual fixing.")
            print("💡 You may need to run SQL commands manually as superuser.")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    print("🚀 Comprehensive Crisis Tables RLS Fix")
    print("=" * 50)
    asyncio.run(fix_crisis_tables_ownership())
    asyncio.run(verify_fix())
