import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud

async def test_fixed_posts():
    print("🧪 TESTING FIXED POSTS CRUD")
    print("=" * 50)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")

        # Test 1: Create post (should work now)
        print("\n1. Testing post creation...")
        try:
            post_data = type('PostIn', (), {
                'content': 'Test post with fixed CRUD',
                'content_type': 'text',
                'mood': 'neutral',
                'visibility': 'public',
                'is_anonymous': False,
                'audio_url': None,
                'audio_duration': None,
                'file_size': None,
                'mime_type': None
            })()
            
            result = await post_crud.create(real_user_id, post_data, real_user_id)
            print(f"   ✅ SUCCESS: Post created with ID: {result['id']}")
            
            # Test 2: Get the post back
            print("\n2. Testing post retrieval...")
            retrieved = await post_crud.get(result['id'], real_user_id)
            print(f"   ✅ SUCCESS: Retrieved post: '{retrieved['content']}'")
            
            # Test 3: Count user posts
            print("\n3. Testing post count...")
            count = await post_crud.count_user_posts(real_user_id, real_user_id)
            print(f"   ✅ SUCCESS: User has {count} posts")
            
            # Clean up
            await post_crud.delete(result['id'], real_user_id, real_user_id)
            print("   ✅ Cleanup: Test post deleted")
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"General error: {e}")
    finally:
        await database.close()
    print("\n" + "=" * 50)

asyncio.run(test_fixed_posts())
