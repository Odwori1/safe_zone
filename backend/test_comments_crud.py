import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database

async def test_comments_crud():
    print("🔍 TESTING COMMENTS CRUD")
    print("=" * 40)
    
    await database.connect()
    try:
        # Get a real user ID and post ID
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", "test-user")
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            post = await conn.fetchrow("SELECT id FROM posts LIMIT 1")
            
            if user and post:
                real_user_id = user['id']
                real_post_id = post['id']
                print(f"Using user ID: {real_user_id}")
                print(f"Using post ID: {real_post_id}")
                
                # Try to import and test comments CRUD
                try:
                    from app.crud.comment import comment_crud
                    print("✅ Comments CRUD imported successfully")
                    
                    # Test if comments CRUD methods work
                    try:
                        # This will fail if comments CRUD needs RLS context
                        comments = await comment_crud.get_by_post(real_post_id)
                        print(f"✅ Comments CRUD get_by_post: SUCCESS - {len(comments)} comments")
                    except Exception as e:
                        print(f"❌ Comments CRUD get_by_post failed: {e}")
                        
                except ImportError:
                    print("ℹ️  No comments CRUD found")
            else:
                print("❌ Need at least one user and post to test comments")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await database.close()

asyncio.run(test_comments_crud())
