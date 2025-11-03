import asyncio
from app.core.config import settings
import asyncpg

async def check_post_status():
    conn = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name
    )
    
    # Check the specific shared post
    post = await conn.fetchrow("""
        SELECT id, content, user_id, status, moderation_status, visibility
        FROM posts 
        WHERE id = 'd27fe40b-e361-4f6a-bc50-8ebdf9d37d6a'
    """)
    
    print("🔍 SHARED POST STATUS:")
    print(f"  ID: {post['id']}")
    print(f"  Status: {post['status']}")
    print(f"  Moderation Status: {post['moderation_status']}")
    print(f"  Visibility: {post['visibility']}")
    print(f"  User ID: {post['user_id']}")
    print(f"  Content: {post['content'][:100]}...")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_post_status())
