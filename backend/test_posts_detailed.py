import requests
import json
import uuid

def test_posts_detailed():
    # Login
    login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
    response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    print('🔍 Detailed Posts Test...')
    
    # Get current user info to see the user_id
    response = requests.get('http://localhost:8001/api/v1/profiles/me', headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ Current user: {user_info['email']} (ID: {user_info['id']})")
    else:
        print(f"❌ Cannot get user info: {response.text}")
        return False

    # Test post creation with detailed logging
    print("Testing post creation...")
    post_data = {
        'content': 'Detailed test post for debugging',
        'visibility': 'public',
        'is_anonymous': False
    }
    
    print(f"Post data: {post_data}")
    print(f"Headers: {headers}")
    
    response = requests.post('http://localhost:8001/api/v1/posts/', json=post_data, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        post_info = response.json()
        print(f"✅ Post created successfully! ID: {post_info['id']}")
        return True
    else:
        print("❌ Post creation failed")
        return False

if __name__ == "__main__":
    test_posts_detailed()
