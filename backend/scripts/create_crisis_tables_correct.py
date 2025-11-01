#!/usr/bin/env python3
"""
Create crisis support system tables following EXACT project patterns
USING THE SAME PATTERN AS create_likes_tables_fixed.py
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_crisis_tables():
    """Create crisis tables with RLS - FOLLOWING EXACT PROJECT PATTERNS"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Use the EXACT same pattern as the working script
            user_id = await conn.fetchval("SELECT id FROM users LIMIT 1;")

            if not user_id:
                print("❌ No users found in database. Cannot set RLS context.")
                return

            print(f"🔧 Setting RLS context with user_id: {user_id}")
            await conn.execute("SELECT set_current_user_id($1);", user_id)

            # Check if tables already exist - FOLLOWING EXACT PATTERN
            existing_tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
            """)

            existing_table_names = [t['table_name'] for t in existing_tables]
            print(f"🔍 Existing crisis tables: {existing_table_names}")

            # Create emergency_contacts table if it doesn't exist
            if 'emergency_contacts' not in existing_table_names:
                print("🔄 Creating emergency_contacts table...")
                await conn.execute("""
                    CREATE TABLE emergency_contacts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        name VARCHAR(100) NOT NULL,
                        relationship VARCHAR(100) NOT NULL,
                        phone_number VARCHAR(20) NOT NULL,
                        email VARCHAR(255),
                        priority_level INTEGER NOT NULL DEFAULT 3 CHECK (priority_level BETWEEN 1 AND 3),
                        is_verified BOOLEAN DEFAULT FALSE,
                        consent_obtained BOOLEAN DEFAULT FALSE,
                        notes TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(user_id, phone_number)
                    );
                """)
                print("✅ Created emergency_contacts table")
            else:
                print("✅ emergency_contacts table already exists")

            # Create crisis_resources table if it doesn't exist
            if 'crisis_resources' not in existing_table_names:
                print("🔄 Creating crisis_resources table...")
                await conn.execute("""
                    CREATE TABLE crisis_resources (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(200) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        description TEXT,
                        phone_number VARCHAR(20),
                        website_url VARCHAR(500),
                        email VARCHAR(255),
                        address TEXT,
                        city VARCHAR(100),
                        state VARCHAR(100),
                        country VARCHAR(100) DEFAULT 'US',
                        latitude DECIMAL(10, 8),
                        longitude DECIMAL(11, 8),
                        is_24_7 BOOLEAN DEFAULT FALSE,
                        languages_supported VARCHAR(500),
                        special_notes TEXT,
                        is_verified BOOLEAN DEFAULT FALSE,
                        created_by UUID REFERENCES users(id),
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                print("✅ Created crisis_resources table")
            else:
                print("✅ crisis_resources table already exists")

            # Create safety_plans table if it doesn't exist
            if 'safety_plans' not in existing_table_names:
                print("🔄 Creating safety_plans table...")
                await conn.execute("""
                    CREATE TABLE safety_plans (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        plan_name VARCHAR(200) NOT NULL DEFAULT 'My Safety Plan',
                        warning_signs TEXT[],
                        internal_coping_strategies TEXT[],
                        external_coping_strategies TEXT[],
                        social_contacts JSONB,
                        professional_contacts JSONB,
                        environment_safety TEXT[],
                        reasons_for_living TEXT[],
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(user_id, plan_name)
                    );
                """)
                print("✅ Created safety_plans table")
            else:
                print("✅ safety_plans table already exists")

            # Create wellness_checkins table if it doesn't exist
            if 'wellness_checkins' not in existing_table_names:
                print("🔄 Creating wellness_checkins table...")
                await conn.execute("""
                    CREATE TABLE wellness_checkins (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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
            else:
                print("✅ wellness_checkins table already exists")

            # Create crisis_alerts table if it doesn't exist
            if 'crisis_alerts' not in existing_table_names:
                print("🔄 Creating crisis_alerts table...")
                await conn.execute("""
                    CREATE TABLE crisis_alerts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('sos', 'wellness_check', 'safety_concern')),
                        severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
                        message TEXT,
                        location_data JSONB,
                        is_resolved BOOLEAN DEFAULT FALSE,
                        resolved_at TIMESTAMPTZ,
                        resolved_by UUID REFERENCES users(id),
                        resolution_notes TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                print("✅ Created crisis_alerts table")
            else:
                print("✅ crisis_alerts table already exists")

            # Enable RLS - FOLLOWING EXACT PATTERN
            crisis_tables = [
                'emergency_contacts',
                'crisis_resources', 
                'safety_plans',
                'wellness_checkins',
                'crisis_alerts'
            ]
            
            for table in crisis_tables:
                if table not in existing_table_names:
                    await conn.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
                    print(f"✅ RLS enabled for {table}")

            # Create RLS policies for emergency_contacts - FOLLOWING EXACT PATTERN
            if 'emergency_contacts' not in existing_table_names:
                await conn.execute("""
                    CREATE POLICY "users_view_own_emergency_contacts" ON emergency_contacts
                        FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_create_own_emergency_contacts" ON emergency_contacts
                        FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_update_own_emergency_contacts" ON emergency_contacts
                        FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_delete_own_emergency_contacts" ON emergency_contacts
                        FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)
                print("✅ RLS policies created for emergency_contacts")

            # Create RLS policies for crisis_resources - FOLLOWING EXACT PATTERN
            if 'crisis_resources' not in existing_table_names:
                await conn.execute("""
                    CREATE POLICY "users_view_crisis_resources" ON crisis_resources
                        FOR SELECT USING (true);
                """)

                await conn.execute("""
                    CREATE POLICY "admins_manage_crisis_resources" ON crisis_resources
                        FOR ALL USING (created_by = current_setting('app.current_user_id', true)::uuid);
                """)
                print("✅ RLS policies created for crisis_resources")

            # Create RLS policies for safety_plans - FOLLOWING EXACT PATTERN
            if 'safety_plans' not in existing_table_names:
                await conn.execute("""
                    CREATE POLICY "users_view_own_safety_plans" ON safety_plans
                        FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_create_own_safety_plans" ON safety_plans
                        FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_update_own_safety_plans" ON safety_plans
                        FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_delete_own_safety_plans" ON safety_plans
                        FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)
                print("✅ RLS policies created for safety_plans")

            # Create RLS policies for wellness_checkins - FOLLOWING EXACT PATTERN
            if 'wellness_checkins' not in existing_table_names:
                await conn.execute("""
                    CREATE POLICY "users_view_own_wellness_checkins" ON wellness_checkins
                        FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_create_own_wellness_checkins" ON wellness_checkins
                        FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_update_own_wellness_checkins" ON wellness_checkins
                        FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_delete_own_wellness_checkins" ON wellness_checkins
                        FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)
                print("✅ RLS policies created for wellness_checkins")

            # Create RLS policies for crisis_alerts - FOLLOWING EXACT PATTERN
            if 'crisis_alerts' not in existing_table_names:
                await conn.execute("""
                    CREATE POLICY "users_view_own_crisis_alerts" ON crisis_alerts
                        FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_create_own_crisis_alerts" ON crisis_alerts
                        FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::uuid);
                """)

                await conn.execute("""
                    CREATE POLICY "users_update_own_crisis_alerts" ON crisis_alerts
                        FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)
                print("✅ RLS policies created for crisis_alerts")

            # Create indexes for better performance
            if 'emergency_contacts' not in existing_table_names:
                await conn.execute("CREATE INDEX idx_emergency_contacts_user_id ON emergency_contacts(user_id);")
                await conn.execute("CREATE INDEX idx_emergency_contacts_priority ON emergency_contacts(priority_level);")

            if 'crisis_resources' not in existing_table_names:
                await conn.execute("CREATE INDEX idx_crisis_resources_category ON crisis_resources(category);")
                await conn.execute("CREATE INDEX idx_crisis_resources_city_state ON crisis_resources(city, state);")

            if 'safety_plans' not in existing_table_names:
                await conn.execute("CREATE INDEX idx_safety_plans_user_id ON safety_plans(user_id);")
                await conn.execute("CREATE INDEX idx_safety_plans_active ON safety_plans(is_active);")

            if 'wellness_checkins' not in existing_table_names:
                await conn.execute("CREATE INDEX idx_wellness_checkins_user_date ON wellness_checkins(user_id, checkin_date DESC);")

            if 'crisis_alerts' not in existing_table_names:
                await conn.execute("CREATE INDEX idx_crisis_alerts_user_id ON crisis_alerts(user_id);")
                await conn.execute("CREATE INDEX idx_crisis_alerts_created_at ON crisis_alerts(created_at DESC);")

            print("✅ Indexes created for crisis tables")

            # Verify final state
            final_tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('emergency_contacts', 'crisis_resources', 'safety_plans', 'wellness_checkins', 'crisis_alerts')
            """)

            final_table_names = [t['table_name'] for t in final_tables]
            print(f"🎉 Final crisis tables: {final_table_names}")

        print("✅ Crisis support system tables setup completed successfully!")

    except Exception as e:
        print(f"❌ Error creating crisis tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    print("🚀 Starting Crisis Support System Table Creation...")
    print("📋 Using EXACT pattern from create_likes_tables_fixed.py")
    asyncio.run(create_crisis_tables())
