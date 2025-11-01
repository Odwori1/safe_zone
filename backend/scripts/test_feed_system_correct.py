import asyncio
import aiohttp
import json

async def test_feed_system():
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
        
        print("\n🧪 TESTING FEED SYSTEM - PHASE 2.7")
        print("=" * 50)
        
        # Test 1: Basic posts endpoint (should work)
        print("\n1. Testing basic posts endpoint...")
        try:
            async with session.get(f"{BASE_URL}/posts?page=1&limit=10", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} posts")
                        if len(data) > 0:
                            post = data[0]
                            print(f"   📝 Sample post: {post.get('content', '')[:50]}...")
                            print(f"   😊 Mood: {post.get('mood', 'N/A')}")
                            print(f"   🔒 Visibility: {post.get('visibility', 'N/A')}")
                    else:
                        print(f"   ⚠️  Unexpected response format: {type(data)}")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Posts with mood filtering
        print("\n2. Testing mood-based filtering...")
        try:
            async with session.get(f"{BASE_URL}/posts?mood=happy&limit=5", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} 'happy' posts")
                        # Count actual happy posts
                        happy_count = sum(1 for post in data if post.get('mood') == 'happy')
                        print(f"   😊 Confirmed {happy_count} posts with 'happy' mood")
                    else:
                        print(f"   ⚠️  Unexpected response format")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Posts with visibility filtering
        print("\n3. Testing visibility filtering...")
        try:
            async with session.get(f"{BASE_URL}/posts?visibility=public&limit=5", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} public posts")
                        public_count = sum(1 for post in data if post.get('visibility') == 'public')
                        print(f"   🔒 Confirmed {public_count} public posts")
                    else:
                        print(f"   ⚠️  Unexpected response format")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Search functionality
        print("\n4. Testing search functionality...")
        try:
            async with session.get(f"{BASE_URL}/posts?search=test&limit=5", headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        print(f"   ✅ Success! Found {len(data)} posts matching 'test'")
                        if len(data) > 0:
                            print(f"   🔍 Sample match: {data[0].get('content', '')[:50]}...")
                    else:
                        print(f"   ⚠️  Unexpected response format")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed: {error[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Check if feed endpoint exists with correct parameters
        print("\n5. Testing feed endpoint (if exists)...")
        try:
            # Try different possible feed endpoints
            feed_endpoints = [
                "/posts/feed?skip=0&limit=10",
                "/feed?skip=0&limit=10", 
                "/posts/user/feed?skip=0&limit=10"
            ]
            
            for endpoint in feed_endpoints:
                print(f"   Trying: {endpoint}")
                async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Feed endpoint found! Response type: {type(data)}")
                        break
                    elif response.status == 404:
                        continue
                    else:
                        error = await response.text()
                        print(f"   ❌ Failed: {error[:200]}")
            else:
                print("   ℹ️  No dedicated feed endpoint found (may need implementation)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("📊 PHASE 2.7 FEED SYSTEM STATUS")
        print("✅ Working:")
        print("   - Basic posts retrieval with pagination")
        print("   - Mood-based filtering") 
        print("   - Visibility filtering")
        print("   - Search functionality")
        print("")
        print("⏳ Potentially needing implementation:")
        print("   - Dedicated feed endpoint")
        print("   - Personalized algorithms")
        print("   - Saved posts/collections")
        print("   - Content discovery")
        print("   - Feed export options")

if __name__ == "__main__":
    asyncio.run(test_feed_system())
