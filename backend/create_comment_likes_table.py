import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_comment_likes_table():
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        print("🔧 CREATING COMMENT_LIKES TABLE...")
        
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
        print('✅ Enabled RLS on comment_likes table')
        
        # Create RLS policies for comment_likes
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
        
        print('✅ Created RLS policies for comment_likes table')
        
        # Also check if post_likes table exists (for post likes)
        post_likes_exists = await conn.fetchval(
            "SELECT 1 FROM information_schema.tables WHERE table_name = 'post_likes'"
        )
        
        if not post_likes_exists:
            print("🔧 CREATING POST_LIKES TABLE...")
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
            print('✅ Enabled RLS on post_likes table')
            
            # Create RLS policies for post_likes
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
                CREATE POLICY "Users can like posts they can see" ON post_likes
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
            
            print('✅ Created RLS policies for post_likes table')
        else:
            print('✅ post_likes table already exists')
        
        print("🎉 DATABASE TABLES CREATED SUCCESSFULLY!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

asyncio.run(create_comment_likes_table())
