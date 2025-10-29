#!/usr/bin/env python3
"""
Create professional journals table with enhanced features and RLS
FOLLOWING EXACT POSTS PATTERN
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_journals_schema():
    """Create enhanced journals table with RLS - FOLLOWING POSTS PATTERN"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Drop existing journals table and recreate with enhanced features
            await conn.execute("DROP TABLE IF EXISTS journals CASCADE;")
            print("✅ Dropped existing journals table")

            # Create enhanced journals table (PROFESSIONAL MENTAL HEALTH STANDARDS)
            await conn.execute("""
                CREATE TABLE journals (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(500), -- Optional title for journal entries
                    content TEXT NOT NULL, -- Journal content
                    content_type VARCHAR(20) DEFAULT 'journal',
                    mood VARCHAR(50), -- Mood at time of writing
                    mood_intensity INTEGER CHECK (mood_intensity >= 1 AND mood_intensity <= 10), -- 1-10 scale
                    tags TEXT[], -- Array of tags for organization
                    word_count INTEGER DEFAULT 0,
                    read_time_minutes INTEGER DEFAULT 0,
                    is_encrypted BOOLEAN DEFAULT false, -- Future: E2E encryption
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    
                    -- Journals are always private - no visibility field needed
                    CONSTRAINT valid_status CHECK (status IN ('active', 'archived', 'deleted'))
                );
            """)
            print("✅ Enhanced journals table created")

            # Create journal_prompts table for writing prompts
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

            # Add prompt_id foreign key to journals
            await conn.execute("""
                ALTER TABLE journals 
                ADD COLUMN IF NOT EXISTS prompt_id UUID REFERENCES journal_prompts(id);
            """)
            print("✅ Added prompt_id to journals")

            # Create indexes for performance
            await conn.execute("CREATE INDEX idx_journals_user_id ON journals(user_id);")
            await conn.execute("CREATE INDEX idx_journals_created_at ON journals(created_at DESC);")
            await conn.execute("CREATE INDEX idx_journals_mood ON journals(mood);")
            await conn.execute("CREATE INDEX idx_journals_tags ON journals USING GIN(tags);")
            await conn.execute("CREATE INDEX idx_journal_prompts_category ON journal_prompts(category);")
            print("✅ Indexes created")

            # Enable Row Level Security (CRITICAL FOR PRIVACY)
            await conn.execute("ALTER TABLE journals ENABLE ROW LEVEL SECURITY;")
            await conn.execute("ALTER TABLE journal_prompts ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled")

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

            # Insert sample journal prompts
            await conn.execute("""
                INSERT INTO journal_prompts (prompt_text, category, difficulty_level) VALUES
                ('What are three things you''re grateful for today?', 'gratitude', 'easy'),
                ('Describe a challenge you faced and how you overcame it.', 'resilience', 'medium'),
                ('What does self-care mean to you right now?', 'self_care', 'easy'),
                ('Write about a moment that brought you peace recently.', 'mindfulness', 'easy'),
                ('What would you tell your younger self about handling difficult emotions?', 'reflection', 'hard'),
                ('Describe your ideal mental health support system.', 'support', 'medium'),
                ('What boundaries do you need to set for your wellbeing?', 'boundaries', 'medium'),
                ('Write about a time you showed yourself compassion.', 'self_compassion', 'easy')
                ON CONFLICT DO NOTHING;
            """)
            print("✅ Sample journal prompts inserted")

            # Verify table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'journals'
                ORDER BY ordinal_position;
            """)
            print("📋 Enhanced journals table structure:")
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")

        print("🎉 Professional journals schema created successfully!")

    except Exception as e:
        print(f"❌ Journals schema creation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(create_journals_schema())
