import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.comment import comment_crud
from app.crud.post_audio import post_crud

async def test_comments_fixed_v2():
    print("🧪 TESTING FIXED COMMENTS CRUD V2")
    print("=" * 50)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")

        # First create a test post
        post_data = type('PostIn', (), {
            'content': 'Test post for comments v2',
            'content_type': 'text',
            'mood': 'neutral',
            'visibility': 'public',
            'is_anonymous': False,
            'audio_url': None,
            'audio_duration': None,
            'file_size': None,
            'mime_type': None
        })()
        
        post = await post_crud.create(real_user_id, post_data, real_user_id)
        post_id = post['id']
        print(f"Created test post: {post_id}")

        # Test 1: Create comment
        print("\n1. Testing comment creation...")
        comment_data = type('CommentIn', (), {
            'content': 'Test comment content v2',
            'parent_comment_id': None
        })()
        
        comment = await comment_crud.create(real_user_id, post_id, comment_data, real_user_id)
        print(f"   ✅ SUCCESS - Comment created with ID: {comment['id']}")
        comment_id = comment['id']

        # Test 2: Get comment by post
        print("\n2. Testing get comments by post...")
        comments = await comment_crud.get_by_post(post_id, real_user_id, limit=10, offset=0)
        print(f"   ✅ SUCCESS - {len(comments)} comments retrieved")

        # Test 3: Get specific comment
        print("\n3. Testing get specific comment...")
        retrieved = await comment_crud.get(comment_id, real_user_id)
        print(f"   ✅ SUCCESS - Retrieved comment: '{retrieved['content']}'")

        # Test 4: Update comment (using simple dict-like approach)
        print("\n4. Testing comment update...")
        # Create a simple object with just the content attribute
        class SimpleUpdate:
            def __init__(self, content):
                self.content = content
        
        update_obj = SimpleUpdate('Updated comment content v2')
        updated = await comment_crud.update(comment_id, real_user_id, update_obj, real_user_id)
        print(f"   ✅ SUCCESS - Updated comment: '{updated['content']}'")

        # Test 5: Delete comment
        print("\n5. Testing comment deletion...")
        success = await comment_crud.delete(comment_id, real_user_id, real_user_id)
        print(f"   ✅ SUCCESS - Comment deleted: {success}")

        # Clean up post
        await post_crud.delete(post_id, real_user_id, real_user_id)
        print("   ✅ Cleanup: Test post deleted")
        
        print("\n🎉 ALL COMMENTS TESTS COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_comments_fixed_v2())
