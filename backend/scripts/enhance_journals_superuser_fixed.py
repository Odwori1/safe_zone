#!/usr/bin/env python3
"""
Enhance journals table using PostgreSQL superuser
With correct password: 0791486006@safezone
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def enhance_journals_superuser():
    """Enhance journals table with superuser privileges"""
    
    # Get database config from .env with correct postgres password
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5433')),
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
        print("\n📋 Current journals table structure:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'journals'
            ORDER BY ordinal_position;
        """)
        for col in columns:
            print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        # 2. Add enhanced columns
        print("\n🔄 Adding professional columns to journals table...")
        
        enhanced_columns = [
            ("title", "VARCHAR(500)"),
            ("content_type", "VARCHAR(20) DEFAULT 'journal'"),
            ("mood_intensity", "INTEGER"),
            ("tags", "TEXT[] DEFAULT '{}'"),
            ("word_count", "INTEGER DEFAULT 0"),
            ("read_time_minutes", "INTEGER DEFAULT 0"),
            ("is_encrypted", "BOOLEAN DEFAULT false"),
            ("status", "VARCHAR(20) DEFAULT 'active'"),
            ("prompt_id", "UUID")
        ]
        
        for col_name, col_type in enhanced_columns:
            try:
                await conn.execute(f"ALTER TABLE journals ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                print(f"✅ Added {col_name} column")
            except Exception as e:
                print(f"⚠️ Could not add {col_name}: {e}")

        # 3. Add constraints
        print("\n🔒 Adding constraints...")
        constraints = [
            ("mood_intensity_range", "CHECK (mood_intensity >= 1 AND mood_intensity <= 10)"),
            ("valid_journal_status", "CHECK (status IN ('active', 'archived', 'deleted'))")
        ]
        
        for const_name, const_def in constraints:
            try:
                await conn.execute(f"ALTER TABLE journals ADD CONSTRAINT IF NOT EXISTS {const_name} {const_def};")
                print(f"✅ Added {const_name} constraint")
            except Exception as e:
                print(f"⚠️ Could not add {const_name}: {e}")

        # 4. Create journal_prompts table
        print("\n📝 Creating journal_prompts table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS journal_prompts (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                prompt_text TEXT NOT NULL,
                category VARCHAR(50) DEFAULT 'general',
                difficulty_level VARCHAR(20) DEFAULT 'easy' CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✅ Journal prompts table created")

        # 5. Add foreign key constraint for prompt_id
        try:
            await conn.execute("""
                ALTER TABLE journals 
                ADD CONSTRAINT IF NOT EXISTS journals_prompt_id_fkey 
                FOREIGN KEY (prompt_id) REFERENCES journal_prompts(id);
            """)
            print("✅ Added prompt_id foreign key constraint")
        except Exception as e:
            print(f"⚠️ Could not add foreign key: {e}")

        # 6. Create updated_at trigger
        print("\n⏰ Creating updated_at trigger...")
        await conn.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        await conn.execute("""
            DROP TRIGGER IF EXISTS update_journals_updated_at ON journals;
            CREATE TRIGGER update_journals_updated_at
                BEFORE UPDATE ON journals
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)
        print("✅ Updated_at trigger created")

        # 7. Create indexes
        print("\n📊 Creating indexes...")
        indexes = [
            "idx_journals_user_id ON journals(user_id)",
            "idx_journals_created_at ON journals(created_at DESC)",
            "idx_journals_mood ON journals(mood)",
            "idx_journals_tags ON journals USING GIN(tags)",
            "idx_journal_prompts_category ON journal_prompts(category)"
        ]
        
        for index in indexes:
            try:
                await conn.execute(f"CREATE INDEX IF NOT EXISTS {index};")
                print(f"✅ Created {index.split(' ')[0]} index")
            except Exception as e:
                print(f"⚠️ Could not create index: {e}")

        # 8. Enable and configure RLS
        print("\n🔐 Configuring Row Level Security...")
        
        # Enable RLS
        await conn.execute("ALTER TABLE journals ENABLE ROW LEVEL SECURITY;")
        await conn.execute("ALTER TABLE journal_prompts ENABLE ROW LEVEL SECURITY;")
        print("✅ RLS enabled")

        # Drop existing policies if any
        await conn.execute("""
            DROP POLICY IF EXISTS "users_view_own_journals" ON journals;
            DROP POLICY IF EXISTS "users_insert_own_journals" ON journals;
            DROP POLICY IF EXISTS "users_update_own_journals" ON journals;
            DROP POLICY IF EXISTS "users_delete_own_journals" ON journals;
            DROP POLICY IF EXISTS "anyone_view_prompts" ON journal_prompts;
            DROP POLICY IF EXISTS "admins_manage_prompts" ON journal_prompts;
        """)
        print("✅ Cleared existing policies")

        # Create strict RLS policies for journals
        journal_policies = [
            ('users_view_own_journals', 'FOR SELECT USING (user_id = current_setting(\'app.current_user_id\', true)::uuid)'),
            ('users_insert_own_journals', 'FOR INSERT WITH CHECK (user_id = current_setting(\'app.current_user_id\', true)::uuid)'),
            ('users_update_own_journals', 'FOR UPDATE USING (user_id = current_setting(\'app.current_user_id\', true)::uuid)'),
            ('users_delete_own_journals', 'FOR DELETE USING (user_id = current_setting(\'app.current_user_id\', true)::uuid)')
        ]
        
        for policy_name, policy_def in journal_policies:
            await conn.execute(f'CREATE POLICY "{policy_name}" ON journals {policy_def};')
            print(f"✅ Created {policy_name} policy")

        # Create RLS policies for prompts
        await conn.execute('CREATE POLICY "anyone_view_prompts" ON journal_prompts FOR SELECT USING (is_active = true);')
        await conn.execute('CREATE POLICY "admins_manage_prompts" ON journal_prompts FOR ALL USING (false);')
        print("✅ Created prompt policies")

        # 9. Insert sample prompts
        print("\n💡 Inserting sample journal prompts...")
        prompt_count = await conn.fetchval("SELECT COUNT(*) FROM journal_prompts;")
        if prompt_count == 0:
            await conn.execute("""
                INSERT INTO journal_prompts (prompt_text, category, difficulty_level) VALUES
                ('What are three things you''re grateful for today?', 'gratitude', 'easy'),
                ('Describe a challenge you faced and how you overcame it.', 'resilience', 'medium'),
                ('What does self-care mean to you right now?', 'self_care', 'easy'),
                ('Write about a moment that brought you peace recently.', 'mindfulness', 'easy'),
                ('What would you tell your younger self about handling difficult emotions?', 'reflection', 'hard'),
                ('Describe your ideal mental health support system.', 'support', 'medium'),
                ('What boundaries do you need to set for your wellbeing?', 'boundaries', 'medium'),
                ('Write about a time you showed yourself compassion.', 'self_compassion', 'easy');
            """)
            print("✅ Inserted 8 sample journal prompts")
        else:
            print(f"✅ Journal prompts already exist: {prompt_count} prompts")

        # 10. Grant permissions to app user
        print("\n👤 Granting permissions to safe_zone_app_user...")
        await conn.execute("""
            GRANT ALL PRIVILEGES ON TABLE journals TO safe_zone_app_user;
            GRANT ALL PRIVILEGES ON TABLE journal_prompts TO safe_zone_app_user;
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;
        """)
        print("✅ Permissions granted")

        # 11. Verify final structure
        print("\n📋 Final journals table structure:")
        final_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'journals'
            ORDER BY ordinal_position;
        """)
        for col in final_columns:
            print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        print("\n🎉 Professional journals schema enhancement completed successfully!")
        print("🔒 Journals now have strict RLS policies for maximum privacy")
        print("📝 Enhanced with professional mental health features")

    except Exception as e:
        print(f"❌ Journals schema enhancement failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(enhance_journals_superuser())
