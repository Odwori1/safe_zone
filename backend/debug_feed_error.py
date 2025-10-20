import requests
import json

# Get auth token
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)
token = auth_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("Testing feed endpoint with video filter...")

# Test different feed queries to isolate the issue
endpoints = [
    '/api/v1/posts/feed/',
    '/api/v1/posts/feed/?content_type=text',
    '/api/v1/posts/feed/?content_type=audio', 
    '/api/v1/posts/feed/?content_type=video'
]

for endpoint in endpoints:
    response = requests.get(f'http://localhost:8001{endpoint}', headers=headers)
    print(f"{endpoint}: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
