import asyncio
import aiohttp
import json

async def test_actual_endpoints():
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
        
        print("\n🧪 TESTING AVAILABLE POSTS ENDPOINTS")
        print("=" * 50)
        
        # Test endpoints that should exist based on the CRUD
        endpoints_to_test = [
            ("/posts", "GET", "Get all posts"),
            ("/posts/feed", "GET", "Get post feed"), 
            ("/posts/personalized", "GET", "Personalized feed"),
            ("/posts/user/me", "GET", "Get user's posts"),
            ("/posts/discover", "GET", "Discover posts"),
            ("/posts/saved", "GET", "Saved posts"),
        ]
        
        for endpoint, method, description in endpoints_to_test:
            print(f"\n📡 Testing: {description}")
            print(f"   Endpoint: {endpoint}")
            try:
                if method == "GET":
                    async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                        print(f"   Status: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            if 'posts' in data or 'items' in data:
                                count = len(data.get('posts', data.get('items', [])))
                                print(f"   ✅ Success! Found {count} items")
                            else:
                                print(f"   ✅ Success! Response: {json.dumps(data, indent=2)[:200]}...")
                        elif response.status == 404:
                            print("   ❌ Endpoint not found (404)")
                        elif response.status == 422:
                            print("   ⚠️  Validation error (might need parameters)")
                        else:
                            error = await response.text()
                            print(f"   ❌ Failed with status {response.status}: {error[:200]}")
                else:
                    print(f"   ⚠️  Method {method} not tested")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🔍 Checking what posts endpoints are available...")
        # Let's also test with parameters that might be required
        test_cases = [
            ("/posts?page=1&page_size=10", "Posts with pagination"),
            ("/posts/feed?page=1&page_size=5", "Feed with pagination"),
            ("/posts?visibility=public", "Public posts"),
            ("/posts?mood=happy", "Posts by mood"),
        ]
        
        for endpoint, description in test_cases:
            print(f"\n🔧 Testing: {description}")
            try:
                async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        count = len(data.get('posts', data.get('items', [])))
                        print(f"   ✅ Success! Found {count} items")
                    elif response.status == 404:
                        print("   ❌ Endpoint not found")
                    else:
                        error = await response.text()
                        print(f"   ❌ Failed: {error[:200]}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_actual_endpoints())
