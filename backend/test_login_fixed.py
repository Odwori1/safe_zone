import requests
import uuid
import json

def test_login_fixed():
    print("🔐 TESTING LOGIN ENDPOINT PROPERLY")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    try:
        # 1. Register user
        print("1. REGISTERING USER...")
        register_data = {
            "email": f"login_test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user_login_{uuid.uuid4().hex[:8]}",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data, timeout=10)
        if response.status_code == 200:
            register_result = response.json()
            print(f"   ✅ SUCCESS - User ID: {register_result.get('id')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 2. Login with CORRECT format
        print("2. LOGGING IN (testing different formats)...")
        
        # Test format 1: JSON with username/password
        print("   Testing format 1: JSON with username/password...")
        login_data1 = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        response1 = requests.post(f"{base_url}/api/v1/auth/login", json=login_data1, timeout=10)
        print(f"      Status: {response1.status_code}")
        if response1.status_code == 200:
            print("      ✅ SUCCESS - Format 1 works!")
            token = response1.json()["access_token"]
        else:
            print(f"      ❌ FAILED: {response1.text}")
        
        # Test format 2: JSON with email/password  
        print("   Testing format 2: JSON with email/password...")
        login_data2 = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        response2 = requests.post(f"{base_url}/api/v1/auth/login", json=login_data2, timeout=10)
        print(f"      Status: {response2.status_code}")
        if response2.status_code == 200:
            print("      ✅ SUCCESS - Format 2 works!")
            token = response2.json()["access_token"]
        else:
            print(f"      ❌ FAILED: {response2.text}")
        
        # Test format 3: Form data
        print("   Testing format 3: Form data...")
        login_data3 = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        response3 = requests.post(f"{base_url}/api/v1/auth/login", data=login_data3, timeout=10)
        print(f"      Status: {response3.status_code}")
        if response3.status_code == 200:
            print("      ✅ SUCCESS - Format 3 works!")
            token = response3.json()["access_token"]
        else:
            print(f"      ❌ FAILED: {response3.text}")
        
        # If we got a token, test the posts endpoint
        if 'token' in locals():
            headers = {"Authorization": f"Bearer {token}"}
            
            print("3. TESTING POSTS WITH TOKEN...")
            post_data = {
                "content": "Test post after successful login",
                "content_type": "text",
                "mood": "happy",
                "visibility": "public", 
                "is_anonymous": False
            }
            
            response = requests.post(f"{base_url}/api/v1/posts/", json=post_data, headers=headers, timeout=10)
            if response.status_code == 200:
                post_result = response.json()
                print(f"   ✅ SUCCESS - Post created: {post_result.get('id')}")
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_fixed()
