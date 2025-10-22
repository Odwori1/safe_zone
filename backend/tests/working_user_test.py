#!/usr/bin/env python3
"""
WORKING USER TEST WITH CORRECT SCHEMA AND LOGIN
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8001"

def register_and_login():
    """Register user and then login to get token"""
    
    print("🚀 WORKING USER TEST WITH LOGIN")
    print("=" * 50)
    
    # Create unique test data
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "securepassword123"
    
    print(f"Test User: {email}")
    print(f"Username: {username}")
    
    # 1. Register user
    print("\n1. REGISTERING USER...")
    register_data = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": "Test User"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Registration Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ REGISTRATION SUCCESSFUL")
        user_data = response.json()
        print(f"User ID: {user_data.get('id')}")
    else:
        print(f"❌ Registration failed: {response.text}")
        return None
    
    # 2. Login to get access token
    print("\n2. LOGGING IN TO GET ACCESS TOKEN...")
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        login_data = response.json()
        token = login_data.get('access_token')
        if token:
            print("✅ LOGIN SUCCESSFUL")
            print(f"Access Token: {token[:20]}...")
            return token
        else:
            print("❌ No access token in response")
            print(f"Response: {login_data}")
    else:
        print(f"❌ Login failed: {response.text}")
    
    return None

def test_auth_me(token):
    """Test the /auth/me endpoint to verify token works"""
    print("\n3. TESTING AUTH/ME ENDPOINT...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers=headers
    )
    
    print(f"Auth/Me Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print("✅ AUTH/ME SUCCESSFUL")
        print(f"User: {user_data.get('email')} (ID: {user_data.get('id')})")
        return user_data
    else:
        print(f"❌ Auth/Me failed: {response.text}")
        return None

def discover_messaging_endpoints(token):
    """Try to discover any messaging-related endpoints"""
    print("\n4. DISCOVERING MESSAGING ENDPOINTS...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Common messaging endpoint patterns to try
    endpoint_patterns = [
        "/api/v1/messages",
        "/api/v1/conversations", 
        "/api/v1/chat",
        "/api/v1/messaging",
        "/api/v1/conversations/",
        "/api/v1/messages/conversations",
        "/api/v1/chat/conversations",
        "/api/v1/messaging/conversations"
    ]
    
    found_endpoints = []
    
    for endpoint in endpoint_patterns:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers
        )
        print(f"Testing {endpoint}: Status {response.status_code}")
        
        if response.status_code == 200:
            found_endpoints.append(endpoint)
            data = response.json()
            print(f"  ✅ FOUND: {len(data) if isinstance(data, list) else 'data'} items")
        elif response.status_code == 404:
            print(f"  ❌ Not found")
        else:
            print(f"  ⚠️  Other status: {response.text}")
    
    return found_endpoints

def test_manual_messaging_creation(token, user_data):
    """Test if we can manually create messaging data via API"""
    print("\n5. TESTING MANUAL MESSAGING CREATION...")
    
    # Since no messaging endpoints exist, let's check if we can access
    # the database directly through any other means
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try posts endpoint to see if basic CRUD works
    print("Testing posts endpoint (should work based on handover)...")
    response = requests.get(
        f"{BASE_URL}/api/v1/posts",
        headers=headers
    )
    
    print(f"Posts endpoint status: {response.status_code}")
    if response.status_code == 200:
        posts_data = response.json()
        print(f"✅ Posts accessible: {len(posts_data) if isinstance(posts_data, list) else 'data'} posts")
        
        # Try to create a post to test basic CRUD
        if isinstance(posts_data, list) and len(posts_data) == 0:
            print("Creating test post...")
            post_data = {
                "content": "Test post for messaging investigation",
                "privacy_level": "public"
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/posts",
                json=post_data,
                headers=headers
            )
            print(f"Post creation: {response.status_code}")
    else:
        print(f"Posts endpoint failed: {response.text}")

if __name__ == "__main__":
    # Get access token
    token = register_and_login()
    
    if token:
        # Test auth
        user_data = test_auth_me(token)
        
        if user_data:
            # Discover endpoints
            found_endpoints = discover_messaging_endpoints(token)
            
            if not found_endpoints:
                print("\n🚨 CRITICAL: No messaging endpoints found!")
                print("The real-time messaging feature may not be fully implemented in the API.")
                print("Testing basic CRUD functionality instead...")
                
                # Test basic functionality
                test_manual_messaging_creation(token, user_data)
            else:
                print(f"\n✅ Found messaging endpoints: {found_endpoints}")
    else:
        print("\n❌ Cannot proceed without valid authentication token")
