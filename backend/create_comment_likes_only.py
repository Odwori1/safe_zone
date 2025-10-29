import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_comment_likes_only():
    """Create only the comment_likes table that's missing"""
    # Use postgres superuser to bypass permission issues
    database_url = "postgresql://postgres:postgres@localhost:5433/safe_zone"
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected as postgres superuser")

        # Create comment_likes table
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

        # Create RLS policies
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

        # Grant permissions to app user
        await conn.execute('GRANT ALL ON comment_likes TO safe_zone_app_user;')
        await conn.execute('GRANT ALL ON SEQUENCE comment_likes_id_seq TO safe_zone_app_user;')
        print('✅ Granted permissions to safe_zone_app_user')

        await conn.close()
        print("🎉 comment_likes table created successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(create_comment_likes_only())
