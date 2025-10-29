import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud

async def test_current_posts_audio():
    print("🔍 TESTING CURRENT POSTS AUDIO CRUD (NO CHANGES)")
    print("=" * 60)
    
    await database.connect()
    try:
        # Use a real user ID from the database for testing
        async with database.pool.acquire() as conn:
            # Get a real user ID from the database
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            if not user:
                print("❌ No users found in database")
                return
                
            real_user_id = user['id']
            print(f"Using real user ID: {real_user_id}")
        
        # Test 1: Test get_feed method (should work for reading)
        print("\n1. Testing get_feed (read operation)...")
        try:
            feed = await post_crud.get_feed(real_user_id, limit=5, offset=0)
            print(f"   ✅ get_feed: SUCCESS - {len(feed)} posts")
        except Exception as e:
            print(f"   ❌ get_feed error: {e}")
        
        # Test 2: Test get_by_user method  
        print("\n2. Testing get_by_user (read operation)...")
        try:
            user_posts = await post_crud.get_by_user(real_user_id, limit=5, offset=0)
            print(f"   ✅ get_by_user: SUCCESS - {len(user_posts)} posts")
        except Exception as e:
            print(f"   ❌ get_by_user error: {e}")
            
        # Test 3: Test create method (this should fail with RLS)
        print("\n3. Testing create method (write operation - should fail)...")
        try:
            post_data = type('PostIn', (), {
                'content': 'Test post from current CRUD',
                'content_type': 'text',
                'mood': 'neutral',
                'visibility': 'public',
                'is_anonymous': False,
                'audio_url': None,
                'audio_duration': None,
                'file_size': None,
                'mime_type': None
            })()
            
            result = await post_crud.create(real_user_id, post_data)
            print(f"   ✅ create: SUCCESS - Post created with ID: {result['id']}")
        except Exception as e:
            print(f"   ❌ create error: {e}")
            
        # Test 4: Test count_user_posts method
        print("\n4. Testing count_user_posts...")
        try:
            count = await post_crud.count_user_posts(real_user_id)
            print(f"   ✅ count_user_posts: SUCCESS - {count} posts")
        except Exception as e:
            print(f"   ❌ count_user_posts error: {e}")
            
        # Test 5: Let's check what methods are available
        print("\n5. Available CRUD methods:")
        methods = [method for method in dir(post_crud) if not method.startswith('_')]
        for method in methods:
            print(f"   - {method}")
            
    except Exception as e:
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()
    print("\n" + "=" * 60)

asyncio.run(test_current_posts_audio())
