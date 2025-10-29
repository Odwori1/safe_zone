import asyncio
import sys
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud
from app.crud.comment import comment_crud

async def test_final_verification():
    print("🎯 FINAL VERIFICATION - POSTS & COMMENTS")
    print("=" * 50)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")

        # Test posts creation
        print("\n1. Testing posts system...")
        post_data = type('PostIn', (), {
            'content': 'Final test post',
            'content_type': 'text',
            'mood': 'happy',
            'visibility': 'public',
            'is_anonymous': False,
            'audio_url': None,
            'audio_duration': None,
            'file_size': None,
            'mime_type': None
        })()
        
        post = await post_crud.create(real_user_id, post_data, real_user_id)
        print(f"   ✅ Posts: SUCCESS - Post created: {post['id']}")
        post_id = post['id']

        # Test comments creation
        print("\n2. Testing comments system...")
        comment_data = type('CommentIn', (), {
            'content': 'Final test comment',
            'parent_comment_id': None
        })()
        
        comment = await comment_crud.create(real_user_id, post_id, comment_data, real_user_id)
        print(f"   ✅ Comments: SUCCESS - Comment created: {comment['id']}")

        # Test reading both
        print("\n3. Testing data retrieval...")
        posts = await post_crud.get_feed(real_user_id, real_user_id, limit=5, offset=0)
        comments = await comment_crud.get_by_post(post_id, real_user_id, limit=5, offset=0)
        print(f"   ✅ Retrieval: SUCCESS - {len(posts)} posts, {len(comments)} comments")

        # Clean up
        await comment_crud.delete(comment['id'], real_user_id, real_user_id)
        await post_crud.delete(post_id, real_user_id, real_user_id)
        print("   ✅ Cleanup: SUCCESS")
        
        print("\n🎉 FINAL VERIFICATION COMPLETED - ALL SYSTEMS WORKING!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_final_verification())
