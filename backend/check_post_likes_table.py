import asyncio
import asyncpg
from app.core.config import settings

async def check_post_likes_table():
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.database_url)
        
        # Check if table exists
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'post_likes')"
        )
        
        if table_exists:
            print("✅ post_likes table exists")
            
            # Check table structure
            columns = await conn.fetch(
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'post_likes'"
            )
            print("📋 Table structure:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
                
        else:
            print("❌ post_likes table does not exist")
            print("📝 Creating post_likes table...")
            
            # Create the table
            await conn.execute('''
                CREATE TABLE post_likes (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(post_id, user_id)
                );
                
                -- Add RLS policies
                ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;
                
                -- Policy: Users can see all likes
                CREATE POLICY "Users can view all likes" ON post_likes
                    FOR SELECT USING (true);
                
                -- Policy: Users can only insert their own likes
                CREATE POLICY "Users can insert their own likes" ON post_likes
                    FOR INSERT WITH CHECK (auth.uid() = user_id);
                
                -- Policy: Users can only delete their own likes
                CREATE POLICY "Users can delete their own likes" ON post_likes
                    FOR DELETE USING (auth.uid() = user_id);
            ''')
            
            print("✅ post_likes table created successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_post_likes_table())
