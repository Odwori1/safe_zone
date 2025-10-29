#!/usr/bin/env python3
"""
Create posts table for basic post creation - BLUEPRINT: Basic post creation (text)
UPDATED: Use app.current_user_id to match rest of system
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_posts_schema():
    """Create posts table with RLS for security - UPDATED FOR CONSISTENCY"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Drop table if exists and recreate (clean slate)
            await conn.execute("DROP TABLE IF EXISTS posts CASCADE;")
            print("✅ Dropped existing posts table")

            # Create posts table with ALL columns
            await conn.execute("""
                CREATE TABLE posts (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    content_type VARCHAR(20) DEFAULT 'text',
                    mood VARCHAR(50),
                    visibility VARCHAR(20) DEFAULT 'public',
                    is_anonymous BOOLEAN DEFAULT false,
                    status VARCHAR(20) DEFAULT 'active',
                    moderation_status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            print("✅ Posts table created with all columns")

            # Add constraints separately
            await conn.execute("""
                ALTER TABLE posts
                ADD CONSTRAINT valid_visibility
                CHECK (visibility IN ('public', 'private', 'support_group'));
            """)
            await conn.execute("""
                ALTER TABLE posts
                ADD CONSTRAINT valid_status
                CHECK (status IN ('active', 'archived', 'deleted'));
            """)
            await conn.execute("""
                ALTER TABLE posts
                ADD CONSTRAINT valid_moderation_status
                CHECK (moderation_status IN ('pending', 'approved', 'rejected', 'flagged'));
            """)
            print("✅ Constraints added")

            # Create indexes
            await conn.execute("CREATE INDEX idx_posts_user_id ON posts(user_id);")
            await conn.execute("CREATE INDEX idx_posts_created_at ON posts(created_at DESC);")
            await conn.execute("CREATE INDEX idx_posts_moderation_status ON posts(moderation_status);")
            await conn.execute("CREATE INDEX idx_posts_visibility ON posts(visibility);")
            print("✅ Indexes created")

            # Enable Row Level Security
            await conn.execute("ALTER TABLE posts ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled")

            # Create RLS policies using app.current_user_id (CONSISTENT WITH SYSTEM)
            await conn.execute("""
                -- Users can view public posts and their own posts
                CREATE POLICY "users_view_public_posts" ON posts
                    FOR SELECT USING (
                        visibility = 'public' 
                        OR user_id = current_setting('app.current_user_id', true)::uuid
                    );
                
                -- Users can insert their own posts
                CREATE POLICY "users_insert_own_posts" ON posts
                    FOR INSERT WITH CHECK (
                        user_id = current_setting('app.current_user_id', true)::uuid
                    );
                
                -- Users can update their own posts
                CREATE POLICY "users_update_own_posts" ON posts
                    FOR UPDATE USING (
                        user_id = current_setting('app.current_user_id', true)::uuid
                    );
                
                -- Users can delete their own posts
                CREATE POLICY "users_delete_own_posts" ON posts
                    FOR DELETE USING (
                        user_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)
            print("✅ RLS policies created using app.current_user_id (consistent)")

            # Verify table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'posts'
                ORDER BY ordinal_position;
            """)
            print("📋 Posts table structure:")
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']})")

        print("🎉 Posts schema created successfully with consistent RLS!")

    except Exception as e:
        print(f"❌ Posts schema creation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(create_posts_schema())
