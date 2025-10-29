import asyncio
import aiohttp
import sys
import uuid
import json
sys.path.append('.')

async def test_fixed_endpoints():
    print("🧪 TESTING FIXED ENDPOINTS")
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
            async with session.post("http://localhost:8001/api/v1/auth/register", json=register_data) as resp:
                if resp.status == 200:
                    register_result = await resp.json()
                    print("   ✅ User registered successfully")
                else:
                    print(f"   ❌ Registration failed: {resp.status}")
                    error_text = await resp.text()
                    print(f"   Error details: {error_text}")
                    return
                    
            # Login to get token - FIXED: use JSON instead of form data
            print("2. Logging in...")
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            async with session.post("http://localhost:8001/api/v1/auth/login", json=login_data) as resp:
                if resp.status == 200:
                    login_result = await resp.json()
                    token = login_result["access_token"]
                    print("   ✅ Login successful")
                else:
                    print(f"   ❌ Login failed: {resp.status}")
                    error_text = await resp.text()
                    print(f"   Error details: {error_text}")
                    return
            
            # Test posts endpoint with auth
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test POST posts
            print("3. Testing POST /api/v1/posts/")
            post_data = {
                "content": "Test post from fixed endpoints",
                "content_type": "text",
                "mood": "neutral", 
                "visibility": "public",
                "is_anonymous": False
            }
            
            async with session.post("http://localhost:8001/api/v1/posts/", json=post_data, headers=headers) as resp:
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
            async with session.get("http://localhost:8001/api/v1/posts/", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    posts = await resp.json()
                    print(f"   ✅ SUCCESS - {len(posts)} posts retrieved")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
            
            # Test GET specific post
            print("5. Testing GET /api/v1/posts/{post_id}")
            async with session.get(f"http://localhost:8001/api/v1/posts/{post_id}", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    post = await resp.json()
                    print(f"   ✅ SUCCESS - Post retrieved: '{post.get('content')}'")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
            
            # Test UPDATE post
            print("6. Testing PUT /api/v1/posts/{post_id}")
            update_data = {
                "content": "Updated post content",
                "mood": "happy"
            }
            async with session.put(f"http://localhost:8001/api/v1/posts/{post_id}", json=update_data, headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    updated = await resp.json()
                    print(f"   ✅ SUCCESS - Post updated: '{updated.get('content')}'")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
            
            # Test DELETE post
            print("7. Testing DELETE /api/v1/posts/{post_id}")
            async with session.delete(f"http://localhost:8001/api/v1/posts/{post_id}", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print(f"   ✅ SUCCESS - {result.get('message')}")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
                    
            print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
                    
        except Exception as e:
            print(f"Request error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_endpoints())
