import requests
import json

# Get auth token
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)
token = auth_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("Testing feed endpoint in detail...")

# Test the feed endpoint that's failing
response = requests.get('http://localhost:8001/api/v1/posts/feed/?content_type=video', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Let's also test without any filters
print("\nTesting without filters:")
response2 = requests.get('http://localhost:8001/api/v1/posts/feed/', headers=headers)
print(f"Status: {response2.status_code}")
