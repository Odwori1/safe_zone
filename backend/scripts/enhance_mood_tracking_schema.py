#!/usr/bin/env python3
"""
Enhance mood tracking table using PostgreSQL superuser
With correct password: 0791486006@safezone
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def enhance_mood_tracking_schema():
    """Enhance mood_entries table with superuser privileges"""

    # Get database config from .env with correct postgres password
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5433')),  # FIXED: Use port 5433
        'database': os.getenv('DB_NAME', 'safe_zone'),
        'user': 'postgres',
        'password': '0791486006@safezone'  # Correct password
    }

    print(f"🔧 Database config: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    print("🔑 Using postgres superuser with provided password")

    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Successfully connected as postgres superuser!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    try:
        # 1. First, let's check current table structure
        print("\n📋 Current mood_entries table structure:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'mood_entries'
            ORDER BY ordinal_position;
        """)
        for col in columns:
            print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        # 2. Add enhanced columns for hybrid tracking
        print("\n🔄 Adding hybrid tracking columns to mood_entries table...")

        enhanced_columns = [
            ("source_type", "VARCHAR(20) DEFAULT 'standalone'"),
            ("source_id", "UUID"),
            ("triggers", "TEXT[] DEFAULT '{}'"),
            ("activities", "TEXT[] DEFAULT '{}'"),
            ("physical_symptoms", "TEXT[] DEFAULT '{}'"),
            ("social_context", "VARCHAR(50)"),
            ("sleep_quality", "INTEGER"),
            ("energy_level", "INTEGER"),
            ("location", "VARCHAR(100)"),
            ("weather", "VARCHAR(50)"),
            ("duration_minutes", "INTEGER"),
            ("medication_taken", "BOOLEAN DEFAULT false"),
            ("medication_notes", "TEXT")
        ]

        for col_name, col_type in enhanced_columns:
            try:
                await conn.execute(f"ALTER TABLE mood_entries ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                print(f"✅ Added {col_name} column")
            except Exception as e:
                print(f"⚠️ Could not add {col_name}: {e}")

        # 3. Add constraints
        print("\n🔒 Adding constraints...")
        constraints = [
            ("valid_source_type", "CHECK (source_type IN ('post', 'journal', 'standalone'))"),
            ("sleep_quality_range", "CHECK (sleep_quality >= 1 AND sleep_quality <= 10)"),
            ("energy_level_range", "CHECK (energy_level >= 1 AND energy_level <= 10)")
        ]

        for const_name, const_def in constraints:
            try:
                await conn.execute(f"ALTER TABLE mood_entries ADD CONSTRAINT IF NOT EXISTS {const_name} {const_def};")
                print(f"✅ Added {const_name} constraint")
            except Exception as e:
                print(f"⚠️ Could not add {const_name}: {e}")

        # 4. Create mood_insights table for future AI features
        print("\n📊 Creating mood_insights table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mood_insights (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                insight_type VARCHAR(50) NOT NULL,
                pattern_description TEXT NOT NULL,
                confidence_score DECIMAL(3,2) DEFAULT 0.0,
                data_points INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✅ Mood insights table created")

        # 5. Create indexes for better performance
        print("\n📈 Creating indexes...")
        indexes = [
            "idx_mood_entries_source ON mood_entries(source_type, source_id)",
            "idx_mood_entries_triggers ON mood_entries USING GIN(triggers)",
            "idx_mood_entries_activities ON mood_entries USING GIN(activities)",
            "idx_mood_entries_physical_symptoms ON mood_entries USING GIN(physical_symptoms)",
            "idx_mood_insights_user ON mood_insights(user_id, insight_type)"
        ]

        for index in indexes:
            try:
                await conn.execute(f"CREATE INDEX IF NOT EXISTS {index};")
                print(f"✅ Created {index.split(' ')[0]} index")
            except Exception as e:
                print(f"⚠️ Could not create index: {e}")

        # 6. Enable and configure RLS for mood_insights
        print("\n🔐 Configuring Row Level Security for mood_insights...")

        # Enable RLS
        await conn.execute("ALTER TABLE mood_insights ENABLE ROW LEVEL SECURITY;")
        print("✅ RLS enabled for mood_insights")

        # Drop existing policies if any
        await conn.execute("""
            DROP POLICY IF EXISTS "users_view_own_mood_insights" ON mood_insights;
            DROP POLICY IF EXISTS "users_insert_own_mood_insights" ON mood_insights;
            DROP POLICY IF EXISTS "users_update_own_mood_insights" ON mood_insights;
            DROP POLICY IF EXISTS "users_delete_own_mood_insights" ON mood_insights;
        """)
        print("✅ Cleared existing mood_insights policies")

        # Create RLS policies for mood_insights
        mood_insights_policies = [
            ('users_view_own_mood_insights', 'FOR SELECT USING (user_id = current_setting(\'app.current_user_id\', true)::uuid)'),
            ('users_insert_own_mood_insights', 'FOR INSERT WITH CHECK (user_id = current_setting(\'app.current_user_id\', true)::uuid)'),
            ('users_update_own_mood_insights', 'FOR UPDATE USING (user_id = current_setting(\'app.current_user_id\', true)::uuid)'),
            ('users_delete_own_mood_insights', 'FOR DELETE USING (user_id = current_setting(\'app.current_user_id\', true)::uuid)')
        ]

        for policy_name, policy_def in mood_insights_policies:
            await conn.execute(f'CREATE POLICY "{policy_name}" ON mood_insights {policy_def};')
            print(f"✅ Created {policy_name} policy")

        # 7. Grant permissions to app user
        print("\n👤 Granting permissions to safe_zone_app_user...")
        await conn.execute("""
            GRANT ALL PRIVILEGES ON TABLE mood_insights TO safe_zone_app_user;
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;
        """)
        print("✅ Permissions granted")

        # 8. Verify final structure
        print("\n📋 Final mood_entries table structure:")
        final_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'mood_entries'
            ORDER BY ordinal_position;
        """)
        for col in final_columns:
            print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        print("\n🎉 Enhanced mood tracking schema completed successfully!")
        print("🔒 Mood insights now have strict RLS policies")
        print("📊 Enhanced with hybrid tracking capabilities")

    except Exception as e:
        print(f"❌ Mood tracking schema enhancement failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(enhance_mood_tracking_schema())
