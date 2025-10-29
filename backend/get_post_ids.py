import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def get_post_ids():
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Get some actual post IDs
        posts = await conn.fetch("""
            SELECT id, content, user_id, created_at 
            FROM posts 
            WHERE status != 'deleted' 
            LIMIT 5
        """)
        
        if posts:
            print("📝 ACTUAL POSTS FOUND:")
            for post in posts:
                print(f"ID: {post['id']}")
                print(f"Content: {post['content'][:50]}...")
                print(f"User ID: {post['user_id']}")
                print(f"Created: {post['created_at']}")
                print("---")
        else:
            print("❌ No posts found in the database")
            print("Let's create a test post...")
            
            # Get a user to create a post with
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            if user:
                test_post = await conn.fetchrow(
                    "INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous, moderation_status) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id, content",
                    user['id'], 'Test post for like system verification', 'text', 'happy', 'public', False, 'approved'
                )
                print(f"✅ Created test post:")
                print(f"ID: {test_post['id']}")
                print(f"Content: {test_post['content']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Please make sure your database is running on port 5433")

asyncio.run(get_post_ids())
