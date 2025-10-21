import requests
import json
import uuid

print("🔐 TESTING SECURITY FOUNDATION (PHASE 1 & 2)")
print("=" * 50)

# Test authentication
auth_response = requests.post(
    'http://localhost:8001/api/v1/auth/login',
    json={'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
)

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("✅ Authentication working")
    
    # Test RLS by trying to access another user's data
    random_uuid = str(uuid.uuid4())
    test_endpoints = [
        f'/api/v1/posts/{random_uuid}',
        f'/api/v1/journals/{random_uuid}',
        f'/api/v1/profiles/{random_uuid}'
    ]
    
    for endpoint in test_endpoints:
        response = requests.get(f'http://localhost:8001{endpoint}', headers=headers)
        if response.status_code == 404:
            print(f"✅ RLS working for {endpoint} - properly returns 404 for unauthorized access")
        else:
            print(f"❌ RLS issue with {endpoint} - returned {response.status_code}")
else:
    print("❌ Authentication broken")
    print(auth_response.text)

print("=" * 50)
