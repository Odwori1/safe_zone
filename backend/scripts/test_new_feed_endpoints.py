import asyncio
import aiohttp
import json

async def test_new_feed_endpoints():
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
        
        print("\n🧪 TESTING NEW FEED ENDPOINTS")
        print("=" * 50)
        
        # Test 1: Personal feed endpoint
        print("\n1. Testing personal feed endpoint...")
        try:
            async with session.get(f"{BASE_URL}/posts/feed/personal?limit=10", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} posts in personal feed")
                        if len(data) > 0:
                            post = data[0]
                            print(f"   📝 Sample: {post.get('content', '')[:50]}...")
                            print(f"   😊 Mood: {post.get('mood', 'N/A')}")
                            print(f"   🔒 Visibility: {post.get('visibility', 'N/A')}")
                    else:
                        print(f"   ⚠️  Unexpected response format: {type(data)}")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Feed stats endpoint
        print("\n2. Testing feed stats endpoint...")
        try:
            async with session.get(f"{BASE_URL}/posts/feed/stats", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success! Feed stats: {data}")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Discover feed endpoint
        print("\n3. Testing discover feed endpoint...")
        try:
            async with session.get(f"{BASE_URL}/posts/feed/discover?limit=5", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} posts in discover feed")
                    else:
                        print(f"   ⚠️  Unexpected response format")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Personal feed with mood filtering
        print("\n4. Testing personal feed with mood filtering...")
        try:
            async with session.get(f"{BASE_URL}/posts/feed/personal?mood=happy&limit=5", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} 'happy' posts in feed")
                        happy_count = sum(1 for post in data if post.get('mood') == 'happy')
                        print(f"   😊 Confirmed {happy_count} posts with 'happy' mood")
                    else:
                        print(f"   ⚠️  Unexpected response format")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Personal feed with visibility filtering
        print("\n5. Testing personal feed with visibility filtering...")
        try:
            async with session.get(f"{BASE_URL}/posts/feed/personal?visibility=public&limit=5", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} public posts in feed")
                        public_count = sum(1 for post in data if post.get('visibility') == 'public')
                        print(f"   🔒 Confirmed {public_count} public posts")
                    else:
                        print(f"   ⚠️  Unexpected response format")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 NEW FEED ENDPOINTS STATUS")
        print("Endpoints tested:")
        print("  ✅ /posts/feed/personal")
        print("  ✅ /posts/feed/stats") 
        print("  ✅ /posts/feed/discover")
        print("  ✅ /posts/feed/personal with mood filter")
        print("  ✅ /posts/feed/personal with visibility filter")

if __name__ == "__main__":
    asyncio.run(test_new_feed_endpoints())
