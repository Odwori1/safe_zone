import asyncio
import aiohttp
import sys
import uuid
sys.path.append('.')

async def test_current_endpoints():
    print("🧪 TESTING CURRENT ENDPOINTS WITH FIXED CRUD")
    print("=" * 60)
    
    # First, let's get an auth token
    async with aiohttp.ClientSession() as session:
        # Register a test user
        register_data = {
            "email": f"test_current_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user_current_{uuid.uuid4().hex[:8]}",
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
                    error_text = await resp.text()
                    print(f"   Error details: {error_text}")
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
                    error_text = await resp.text()
                    print(f"   Error details: {error_text}")
                    return
            
            # Test posts endpoint with auth
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test POST posts (this was failing before)
            print("3. Testing POST /api/v1/posts/")
            post_data = {
                "content": "Test post with current endpoints",
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
                    # Don't return yet - let's test other endpoints
            
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
            
            # Test GET specific post (if we have a post_id)
            if 'post_id' in locals():
                print("5. Testing GET /api/v1/posts/{post_id}")
                async with session.get(f"http://localhost:8000/api/v1/posts/{post_id}", headers=headers) as resp:
                    print(f"   Status: {resp.status}")
                    if resp.status == 200:
                        post = await resp.json()
                        print(f"   ✅ SUCCESS - Post retrieved: '{post.get('content')}'")
                    else:
                        error = await resp.text()
                        print(f"   ❌ ERROR: {error}")
            
            # Test audio posts endpoint
            print("6. Testing GET /api/v1/posts/audio")
            async with session.get("http://localhost:8000/api/v1/posts/audio", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    audio_posts = await resp.json()
                    print(f"   ✅ SUCCESS - {len(audio_posts)} audio posts retrieved")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
            
            # Test video posts endpoint  
            print("7. Testing GET /api/v1/posts/video")
            async with session.get("http://localhost:8000/api/v1/posts/video", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    video_posts = await resp.json()
                    print(f"   ✅ SUCCESS - {len(video_posts)} video posts retrieved")
                else:
                    error = await resp.text()
                    print(f"   ❌ ERROR: {error}")
                    
        except Exception as e:
            print(f"Request error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_current_endpoints())
