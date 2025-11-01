#!/usr/bin/env python3
"""
Create crisis support system tables - FINAL VERSION
Handles existing tables and permission issues
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_crisis_tables():
    """Create only missing crisis tables and setup RLS"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Get a user ID for RLS context
            user_id = await conn.fetchval("SELECT id FROM users LIMIT 1;")
            
            if not user_id:
                print("❌ No users found in database. Cannot set RLS context.")
                return

            print(f"🔧 Setting RLS context with user_id: {user_id}")
            await conn.execute("SELECT set_current_user_id($1);", user_id)

            # Check which tables exist
            existing_tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
            """)

            existing_table_names = [t['table_name'] for t in existing_tables]
            print(f"🔍 Existing crisis tables: {existing_table_names}")

            # Create only missing tables
            missing_tables = []
            
            # Create wellness_checkins if missing
            if 'wellness_checkins' not in existing_table_names:
                print("🔄 Creating wellness_checkins table...")
                try:
                    await conn.execute("""
                        CREATE TABLE wellness_checkins (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            user_id UUID NOT NULL,
                            checkin_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            mood_rating INTEGER CHECK (mood_rating BETWEEN 1 AND 10),
                            anxiety_level INTEGER CHECK (anxiety_level BETWEEN 1 AND 10),
                            sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 5),
                            safety_concerns BOOLEAN DEFAULT FALSE,
                            safety_concerns_details TEXT,
                            coping_strategies_used TEXT[],
                            support_needed BOOLEAN DEFAULT FALSE,
                            support_type VARCHAR(100),
                            notes TEXT,
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            UNIQUE(user_id, checkin_date)
                        );
                    """)
                    print("✅ Created wellness_checkins table")
                    missing_tables.append('wellness_checkins')
                except Exception as e:
                    print(f"⚠️ Could not create wellness_checkins: {e}")

            # Create crisis_alerts if missing
            if 'crisis_alerts' not in existing_table_names:
                print("🔄 Creating crisis_alerts table...")
                try:
                    await conn.execute("""
                        CREATE TABLE crisis_alerts (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            user_id UUID NOT NULL,
                            alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('sos', 'wellness_check', 'safety_concern')),
                            severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
                            message TEXT,
                            location_data JSONB,
                            is_resolved BOOLEAN DEFAULT FALSE,
                            resolved_at TIMESTAMPTZ,
                            resolved_by UUID,
                            resolution_notes TEXT,
                            created_at TIMESTAMPTZ DEFAULT NOW()
                        );
                    """)
                    print("✅ Created crisis_alerts table")
                    missing_tables.append('crisis_alerts')
                except Exception as e:
                    print(f"⚠️ Could not create crisis_alerts: {e}")

            # Enable RLS on all crisis tables
            crisis_tables = ['emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts']
            
            for table in crisis_tables:
                try:
                    # Check if RLS is already enabled
                    rls_enabled = await conn.fetchval("""
                        SELECT rowsecurity 
                        FROM pg_tables 
                        WHERE tablename = $1 AND schemaname = 'public'
                    """, table)
                    
                    if not rls_enabled:
                        await conn.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
                        print(f"✅ RLS enabled for {table}")
                    else:
                        print(f"✅ RLS already enabled for {table}")
                        
                except Exception as e:
                    print(f"⚠️ Could not enable RLS for {table}: {e}")

            # Setup RLS policies for each table
            await setup_rls_policies(conn, existing_table_names + missing_tables)

            print("🎉 Crisis tables setup completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

async def setup_rls_policies(conn, tables):
    """Setup RLS policies for crisis tables"""
    print("🔧 Setting up RLS policies...")
    
    # Emergency Contacts policies
    if 'emergency_contacts' in tables:
        try:
            await conn.execute("DROP POLICY IF EXISTS user_emergency_contacts_policy ON emergency_contacts;")
            await conn.execute("""
                CREATE POLICY user_emergency_contacts_policy ON emergency_contacts
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies set for emergency_contacts")
        except Exception as e:
            print(f"⚠️ Could not set emergency_contacts policies: {e}")

    # Crisis Resources policies
    if 'crisis_resources' in tables:
        try:
            await conn.execute("DROP POLICY IF EXISTS view_crisis_resources_policy ON crisis_resources;")
            await conn.execute("DROP POLICY IF EXISTS manage_crisis_resources_policy ON crisis_resources;")
            
            await conn.execute("""
                CREATE POLICY view_crisis_resources_policy ON crisis_resources
                FOR SELECT USING (true);
            """)
            
            await conn.execute("""
                CREATE POLICY manage_crisis_resources_policy ON crisis_resources
                FOR ALL USING (created_by = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies set for crisis_resources")
        except Exception as e:
            print(f"⚠️ Could not set crisis_resources policies: {e}")

    # Safety Plans policies
    if 'safety_plans' in tables:
        try:
            await conn.execute("DROP POLICY IF EXISTS user_safety_plans_policy ON safety_plans;")
            await conn.execute("""
                CREATE POLICY user_safety_plans_policy ON safety_plans
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies set for safety_plans")
        except Exception as e:
            print(f"⚠️ Could not set safety_plans policies: {e}")

    # Wellness Checkins policies
    if 'wellness_checkins' in tables:
        try:
            await conn.execute("DROP POLICY IF EXISTS user_wellness_checkins_policy ON wellness_checkins;")
            await conn.execute("""
                CREATE POLICY user_wellness_checkins_policy ON wellness_checkins
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies set for wellness_checkins")
        except Exception as e:
            print(f"⚠️ Could not set wellness_checkins policies: {e}")

    # Crisis Alerts policies
    if 'crisis_alerts' in tables:
        try:
            await conn.execute("DROP POLICY IF EXISTS user_crisis_alerts_policy ON crisis_alerts;")
            await conn.execute("""
                CREATE POLICY user_crisis_alerts_policy ON crisis_alerts
                FOR ALL USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies set for crisis_alerts")
        except Exception as e:
            print(f"⚠️ Could not set crisis_alerts policies: {e}")

async def verify_crisis_tables():
    """Verify that crisis tables are properly set up"""
    try:
        await database.connect()
        print("\n🔍 Verifying crisis tables setup...")
        
        async with database.pool.acquire() as conn:
            # Check tables exist
            tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
            """)
            
            print("📋 Existing crisis tables:")
            for table in tables:
                table_name = table['table_name']
                
                # Check RLS status
                rls_status = await conn.fetchval("""
                    SELECT rowsecurity 
                    FROM pg_tables 
                    WHERE tablename = $1 AND schemaname = 'public'
                """, table_name)
                
                # Check policies
                policies = await conn.fetch("""
                    SELECT policyname
                    FROM pg_policies 
                    WHERE tablename = $1 AND schemaname = 'public'
                """, table_name)
                
                policy_names = [p['policyname'] for p in policies]
                
                print(f"   - {table_name}: RLS={rls_status}, Policies={policy_names}")
        
        print("✅ Verification complete!")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        await database.close()

if __name__ == "__main__":
    print("🚀 Starting Crisis Support System Setup...")
    asyncio.run(create_crisis_tables())
    asyncio.run(verify_crisis_tables())
    print("\n🎉 Crisis Support System setup completed!")
