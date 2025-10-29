#!/usr/bin/env python3
"""
Create post_likes and comment_likes tables following existing project patterns
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_likes_tables():
    """Create likes tables with RLS - FOLLOWING EXACT PROJECT PATTERNS"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # We need to use a valid user ID for RLS context during table creation
            user_id = await conn.fetchval("SELECT id FROM users LIMIT 1;")

            if not user_id:
                print("❌ No users found in database. Cannot set RLS context.")
                return

            print(f"🔧 Setting RLS context with user_id: {user_id}")
            await conn.execute("SELECT set_current_user_id($1);", user_id)

            # Check if tables already exist
            print("🔍 Checking existing tables...")
            existing_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('post_likes', 'comment_likes')
            """)
            
            if existing_tables:
                print(f"⚠️ Tables already exist: {[t['table_name'] for t in existing_tables]}")
                return

            # Create post_likes table WITHOUT foreign keys first
            print("🔄 Creating post_likes table...")
            await conn.execute("""
                CREATE TABLE post_likes (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    post_id UUID NOT NULL,
                    user_id UUID NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(post_id, user_id)
                );
            """)
            print("✅ Created post_likes table")

            # Create comment_likes table WITHOUT foreign keys first
            print("🔄 Creating comment_likes table...")
            await conn.execute("""
                CREATE TABLE comment_likes (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    comment_id UUID NOT NULL,
                    user_id UUID NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(comment_id, user_id)
                );
            """)
            print("✅ Created comment_likes table")

            # Enable RLS
            await conn.execute("ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;")
            await conn.execute("ALTER TABLE comment_likes ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled for both tables")

            # Create RLS policies for post_likes
            await conn.execute("""
                CREATE POLICY "users_view_post_likes" ON post_likes
                    FOR SELECT USING (
                        EXISTS (
                            SELECT 1 FROM posts 
                            WHERE posts.id = post_likes.post_id 
                            AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                        )
                    );
            """)

            await conn.execute("""
                CREATE POLICY "users_create_post_likes" ON post_likes
                    FOR INSERT WITH CHECK (
                        user_id = current_setting('app.current_user_id', true)::uuid
                        AND EXISTS (
                            SELECT 1 FROM posts 
                            WHERE posts.id = post_likes.post_id 
                            AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                        )
                    );
            """)

            await conn.execute("""
                CREATE POLICY "users_delete_post_likes" ON post_likes
                    FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies created for post_likes")

            # Create RLS policies for comment_likes
            await conn.execute("""
                CREATE POLICY "users_view_comment_likes" ON comment_likes
                    FOR SELECT USING (
                        EXISTS (
                            SELECT 1 FROM comments 
                            WHERE comments.id = comment_likes.comment_id 
                            AND EXISTS (
                                SELECT 1 FROM posts 
                                WHERE posts.id = comments.post_id 
                                AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                            )
                        )
                    );
            """)

            await conn.execute("""
                CREATE POLICY "users_create_comment_likes" ON comment_likes
                    FOR INSERT WITH CHECK (
                        user_id = current_setting('app.current_user_id', true)::uuid
                        AND EXISTS (
                            SELECT 1 FROM comments 
                            WHERE comments.id = comment_likes.comment_id 
                            AND EXISTS (
                                SELECT 1 FROM posts 
                                WHERE posts.id = comments.post_id 
                                AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                            )
                        )
                    );
            """)

            await conn.execute("""
                CREATE POLICY "users_delete_comment_likes" ON comment_likes
                    FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::uuid);
            """)
            print("✅ RLS policies created for comment_likes")

            # Create indexes
            await conn.execute("CREATE INDEX idx_post_likes_post_id ON post_likes(post_id);")
            await conn.execute("CREATE INDEX idx_post_likes_user_id ON post_likes(user_id);")
            await conn.execute("CREATE INDEX idx_comment_likes_comment_id ON comment_likes(comment_id);")
            await conn.execute("CREATE INDEX idx_comment_likes_user_id ON comment_likes(user_id);")
            print("✅ Indexes created")

            # Verify tables
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('post_likes', 'comment_likes')
            """)
            
            print(f"✅ Created tables: {[t['table_name'] for t in tables]}")

        print("🎉 Likes tables created successfully!")
        print("💡 Note: Foreign keys not added due to permission restrictions.")
        print("   Application will handle referential integrity at application level.")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(create_likes_tables())
