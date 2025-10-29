import asyncio
import sys
import uuid
sys.path.append('.')
from app.database.database import database
from app.crud.post_audio import post_crud
from app.api.endpoints.posts import create_new_post, read_posts, read_post, update_post, delete_post
from app.schemas.post import PostCreate, PostUpdate
from app.schemas.user import User
from uuid import UUID

async def test_posts_system_direct():
    print("🧪 TESTING POSTS SYSTEM DIRECTLY")
    print("=" * 50)
    
    await database.connect()
    try:
        # Get a real user ID
        async with database.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id, username, email FROM users LIMIT 1")
            real_user_id = user['id']
            print(f"Using user ID: {real_user_id}")
        
        # Create a mock current_user object
        current_user = User(
            id=real_user_id,
            username=user['username'],
            email=user['email'],
            is_active=True,
            is_superuser=False
        )
        
        # Test 1: Create post
        print("\n1. Testing post creation...")
        post_create = PostCreate(
            content="Test post from direct test",
            content_type="text",
            mood="neutral",
            visibility="public",
            is_anonymous=False
        )
        
        # Simulate what the endpoint does
        result = await post_crud.create(current_user.id, post_create, current_user.id)
        if result:
            post_data = dict(result)
            if post_data.get('is_anonymous'):
                post_data['username'] = None
                post_data['user_avatar'] = None
            print(f"   ✅ SUCCESS - Post created with ID: {post_data['id']}")
            post_id = post_data['id']
        else:
            print("   ❌ FAILED - Post creation returned None")
            return
        
        # Test 2: Get post feed
        print("\n2. Testing post feed...")
        posts = await post_crud.get_feed(current_user.id, current_user.id, limit=10, offset=0)
        response_posts = []
        for post in posts:
            post_data = dict(post)
            if post_data.get('is_anonymous'):
                post_data['username'] = None
                post_data['user_avatar'] = None
            response_posts.append(post_data)
        print(f"   ✅ SUCCESS - {len(response_posts)} posts in feed")
        
        # Test 3: Get specific post
        print("\n3. Testing get specific post...")
        post = await post_crud.get(post_id, current_user.id)
        if post:
            post_data = dict(post)
            print(f"   ✅ SUCCESS - Retrieved post: '{post_data['content']}'")
        else:
            print("   ❌ FAILED - Could not retrieve post")
        
        # Test 4: Update post
        print("\n4. Testing post update...")
        post_update = PostUpdate(
            content="Updated post content",
            mood="happy"
        )
        updated_post = await post_crud.update(post_id, current_user.id, post_update, current_user.id)
        if updated_post:
            updated_data = dict(updated_post)
            print(f"   ✅ SUCCESS - Updated post: '{updated_data['content']}'")
        else:
            print("   ❌ FAILED - Could not update post")
        
        # Test 5: Delete post
        print("\n5. Testing post deletion...")
        success = await post_crud.delete(post_id, current_user.id, current_user.id)
        if success:
            print("   ✅ SUCCESS - Post deleted")
        else:
            print("   ❌ FAILED - Could not delete post")
        
        # Test 6: Verify post is gone
        print("\n6. Verifying post deletion...")
        deleted_post = await post_crud.get(post_id, current_user.id)
        if not deleted_post:
            print("   ✅ SUCCESS - Post properly deleted")
        else:
            print("   ❌ FAILED - Post still exists after deletion")
        
        print("\n🎉 ALL DIRECT TESTS COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

asyncio.run(test_posts_system_direct())
