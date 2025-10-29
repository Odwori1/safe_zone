#!/usr/bin/env python3
"""
Create comments table for basic commenting system - BLUEPRINT: Basic commenting system
UPDATED: Use app.current_user_id to match rest of system
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_comments_schema():
    """Create comments table with RLS for security - UPDATED FOR CONSISTENCY"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Drop table if exists and recreate (clean slate)
            await conn.execute("DROP TABLE IF EXISTS comments CASCADE;")
            print("✅ Dropped existing comments table")

            # Create comments table
            await conn.execute("""
                CREATE TABLE comments (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    parent_comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    is_anonymous BOOLEAN DEFAULT false,
                    status VARCHAR(20) DEFAULT 'active',
                    moderation_status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            print("✅ Comments table created with all columns")

            # Add constraints
            await conn.execute("""
                ALTER TABLE comments
                ADD CONSTRAINT valid_status
                CHECK (status IN ('active', 'archived', 'deleted'));
            """)
            await conn.execute("""
                ALTER TABLE comments
                ADD CONSTRAINT valid_moderation_status
                CHECK (moderation_status IN ('pending', 'approved', 'rejected', 'flagged'));
            """)
            await conn.execute("""
                ALTER TABLE comments
                ADD CONSTRAINT comment_content_not_empty
                CHECK (length(trim(content)) > 0);
            """)
            print("✅ Constraints added")

            # Create indexes
            await conn.execute("CREATE INDEX idx_comments_user_id ON comments(user_id);")
            await conn.execute("CREATE INDEX idx_comments_post_id ON comments(post_id);")
            await conn.execute("CREATE INDEX idx_comments_parent_id ON comments(parent_comment_id);")
            await conn.execute("CREATE INDEX idx_comments_created_at ON comments(created_at DESC);")
            await conn.execute("CREATE INDEX idx_comments_moderation_status ON comments(moderation_status);")
            print("✅ Indexes created")

            # Enable Row Level Security
            await conn.execute("ALTER TABLE comments ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled")

            # Create RLS policies using app.current_user_id (CONSISTENT WITH SYSTEM)
            await conn.execute("""
                -- Users can view comments on posts they can see
                CREATE POLICY "users_view_comments" ON comments
                    FOR SELECT USING (
                        EXISTS (
                            SELECT 1 FROM posts 
                            WHERE posts.id = comments.post_id 
                            AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                        )
                    );

                -- Users can insert their own comments
                CREATE POLICY "users_insert_own_comments" ON comments
                    FOR INSERT WITH CHECK (
                        user_id = current_setting('app.current_user_id', true)::uuid
                    );

                -- Users can update their own comments
                CREATE POLICY "users_update_own_comments" ON comments
                    FOR UPDATE USING (
                        user_id = current_setting('app.current_user_id', true)::uuid
                    );

                -- Users can delete their own comments
                CREATE POLICY "users_delete_own_comments" ON comments
                    FOR DELETE USING (
                        user_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)
            print("✅ RLS policies created using app.current_user_id (consistent)")

            # Verify table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'comments'
                ORDER BY ordinal_position;
            """)
            print("📋 Comments table structure:")
            for col in columns:
                print(f"   - {col['column_name']} ({col['data_type']})")

        print("🎉 Comments schema created successfully with consistent RLS!")

    except Exception as e:
        print(f"❌ Comments schema creation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(create_comments_schema())
