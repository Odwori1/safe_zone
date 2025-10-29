import asyncio
import asyncpg
from app.core.config import settings

async def create_post_likes_table():
    """
    Safely create post_likes table following existing RLS patterns
    """
    try:
        # Connect to database using the same settings
        conn = await asyncpg.connect(settings.database_url)
        
        print("🔧 Creating post_likes table with RLS policies...")
        
        # Create the table following existing patterns
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS post_likes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(post_id, user_id)
            );
        ''')
        
        print("✅ post_likes table created")
        
        # Enable RLS (following existing pattern)
        await conn.execute('ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;')
        print("✅ RLS enabled")
        
        # Create RLS policies following the same pattern as other tables
        # Policy: Users can see all likes (same as posts visibility)
        await conn.execute('''
            CREATE POLICY "Users can view all likes" ON post_likes
                FOR SELECT USING (true);
        ''')
        print("✅ SELECT policy created")
        
        # Policy: Users can only insert their own likes
        await conn.execute('''
            CREATE POLICY "Users can insert their own likes" ON post_likes
                FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::uuid);
        ''')
        print("✅ INSERT policy created")
        
        # Policy: Users can only delete their own likes  
        await conn.execute('''
            CREATE POLICY "Users can delete their own likes" ON post_likes
                FOR DELETE USING (user_id = current_setting('app.current_user_id')::uuid);
        ''')
        print("✅ DELETE policy created")
        
        # Verify the table was created
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'post_likes')"
        )
        
        if table_exists:
            print("🎉 post_likes table created successfully with RLS policies!")
            
            # Show table structure
            columns = await conn.fetch(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'post_likes'"
            )
            print("📋 Table structure:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ Failed to create post_likes table")
            
    except Exception as e:
        print(f"❌ Error creating post_likes table: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_post_likes_table())
