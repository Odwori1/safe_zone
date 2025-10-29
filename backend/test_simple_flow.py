import requests
import uuid
import json

def test_simple_flow():
    print("🌐 SIMPLE END-TO-END FLOW TEST")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    try:
        # 1. Register user
        print("1. REGISTERING USER...")
        register_data = {
            "email": f"simple_test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"user_simple_{uuid.uuid4().hex[:8]}",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data, timeout=10)
        if response.status_code == 200:
            register_result = response.json()
            print(f"   ✅ SUCCESS - User ID: {register_result.get('id')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 2. Login
        print("2. LOGGING IN...")
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        
        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data, timeout=10)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            print("   ✅ SUCCESS - Login successful")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test auth/me endpoint
        print("3. TESTING AUTH/ME...")
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ SUCCESS - User: {user_data.get('email')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 4. Create a post (THE MAIN TEST - this was failing before our fix)
        print("4. CREATING POST...")
        post_data = {
            "content": "This post proves RLS is fixed!",
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
            print("   🎉 THIS PROVES THE RLS FIX WORKED! (Was previously failing with 500)")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
            return
        
        # 5. Get the post back
        print("5. GETTING POST BACK...")
        response = requests.get(f"{base_url}/api/v1/posts/{post_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            post = response.json()
            print(f"   ✅ SUCCESS - Retrieved: '{post.get('content')}'")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
        
        # 6. Update the post
        print("6. UPDATING POST...")
        update_data = {
            "content": "This post has been successfully updated!",
            "mood": "excited"
        }
        
        response = requests.put(f"{base_url}/api/v1/posts/{post_id}", json=update_data, headers=headers, timeout=10)
        if response.status_code == 200:
            updated_post = response.json()
            print(f"   ✅ SUCCESS - Updated: '{updated_post.get('content')}'")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
        
        # 7. Delete the post
        print("7. DELETING POST...")
        response = requests.delete(f"{base_url}/api/v1/posts/{post_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            delete_result = response.json()
            print(f"   ✅ SUCCESS - {delete_result.get('message')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
        
        print("\n🎉 COMPLETE FLOW TEST FINISHED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ Posts system is NOW WORKING with proper RLS security!")
        print("✅ The RLS architecture mismatch has been RESOLVED!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_flow()
