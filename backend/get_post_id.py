import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def get_post_id():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get a post ID to test with
    post = await conn.fetchrow("SELECT id FROM posts WHERE status != 'deleted' LIMIT 1")
    if post:
        print(f'Post ID to test: {post["id"]}')
    else:
        print('No posts found in database')
        # Let's create a test post
        user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
        if user:
            test_post = await conn.fetchrow(
                "INSERT INTO posts (user_id, content, content_type, mood, visibility, is_anonymous, moderation_status) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id",
                user['id'], 'Test post for like system', 'text', 'happy', 'public', False, 'approved'
            )
            print(f'Created test post with ID: {test_post["id"]}')
    
    await conn.close()

asyncio.run(get_post_id())
