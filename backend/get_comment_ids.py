import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def get_comment_ids():
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    conn = await asyncpg.connect(database_url)
    
    # Get some comment IDs
    comments = await conn.fetch("""
        SELECT id, content, post_id, user_id, created_at 
        FROM comments 
        WHERE status != 'deleted' 
        LIMIT 5
    """)
    
    if comments:
        print("💬 COMMENTS FOUND:")
        for comment in comments:
            print(f"Comment ID: {comment['id']}")
            print(f"Content: {comment['content'][:50]}...")
            print(f"Post ID: {comment['post_id']}")
            print(f"User ID: {comment['user_id']}")
            print("---")
    else:
        print("❌ No comments found")
        
    await conn.close()

asyncio.run(get_comment_ids())
