import asyncio
import asyncpg
from app.core.config import settings

async def test_posts_directly():
    conn = await asyncpg.connect(settings.database_url)
    try:
        # Test without RLS context
        posts = await conn.fetch("SELECT * FROM posts WHERE user_id = $1", 'ccf58f87-472c-46ff-8475-108055247ea2')
        print(f"Direct query found {len(posts)} posts")
        
        # Test with RLS context
        await conn.execute("SELECT set_config('app.current_user_id', $1, false)", 'ccf58f87-472c-46ff-8475-108055247ea2')
        posts_with_rls = await conn.fetch("SELECT * FROM posts WHERE status = 'active'")
        print(f"With RLS context found {len(posts_with_rls)} posts")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(test_posts_directly())
