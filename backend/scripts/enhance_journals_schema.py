#!/usr/bin/env python3
"""
Enhance existing journals table with professional features and RLS
FOLLOWING EXACT PROJECT PATTERNS - NO TABLE DROP
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def enhance_journals_schema():
    """Enhance existing journals table with professional features"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Check if journals table exists and get current structure
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'journals'
                );
            """)
            
            if not table_exists:
                print("❌ Journals table does not exist. Please run init_database.py first.")
                return

            print("📋 Current journals table structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'journals'
                ORDER BY ordinal_position;
            """)
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

            # Add missing columns to existing journals table
            print("🔄 Adding enhanced columns to journals table...")
            
            # Add title column if missing
            try:
                await conn.execute("ALTER TABLE journals ADD COLUMN IF NOT EXISTS title VARCHAR(500);")
                print("✅ Added title column")
            except Exception as e:
                print(f"⚠️ Could not add title column: {e}")

            # Add content_type column if missing
            try:
                await conn.execute("ALTER TABLE journals ADD COLUMN IF NOT EXISTS content_type VARCHAR(20) DEFAULT 'journal';")
                print("✅ Added content_type column")
            except Exception as e:
                print(f"⚠️ Could not add content_type column: {e}")

            # Add mood_intensity column if missing
            try:
                await conn.execute("""
                    ALTER TABLE journals ADD COLUMN IF NOT EXISTS mood_intensity INTEGER;
                    ALTER TABLE journals ADD CONSTRAINT mood_intensity_range 
                    CHECK (mood_intensity >= 1 AND mood_intensity <= 10);
                """)
                print("✅ Added mood_intensity column with constraint")
            except Exception as e:
                print(f"⚠️ Could not add mood_intensity column: {e}")

            # Add tags array column if missing
            try:
                await conn.execute("ALTER TABLE journals ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';")
                print("✅ Added tags column")
            except Exception as e:
                print(f"⚠️ Could not add tags column: {e}")

            # Add word_count column if missing
            try:
                await conn.execute("ALTER TABLE journals ADD COLUMN IF NOT EXISTS word_count INTEGER DEFAULT 0;")
                print("✅ Added word_count column")
            except Exception as e:
                print(f"⚠️ Could not add word_count column: {e}")

            # Add read_time_minutes column if missing
            try:
                await conn.execute("ALTER TABLE journals ADD COLUMN IF NOT EXISTS read_time_minutes INTEGER DEFAULT 0;")
                print("✅ Added read_time_minutes column")
            except Exception as e:
                print(f"⚠️ Could not add read_time_minutes column: {e}")

            # Add is_encrypted column if missing
            try:
                await conn.execute("ALTER TABLE journals ADD COLUMN IF NOT EXISTS is_encrypted BOOLEAN DEFAULT false;")
                print("✅ Added is_encrypted column")
            except Exception as e:
                print(f"⚠️ Could not add is_encrypted column: {e}")

            # Add status column if missing
            try:
                await conn.execute("""
                    ALTER TABLE journals ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';
                    ALTER TABLE journals ADD CONSTRAINT valid_journal_status 
                    CHECK (status IN ('active', 'archived', 'deleted'));
                """)
                print("✅ Added status column with constraint")
            except Exception as e:
                print(f"⚠️ Could not add status column: {e}")

            # Add updated_at trigger if missing
            try:
                await conn.execute("""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';

                    DROP TRIGGER IF EXISTS update_journals_updated_at ON journals;
                    CREATE TRIGGER update_journals_updated_at
                        BEFORE UPDATE ON journals
                        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """)
                print("✅ Added updated_at trigger")
            except Exception as e:
                print(f"⚠️ Could not add updated_at trigger: {e}")

            # Create journal_prompts table if not exists
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
            print("✅ Journal prompts table created/verified")

            # Add prompt_id foreign key to journals if not exists
            try:
                await conn.execute("""
                    ALTER TABLE journals 
                    ADD COLUMN IF NOT EXISTS prompt_id UUID REFERENCES journal_prompts(id);
                """)
                print("✅ Added prompt_id to journals")
            except Exception as e:
                print(f"⚠️ Could not add prompt_id: {e}")

            # Create indexes for performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_journals_user_id ON journals(user_id);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_journals_created_at ON journals(created_at DESC);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_journals_mood ON journals(mood);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_journals_tags ON journals USING GIN(tags);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_journal_prompts_category ON journal_prompts(category);")
            print("✅ Indexes created/verified")

            # Enable Row Level Security if not enabled
            rls_enabled = await conn.fetchval("""
                SELECT relrowsecurity FROM pg_class WHERE relname = 'journals';
            """)
            if not rls_enabled:
                await conn.execute("ALTER TABLE journals ENABLE ROW LEVEL SECURITY;")
                print("✅ RLS enabled on journals")
            else:
                print("✅ RLS already enabled on journals")

            # Check existing RLS policies
            existing_policies = await conn.fetch("""
                SELECT policyname FROM pg_policies WHERE tablename = 'journals';
            """)
            
            if not existing_policies:
                # Create STRICT RLS policies for journals (STRICTER THAN POSTS)
                await conn.execute("""
                    -- Users can ONLY view their own journals (no public visibility)
                    CREATE POLICY "users_view_own_journals" ON journals
                        FOR SELECT USING (
                            user_id = current_setting('app.current_user_id', true)::uuid
                        );

                    -- Users can ONLY insert their own journals
                    CREATE POLICY "users_insert_own_journals" ON journals
                        FOR INSERT WITH CHECK (
                            user_id = current_setting('app.current_user_id', true)::uuid
                        );

                    -- Users can ONLY update their own journals
                    CREATE POLICY "users_update_own_journals" ON journals
                        FOR UPDATE USING (
                            user_id = current_setting('app.current_user_id', true)::uuid
                        );

                    -- Users can ONLY delete their own journals
                    CREATE POLICY "users_delete_own_journals" ON journals
                        FOR DELETE USING (
                            user_id = current_setting('app.current_user_id', true)::uuid
                        );
                """)
                print("✅ STRICT RLS policies created for journals")
            else:
                policy_names = [p['policyname'] for p in existing_policies]
                print(f"✅ RLS policies already exist: {policy_names}")

            # Enable RLS for journal_prompts if not enabled
            prompts_rls_enabled = await conn.fetchval("""
                SELECT relrowsecurity FROM pg_class WHERE relname = 'journal_prompts';
            """)
            if not prompts_rls_enabled:
                await conn.execute("ALTER TABLE journal_prompts ENABLE ROW LEVEL SECURITY;")
                print("✅ RLS enabled on journal_prompts")

            # Check existing RLS policies for prompts
            prompt_policies = await conn.fetch("""
                SELECT policyname FROM pg_policies WHERE tablename = 'journal_prompts';
            """)
            
            if not prompt_policies:
                # RLS policies for journal_prompts (public read, admin write)
                await conn.execute("""
                    -- Anyone can view active prompts
                    CREATE POLICY "anyone_view_prompts" ON journal_prompts
                        FOR SELECT USING (is_active = true);

                    -- Only admins can manage prompts (placeholder for future)
                    CREATE POLICY "admins_manage_prompts" ON journal_prompts
                        FOR ALL USING (false); -- Disabled until admin system
                """)
                print("✅ RLS policies created for journal_prompts")
            else:
                prompt_policy_names = [p['policyname'] for p in prompt_policies]
                print(f"✅ RLS policies already exist for prompts: {prompt_policy_names}")

            # Insert sample journal prompts if none exist
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
                print(f"✅ Inserted {prompt_count} sample journal prompts")
            else:
                print(f"✅ Journal prompts already exist: {prompt_count} prompts")

            # Verify final table structure
            final_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'journals'
                ORDER BY ordinal_position;
            """)
            print("📋 Enhanced journals table structure:")
            for col in final_columns:
                print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        print("🎉 Professional journals schema enhancement completed successfully!")

    except Exception as e:
        print(f"❌ Journals schema enhancement failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(enhance_journals_schema())
