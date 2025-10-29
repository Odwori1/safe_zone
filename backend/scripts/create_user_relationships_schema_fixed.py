#!/usr/bin/env python3
"""
Create user relationships schema following existing project patterns
INCLUDES: post_likes and comment_likes tables
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def create_likes_tables():
    """Create likes tables following existing project patterns"""
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        # Connect as superuser to create tables (following project pattern)
        superuser_url = database_url.replace(
            f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}",
            "postgres:postgres"  # Use your actual postgres credentials
        )
        
        conn = await asyncpg.connect(superuser_url)
        print("✅ Connected to database as superuser")

        # Check if tables already exist
        existing_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('post_likes', 'comment_likes')
        """)
        
        if existing_tables:
            table_names = [t['table_name'] for t in existing_tables]
            print(f"✅ Tables already exist: {table_names}")
            
            # Check if comment_likes is missing
            if 'comment_likes' not in table_names:
                print("🔧 Creating missing comment_likes table...")
                await create_comment_likes_table(conn)
        else:
            print("🔧 Creating post_likes and comment_likes tables...")
            await create_post_likes_table(conn)
            await create_comment_likes_table(conn)

        await conn.close()
        print("🎉 Likes tables setup complete!")

    except Exception as e:
        print(f"❌ Error: {e}")

async def create_post_likes_table(conn):
    """Create post_likes table following project patterns"""
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS post_likes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(post_id, user_id)
        );
    ''')
    print('✅ Created post_likes table')

    # Enable RLS
    await conn.execute('ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;')
    print('✅ Enabled RLS on post_likes')

    # Create RLS policies following project pattern
    await conn.execute('''
        CREATE POLICY "Users can view likes on posts they can see" ON post_likes
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM posts 
                WHERE posts.id = post_likes.post_id 
                AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id')::UUID)
            )
        );
    ''')

    await conn.execute('''
        CREATE POLICY "Users can like their own posts or public posts" ON post_likes
        FOR INSERT WITH CHECK (
            user_id = current_setting('app.current_user_id')::UUID
            AND EXISTS (
                SELECT 1 FROM posts 
                WHERE posts.id = post_likes.post_id 
                AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id')::UUID)
            )
        );
    ''')

    await conn.execute('''
        CREATE POLICY "Users can unlike their own likes" ON post_likes
        FOR DELETE USING (user_id = current_setting('app.current_user_id')::UUID);
    ''')
    print('✅ Created RLS policies for post_likes')

async def create_comment_likes_table(conn):
    """Create comment_likes table following project patterns"""
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS comment_likes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            comment_id UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(comment_id, user_id)
        );
    ''')
    print('✅ Created comment_likes table')

    # Enable RLS
    await conn.execute('ALTER TABLE comment_likes ENABLE ROW LEVEL SECURITY;')
    print('✅ Enabled RLS on comment_likes')

    # Create RLS policies following project pattern
    await conn.execute('''
        CREATE POLICY "Users can view likes on comments they can see" ON comment_likes
        FOR SELECT USING (
            EXISTS (
                SELECT 1 FROM comments 
                WHERE comments.id = comment_likes.comment_id 
                AND EXISTS (
                    SELECT 1 FROM posts 
                    WHERE posts.id = comments.post_id 
                    AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id')::UUID)
                )
            )
        );
    ''')

    await conn.execute('''
        CREATE POLICY "Users can like comments on posts they can see" ON comment_likes
        FOR INSERT WITH CHECK (
            user_id = current_setting('app.current_user_id')::UUID
            AND EXISTS (
                SELECT 1 FROM comments 
                WHERE comments.id = comment_likes.comment_id 
                AND EXISTS (
                    SELECT 1 FROM posts 
                    WHERE posts.id = comments.post_id 
                    AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id')::UUID)
                )
            )
        );
    ''')

    await conn.execute('''
        CREATE POLICY "Users can unlike their own likes" ON comment_likes
        FOR DELETE USING (user_id = current_setting('app.current_user_id')::UUID);
    ''')
    print('✅ Created RLS policies for comment_likes')

if __name__ == "__main__":
    asyncio.run(create_likes_tables())
