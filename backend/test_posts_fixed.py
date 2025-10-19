import requests
import json

def test_posts_system():
    # Login first to get token
    login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
    response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    print('📝 Testing Posts System After RLS Fix...')
    
    # Test post creation
    post_data = {
        'content': 'Test post after RLS fix',
        'visibility': 'public',
        'is_anonymous': False
    }
    response = requests.post('http://localhost:8001/api/v1/posts/', json=post_data, headers=headers)
    print(f'Create post status: {response.status_code}')
    
    if response.status_code == 200:
        print('✅ POSTS SYSTEM WORKING!')
        post_id = response.json()['id']
        print(f'Created post with ID: {post_id}')
        return True
    else:
        print(f'❌ Still failing: {response.text}')
        return False

if __name__ == "__main__":
    test_posts_system()
