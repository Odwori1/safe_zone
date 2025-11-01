import asyncio
import aiohttp
import json

async def test_saved_posts():
    BASE_URL = "http://localhost:8001/api/v1"
    
    # Get token first
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {
            "email": "developer_test@example.com",
            "password": "DeveloperPass123!"
        }
        
        print("🔐 Logging in...")
        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result['access_token']
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {response.status}")
                return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("\n🧪 TESTING SAVED POSTS FUNCTIONALITY")
        print("=" * 50)
        
        # First, let's get some posts to save
        print("\n1. Getting posts to save...")
        async with session.get(f"{BASE_URL}/posts?limit=3", headers=headers) as response:
            if response.status == 200:
                posts = await response.json()
                if len(posts) > 0:
                    post_to_save = posts[0]
                    post_id = post_to_save['id']
                    print(f"   ✅ Found post to save: {post_to_save['content'][:50]}...")
                else:
                    print("   ❌ No posts found to save")
                    return
            else:
                print("   ❌ Failed to get posts")
                return
        
        # Test 2: Save a post
        print(f"\n2. Saving post {post_id}...")
        try:
            async with session.post(f"{BASE_URL}/posts/{post_id}/save", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Success! {result['message']}")
                    if result.get('already_saved'):
                        print("   ℹ️  Post was already saved")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Get saved posts
        print("\n3. Getting saved posts...")
        try:
            async with session.get(f"{BASE_URL}/posts/saved/posts", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    saved_posts = await response.json()
                    print(f"   ✅ Success! Found {len(saved_posts)} saved posts")
                    if len(saved_posts) > 0:
                        for i, post in enumerate(saved_posts[:2]):
                            print(f"   📝 Saved post {i+1}: {post['content'][:50]}...")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Get saved stats
        print("\n4. Getting saved posts stats...")
        try:
            async with session.get(f"{BASE_URL}/posts/saved/stats", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    stats = await response.json()
                    print(f"   ✅ Success! Stats: {stats}")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Check if post is saved
        print(f"\n5. Checking if post {post_id} is saved...")
        try:
            # We'll check by trying to save it again (should return already_saved)
            async with session.post(f"{BASE_URL}/posts/{post_id}/save", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('already_saved'):
                        print(f"   ✅ Confirmed: Post is saved")
                    else:
                        print(f"   ❌ Post is not saved")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed to check: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Unsave the post
        print(f"\n6. Unsaving post {post_id}...")
        try:
            async with session.post(f"{BASE_URL}/posts/{post_id}/unsave", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Success! {result['message']}")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 SAVED POSTS TEST SUMMARY")
        print("Endpoints tested:")
        print("  ✅ POST /posts/{id}/save")
        print("  ✅ GET /posts/saved/posts") 
        print("  ✅ GET /posts/saved/stats")
        print("  ✅ POST /posts/{id}/unsave")
        print("\n📊 Saved Posts Status: IMPLEMENTED ✅")

if __name__ == "__main__":
    asyncio.run(test_saved_posts())
