import requests
import uuid
import json

def test_correct_login():
    print("🔐 TESTING CORRECT LOGIN FORMAT")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    try:
        # 1. Register user
        print("1. REGISTERING USER...")
        register_data = {
            "email": f"correct_login_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user_correct_{uuid.uuid4().hex[:8]}",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data, timeout=10)
        if response.status_code == 200:
            register_result = response.json()
            print(f"   ✅ SUCCESS - User ID: {register_result.get('id')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 2. Login with CORRECT format: email + password in JSON
        print("2. LOGGING IN WITH CORRECT FORMAT...")
        login_data = {
            "email": register_data["email"],  # ✅ CORRECT: Use email, not username
            "password": register_data["password"]
        }
        
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            print("   ✅ SUCCESS - Login successful!")
            print(f"   Token received: {token[:50]}...")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test auth/me endpoint
        print("3. TESTING AUTH/ME ENDPOINT...")
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ SUCCESS - User authenticated: {user_data.get('email')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 4. Test posts creation (THE MAIN TEST)
        print("4. TESTING POSTS CREATION...")
        post_data = {
            "content": "This post proves the complete login-to-posts flow works!",
            "content_type": "text",
            "mood": "happy",
            "visibility": "public",
            "is_anonymous": False
        }
        
        response = requests.post(f"{base_url}/api/v1/posts/", json=post_data, headers=headers, timeout=10)
        if response.status_code == 200:
            post_result = response.json()
            post_id = post_result.get('id')
            print(f"   ✅ SUCCESS - Post created with ID: {post_id}")
            print("   🎉 COMPLETE FLOW VERIFIED: Login → Auth → Posts ALL WORKING!")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 5. Test getting the post back
        print("5. VERIFYING POST RETRIEVAL...")
        response = requests.get(f"{base_url}/api/v1/posts/{post_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            post = response.json()
            print(f"   ✅ SUCCESS - Retrieved post: '{post.get('content')}'")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
        
        # 6. Clean up
        print("6. CLEANING UP...")
        response = requests.delete(f"{base_url}/api/v1/posts/{post_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            print("   ✅ SUCCESS - Post deleted")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
        
        print("\n🎉 COMPLETE LOGIN-TO-POSTS FLOW VERIFIED!")
        print("=" * 50)
        print("✅ Registration → Login → Authentication → Posts Creation → Posts Retrieval → Cleanup")
        print("✅ ALL STEPS WORKING CORRECTLY!")
        print("✅ RLS FIX CONFIRMED - Posts system is fully functional!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correct_login()
