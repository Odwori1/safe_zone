import asyncio
from app.core.config import settings
import asyncpg

async def check_recent_posts():
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name
    )
    
    # Get the 10 most recent posts
    posts = await conn.fetch("""
        SELECT id, content, user_id, created_at, visibility 
        FROM posts 
        WHERE status = 'active'
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    print("🔍 10 MOST RECENT POSTS:")
    for i, post in enumerate(posts):
        print(f"  {i+1}. ID: {post['id']}")
        print(f"     User: {post['user_id']}")
        print(f"     Visibility: {post['visibility']}")
        print(f"     Content: {post['content'][:80]}...")
        print(f"     Created: {post['created_at']}")
        print()
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_recent_posts())
