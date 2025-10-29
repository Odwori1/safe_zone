import asyncio
import aiohttp
import sys
import uuid
sys.path.append('.')

async def test_posts_endpoint_fixed():
    print("🌐 TESTING FIXED POSTS ENDPOINT")
    print("=" * 50)
    
    # First, let's get an auth token
    async with aiohttp.ClientSession() as session:
        # Register a test user
        register_data = {
            "email": f"test_fixed_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user_fixed_{uuid.uuid4().hex[:8]}",
            "password": "testpassword123"
        }
        
        try:
            # Register
            print("1. Registering test user...")
            async with session.post("http://localhost:8000/api/v1/auth/register", json=register_data) as resp:
                if resp.status == 200:
                    register_result = await resp.json()
                    print("   ✅ User registered successfully")
                else:
                    print(f"   ❌ Registration failed: {resp.status}")
                    return
                    
            # Login to get token
            print("2. Logging in...")
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            async with session.post("http://localhost:8000/api/v1/auth/login", data=login_data) as resp:
                if resp.status == 200:
                    login_result = await resp.json()
                    token = login_result["access_token"]
                    print("   ✅ Login successful")
                else:
                    print(f"   ❌ Login failed: {resp.status}")
                    return
            
            # Test posts endpoint with auth
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test POST posts (this was failing before)
            print("3. Testing POST /api/v1/posts/")
            post_data = {
                "content": "Test post from fixed endpoint",
                "content_type": "text",
                "mood": "neutral", 
                "visibility": "public",
                "is_anonymous": False
            }
            
            async with session.post("http://localhost:8000/api/v1/posts/", json=post_data, headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print(f"   ✅ SUCCESS - Post created with ID: {result.get('id')}")
                    post_id = result.get('id')
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
                    return
            
            # Test GET posts
            print("4. Testing GET /api/v1/posts/")
            async with session.get("http://localhost:8000/api/v1/posts/", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    posts = await resp.json()
                    print(f"   ✅ SUCCESS - {len(posts)} posts retrieved")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
            
            # Test GET specific post
            print("5. Testing GET /api/v1/posts/{post_id}")
            async with session.get(f"http://localhost:8000/api/v1/posts/{post_id}", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    post = await resp.json()
                    print(f"   ✅ SUCCESS - Post retrieved: '{post.get('content')}'")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
                    
        except Exception as e:
            print(f"Request error: {e}")

if __name__ == "__main__":
    asyncio.run(test_posts_endpoint_fixed())
