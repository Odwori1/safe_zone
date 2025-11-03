import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_shared_posts():
    # Use the same connection settings as the main app
    from app.core.config import settings
    
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name
    )
    
    # Check recent posts
    posts = await conn.fetch("""
        SELECT id, content, user_id, created_at, content_type 
        FROM posts 
        WHERE content LIKE '%Shared from%' 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    print("🔍 RECENT SHARED POSTS:")
    for post in posts:
        print(f"  - ID: {post['id']}")
        print(f"    User: {post['user_id']}")
        print(f"    Content: {post['content'][:100]}...")
        print(f"    Created: {post['created_at']}")
        print()
    
    # Check post_shares table
    shares = await conn.fetch("SELECT * FROM post_shares ORDER BY created_at DESC LIMIT 10")
    print("🔍 RECENT SHARE RECORDS:")
    for share in shares:
        print(f"  - Post: {share['post_id']}, User: {share['user_id']}, Created: {share['created_at']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_shared_posts())
