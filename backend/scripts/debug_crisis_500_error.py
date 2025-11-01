import requests
import json

# Get a token first
login_data = {
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
}

login_response = requests.post("http://localhost:8001/api/v1/auth/login", json=login_data)
token = login_response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

print("🔍 Testing crisis resources endpoint for 500 error...")

# Test the exact same URL the frontend is using
url = "http://localhost:8001/api/v1/crisis-support/resources/?limit=50&page=1"
print(f"Testing URL: {url}")

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")

if response.status_code == 500:
    print("❌ Server Error 500 - Getting detailed error:")
    try:
        error_detail = response.json()
        print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
    except:
        print(f"Raw Response: {response.text}")
else:
    print(f"✅ Success: {response.status_code}")
    data = response.json()
    print(f"Resources count: {data.get('total', 0)}")
